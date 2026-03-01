import os
import sys
import numpy as np
import pandas as pd
import mlflow
import mlflow.sklearn
import shutil
import time
from deltalake import DeltaTable
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.metrics import mean_squared_error, r2_score
from mlflow.tracking import MlflowClient

# MLflow istemcisi ve sunucusu arasındaki versiyon farklarından kaynaklanan 
# '/api/2.0/mlflow/logged-models' 404 hatasını engellemek için bu özelliği devre dışı bırakıyorum.
os.environ["MLFLOW_DISABLE_LOGGED_MODELS"] = "true"

# --- 1. KONFİGÜRASYON VE S3 BAĞLANTISI ---
MINIO_ENDPOINT = os.getenv("MINIO_ENDPOINT", "http://minio:9000")
MLFLOW_TRACKING_URI = os.getenv("MLFLOW_TRACKING_URI", "http://mlflow_server:5000")
DATA_PATH = "s3://market-data/silver_layer_delta" 

# Veri okuma performansını artırmak amacıyla Spark yerine Rust tabanlı deltalake kütüphanesini tercih ettim.
# Bu sayede JVM ayağa kaldırmadan doğrudan S3 (MinIO) üzerinden Delta tablolarını okuyabiliyorum.
storage_options = {
    "AWS_ACCESS_KEY_ID": os.getenv("MINIO_ROOT_USER", "admin"),
    "AWS_SECRET_ACCESS_KEY": os.getenv("MINIO_ROOT_PASSWORD", "admin12345"),
    "AWS_ENDPOINT_URL": MINIO_ENDPOINT,
    "AWS_REGION": "us-east-1",
    "AWS_S3_ALLOW_UNSAFE_RENAME": "true",
    "AWS_ALLOW_HTTP": "true"
}

os.environ["MLFLOW_S3_ENDPOINT_URL"] = MINIO_ENDPOINT
os.environ["AWS_ACCESS_KEY_ID"] = storage_options["AWS_ACCESS_KEY_ID"]
os.environ["AWS_SECRET_ACCESS_KEY"] = storage_options["AWS_SECRET_ACCESS_KEY"]

print("Python AutoML Engine baslatiliyor (Spark-free Architecture)...")

mlflow.set_tracking_uri(MLFLOW_TRACKING_URI)
mlflow.set_experiment("RealTime_AutoML_League")

# --- 2. FEATURE ENGINEERING (ÖZELLİK MÜHENDİSLİĞİ) ---
def create_smart_features(df):
    """
    Zaman serisi verilerinden anlamlı öznitelikler üretir. 
    Veri sızıntısını (data leakage) önlemek ve gerçek tahmini saglamak için 
    Target değişkenini bir adım ileri kaydıran (shift -1) mantığı kurguladım.
    """
    # Kronolojik sıra zaman serisi modelleri için kritiktir.
    df = df.sort_values(by="processed_time").reset_index(drop=True)
    
    # Teknik indikatör simülasyonları: Gecikmeler ve Hareketli Ortalamalar
    df['lag_1'] = df['average_price'].shift(1)
    df['lag_3'] = df['average_price'].shift(3)
    df['ma_5'] = df['average_price'].rolling(window=5).mean()
    df['ma_10'] = df['average_price'].rolling(window=10).mean()
    
    # Momentum ve volatilite değişim hızı
    df['momentum'] = df['average_price'] - df['lag_3']
    df['volatility_change'] = df['volatility'] - df['volatility'].shift(1)
    
    # Tahmin Hedefi: Modelin mevcut verilere bakarak 'gelecekteki' fiyatı öngörmesini sağlıyorum.
    df['TARGET_PRICE'] = df['average_price'].shift(-1)
    
    # Hesaplama sonrası oluşan eksik verileri (NaN) temizleyerek eğitim setini hazır hale getiriyorum.
    df = df.dropna()
    return df

