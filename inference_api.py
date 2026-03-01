from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import mlflow.sklearn
import os
import pandas as pd

app = FastAPI(title="MLOps Inference API", description="Real-time Crypto Price Prediction")

# MLflow Ayarları
MLFLOW_TRACKING_URI = os.getenv("MLFLOW_TRACKING_URI", "http://mlflow_server:5000")
os.environ["MLFLOW_S3_ENDPOINT_URL"] = os.getenv("MINIO_ENDPOINT", "http://minio:9000")
os.environ["AWS_ACCESS_KEY_ID"] = os.getenv("MINIO_ROOT_USER", "admin")
os.environ["AWS_SECRET_ACCESS_KEY"] = os.getenv("MINIO_ROOT_PASSWORD", "admin12345")

mlflow.set_tracking_uri(MLFLOW_TRACKING_URI)

# Modeli RAM'de tutacağımız global değişken (Singleton Pattern)
model_cache = {}

class FeaturePayload(BaseModel):
    symbol: str
    volatility: float
    lag_1: float
    lag_3: float
    ma_5: float
    ma_10: float
    momentum: float
    volatility_change: float

def load_model(symbol: str):
    """MLflow'dan Production modelini çeker ve RAM'e yükler (Sadece 1 kere çalışır)"""
    if symbol in model_cache:
        return model_cache[symbol]
    
    model_name = f"model_{symbol}"
    try:
        print(f"🔄 MLflow'dan {model_name} (Production) indiriliyor...")
        # Doğrudan Production etiketli versiyonu indir!
        model_uri = f"models:/{model_name}/Production"
        model = mlflow.sklearn.load_model(model_uri)
        model_cache[symbol] = model
        print(f"✅ {model_name} RAM'e yüklendi!")
        return model
    except Exception as e:
        print(f"⚠️ Model bulunamadı ({symbol}): {e}")
        return None

@app.post("/predict")
async def predict_price(payload: FeaturePayload):
    """Spark'tan gelen özellikleri alır, anında tahmini döner."""
    model = load_model(payload.symbol)
    
    if not model:
        # Eğer model henüz eğitilmemişse, güvenli bir şekilde 0 veya hata dön.
        raise HTTPException(status_code=404, detail=f"{payload.symbol} için Production modeli bulunamadı. Lütfen önce modeli eğitin.")
    
    # Gelen veriyi Scikit-Learn'ün anladığı formata (DataFrame) çevir
    features_df = pd.DataFrame([{
        "volatility": payload.volatility,
        "lag_1": payload.lag_1,
        "lag_3": payload.lag_3,
        "ma_5": payload.ma_5,
        "ma_10": payload.ma_10,
        "momentum": payload.momentum,
        "volatility_change": payload.volatility_change
    }])
    
    try:
        # TAHMİNİ YAP (Milisaniyeler sürer)
        prediction = model.predict(features_df)[0]
        return {
            "symbol": payload.symbol,
            "predicted_price": round(float(prediction), 2)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Tahmin hatası: {str(e)}")

@app.get("/health")
async def health_check():
    return {"status": "ok", "loaded_models": list(model_cache.keys())}

@app.post("/reload")
async def reload_models():
    """Dışarıdan (ml_watcher) gelen tetiklemeyle RAM'deki eski modelleri temizler."""
    model_cache.clear()
    print("🔄 Cache temizlendi! Yeni istek geldiğinde modeller MLflow'dan taze olarak indirilecek.")
    return {"status": "success", "message": "Model cache cleared. Ready for fresh load."}