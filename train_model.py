import os
#MLflow'un o sorun çıkaran yeni metadata özelliğini kapatır.
os.environ["MLFLOW_DISABLE_LOGGED_MODELS"] = "true"
import sys
from time import time
import numpy as np
import pandas as pd
import mlflow
import mlflow.sklearn
from deltalake import DeltaTable
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.metrics import mean_squared_error, r2_score
from mlflow.tracking import MlflowClient



# --- 1. AYARLAR VE KİMLİK BİLGİLERİ ---
MINIO_ENDPOINT = os.getenv("MINIO_ENDPOINT", "http://minio:9000")
MLFLOW_TRACKING_URI = os.getenv("MLFLOW_TRACKING_URI", "http://mlflow_server:5000")
DATA_PATH = "s3://market-data/silver_layer_delta" # s3a değil, s3 kullanıyoruz (Rust tabanlı deltalake için)

# Deltalake (Rust) kütüphanesi için MinIO bağlantı ayarları
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

print("🚀 Enterprise Python AutoML Engine Başlatılıyor (No Spark, No JVM)...")

mlflow.set_tracking_uri(MLFLOW_TRACKING_URI)
mlflow.set_experiment("RealTime_AutoML_League")

# --- 2. ÖZELLİK MÜHENDİSLİĞİ (PANDAS İLE IŞIK HIZINDA) ---
def create_smart_features(df):
    """
    Pandas kullanarak zaman serisi özelliklerini (Features) üretir.
    En Önemlisi: Hedef değişkeni (Target) 1 adım İLERİ kaydırır (Shift -1).
    """
    # Veriyi zaman damgasına göre kesinlikle sıralamalıyız
    df = df.sort_values(by="processed_time").reset_index(drop=True)
    
    # Gecikmeler (Lags)
    df['lag_1'] = df['average_price'].shift(1)
    df['lag_3'] = df['average_price'].shift(3)
    
    # Hareketli Ortalamalar (Moving Averages)
    df['ma_5'] = df['average_price'].rolling(window=5).mean()
    df['ma_10'] = df['average_price'].rolling(window=10).mean()
    
    # Momentum ve Volatilite Değişimi
    df['momentum'] = df['average_price'] - df['lag_3']
    df['volatility_change'] = df['volatility'] - df['volatility'].shift(1)
    
    # 🎯 SENIOR DOKUNUŞU: GELECEĞİ TAHMİN ETMEK (TARGET)
    # Modelin 'şu an'ki verilere bakarak 'bir sonraki' fiyatı bulmasını istiyoruz.
    df['TARGET_PRICE'] = df['average_price'].shift(-1)
    
    # NaN değerleri temizle (Shift ve Rolling işlemlerinden dolayı oluşur)
    df = df.dropna()
    return df