# --- 3. VERİ YÜKLEME VE İŞLEME ---
try:
    print(f"Veri kaynagi taraniyor: {DATA_PATH}")
    # Rust motoru üzerinden Delta Lake dosyasını Pandas DataFrame'e dönüştürüyorum.
    dt = DeltaTable(DATA_PATH, storage_options=storage_options)
    base_df = dt.to_pandas()
    
    # Sadece yeterli veri hacmine sahip sembolleri eğitim döngüsüne alıyorum.
    symbol_counts = base_df['symbol'].value_counts()
    target_symbols = symbol_counts[symbol_counts > 20].index.tolist()
    
    if not target_symbols:
        print("Egitim için yeterli veri seti bulunamadı.")
        sys.exit(0)
        
    for symbol in target_symbols:
        print(f"Analiz süreci baslatildi: {symbol}")
        
        raw_df = base_df[base_df['symbol'] == symbol].copy()
        feature_df = create_smart_features(raw_df)
        
        feature_cols = ["volatility", "lag_1", "lag_3", "ma_5", "ma_10", "momentum", "volatility_change"]
        X = feature_df[feature_cols]
        y = feature_df["TARGET_PRICE"]
        
        # Time-Series Split: Verinin kronolojik yapısını bozmamak için rastgele değil, 
        # zamana dayalı %80 egitim ve %20 test ayrımı uyguladım.
        split_idx = int(len(feature_df) * 0.8)
        X_train, X_test = X.iloc[:split_idx], X.iloc[split_idx:]
        y_train, y_test = y.iloc[:split_idx], y.iloc[split_idx:]
        
        print(f"Veri seti durumu: {len(feature_df)} satir (Train: {len(X_train)} | Test: {len(X_test)})")
        
        # --- 4. AUTO-ML MODEL YARIŞTIRMA ---
        # En iyi performansı veren algoritmayı belirlemek için çoklu modelleme yapıyorum.
        models = {
            "RandomForest_Pro": RandomForestRegressor(n_estimators=50, max_depth=10, random_state=42),
            "GradientBoosted_X": GradientBoostingRegressor(n_estimators=50, max_depth=5, random_state=42)
        }
        
        best_rmse = float('inf')
        best_model = None
        best_model_name = ""
        
        for name, model in models.items():
            with mlflow.start_run(run_name=f"{symbol}_{name}") as run:
                print(f"Algoritma test ediliyor: {name}...", end=" ")
                
                model.fit(X_train, y_train)
                predictions = model.predict(X_test)
                
                rmse = np.sqrt(mean_squared_error(y_test, predictions))
                r2 = r2_score(y_test, predictions)
                
                print(f"RMSE Skoru: {rmse:.4f}")
                
                # Model performans metriklerini MLflow Tracking üzerine kaydediyorum.
                mlflow.log_param("symbol", symbol)
                mlflow.log_metric("rmse", rmse)
                mlflow.log_metric("r2", r2)
                
                if rmse < best_rmse:
                    best_rmse = rmse
                    best_model = model
                    best_model_name = name

        # --- 5. MODEL REGISTRY VE PRODUCTION YÖNETİMİ ---
        # MLflow sunucu uyumluluğunu saglamak icin 'Manual Artifact Bypass' stratejisini uyguladım.
        if best_model:
            print(f"Kazanan model belirlendi: {best_model_name} (RMSE: {best_rmse:.4f})")
            registered_model_name = f"model_{symbol}"
            
            with mlflow.start_run(run_name=f"{symbol}_CHAMPION") as run:
                mlflow.log_metric("final_rmse", best_rmse)
                mlflow.log_param("winner_algo", best_model_name)
                
                # Hata veren yüksek seviyeli API yerine, modeli önce yerel olarak kaydedip 
                # ardından artifact olarak yüklüyorum. Bu sayede 404 hatalarını pas geçiyorum.
                temp_path = f"/tmp/model_{symbol}"
                if os.path.exists(temp_path): shutil.rmtree(temp_path)
                
                print("Model yerel disk üzerinde paketleniyor...")
                mlflow.sklearn.save_model(sk_model=best_model, path=temp_path)
                
                print("Dosyalar MLflow sunucusuna manuel olarak yükleniyor...")
                mlflow.log_artifacts(temp_path, artifact_path="model")
                shutil.rmtree(temp_path)
                
                # Kayıtlı modeli Registry (Vitrini) üzerine bağlama süreci
                run_id = run.info.run_id
                model_uri = f"runs:/{run_id}/model"
                
                client = MlflowClient()
                try:
                    client.create_registered_model(registered_model_name)
                except: pass 

                # Yeni versiyon oluşturup modeli otomatik olarak Production aşamasına taşıyorum.
                mv = client.create_model_version(registered_model_name, model_uri, run_id)
                time.sleep(2) # Metaveri senkronizasyonu icin kısa bekleme
                
                client.transition_model_version_stage(
                    name=registered_model_name, 
                    version=mv.version,
                    stage="Production", 
                    archive_existing_versions=True
                )
            print(f"Basariyla tamamlandi: {registered_model_name} v{mv.version} artik Production'da.")

except Exception as e:
    print(f"Sistem hatasi meydana geldi: {e}")
    import traceback
    traceback.print_exc()