# --- 3. VERİ YÜKLEME VE EĞİTİM ---
try:
    print(f"📂 Veri Havuzu Taranıyor: {DATA_PATH}")
    # Spark ayağa kaldırmadan, Rust gücüyle Delta Lake okuma (Çok Hızlı)
    dt = DeltaTable(DATA_PATH, storage_options=storage_options)
    base_df = dt.to_pandas()
    
    # Hedef semboller (Sadece verisi 20'den büyük olanlar)
    symbol_counts = base_df['symbol'].value_counts()
    target_symbols = symbol_counts[symbol_counts > 20].index.tolist()
    
    if not target_symbols:
        print("⚠️ İşlenecek uygun sembol bulunamadı. Veri akışını bekleyin.")
        sys.exit(0)
        
    for symbol in target_symbols:
        print(f"\n📊 ANALİZ BAŞLIYOR: {symbol}")
        
        # Filtrele ve Özellikleri Çıkar
        raw_df = base_df[base_df['symbol'] == symbol].copy()
        feature_df = create_smart_features(raw_df)
        
        # Modelin eğitileceği kolonlar (Features)
        feature_cols = ["volatility", "lag_1", "lag_3", "ma_5", "ma_10", "momentum", "volatility_change"]
        
        X = feature_df[feature_cols]
        y = feature_df["TARGET_PRICE"]
        
        # Zaman Serisi Ayrımı (Time-Series Split: %80 Train, %20 Test)
        split_idx = int(len(feature_df) * 0.8)
        X_train, X_test = X.iloc[:split_idx], X.iloc[split_idx:]
        y_train, y_test = y.iloc[:split_idx], y.iloc[split_idx:]
        
        print(f"   Veri Seti: {len(feature_df)} satır (Train: {len(X_train)} | Test: {len(X_test)})")
        
        # --- 4. AUTO-ML LİGİ (SCIKIT-LEARN) ---
        models = {
            "RandomForest_Pro": RandomForestRegressor(n_estimators=50, max_depth=10, random_state=42),
            "GradientBoosted_X": GradientBoostingRegressor(n_estimators=50, max_depth=5, random_state=42)
        }
        
        best_rmse = float('inf')
        best_model = None
        best_model_name = ""
        
        for name, model in models.items():
            with mlflow.start_run(run_name=f"{symbol}_{name}") as run:
                print(f"   ⚔️ Dövüşüyor: {name}...", end=" ")
                
                # Eğit
                model.fit(X_train, y_train)
                
                # Tahmin ve Başarı Ölçümü
                predictions = model.predict(X_test)
                rmse = np.sqrt(mean_squared_error(y_test, predictions))
                r2 = r2_score(y_test, predictions)
                
                print(f"-> Skor (RMSE): {rmse:.4f}")
                
                # MLflow'a Logla
                mlflow.log_param("symbol", symbol)
                mlflow.log_metric("rmse", rmse)
                mlflow.log_metric("r2", r2)
                
                if rmse < best_rmse:
                    best_rmse = rmse
                    best_model = model
                    best_model_name = name
                    best_run_id = run.info.run_id

        # --- 5. ŞAMPİYONU REGISTRY'YE KAYDET (ULTRA-STABİL BYPASS YÖNTEMİ) ---
        if best_model:
            print(f"   🏆 KAZANAN: {best_model_name} (Hata: {best_rmse:.4f})")
            registered_model_name = f"model_{symbol}"
            
            with mlflow.start_run(run_name=f"{symbol}_CHAMPION") as run:
                mlflow.log_metric("final_rmse", best_rmse)
                mlflow.log_param("winner_algo", best_model_name)
                
                # 🚀 BYPASS STRATEJİSİ: log_model yerine save_model + log_artifacts kullanıyoruz
                import shutil
                temp_path = f"/tmp/model_{symbol}"
                if os.path.exists(temp_path): shutil.rmtree(temp_path)
                
                print("   📦 Model yerel olarak paketleniyor...")
                mlflow.sklearn.save_model(sk_model=best_model, path=temp_path)
                
                print("   📂 Dosyalar MLflow'a yükleniyor (Artifact Upload)...")
                # Bu aşama 404 hatası veren '/logged-models' endpoint'ini ASLA çağırmaz
                mlflow.log_artifacts(temp_path, artifact_path="model")
                shutil.rmtree(temp_path) # Temizlik
                
                # 2. Modeli Registry'ye manuel bağla
                run_id = run.info.run_id
                model_uri = f"runs:/{run_id}/model"
                
                print(f"   🚀 Registry Kaydı: {registered_model_name}")
                client = mlflow.tracking.MlflowClient()
                try:
                    client.create_registered_model(registered_model_name)
                except: pass 

                mv = client.create_model_version(registered_model_name, model_uri, run_id)
                
                # 3. Production etiketini bas
                import time
                time.sleep(2)
                client.transition_model_version_stage(
                    name=registered_model_name, version=mv.version,
                    stage="Production", archive_existing_versions=True
                )
            print(f"   ✅ ZAFER: {registered_model_name} v{mv.version} artık Production'da!")

except Exception as e:
    print(f"❌ KRİTİK SİSTEM HATASI: {e}")
    import traceback
    traceback.print_exc()