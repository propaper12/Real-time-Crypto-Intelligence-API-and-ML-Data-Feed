from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import mlflow.sklearn
import os
import pandas as pd

# Projenin servis katmanını FastAPI ile kurguladım. 
# Asenkron yapısı ve otomatik Swagger dökümantasyonu sayesinde 
# Spark ile ML modelleri arasında düşük gecikmeli bir köprü kurmayı hedefledim.
app = FastAPI(title="MLOps Inference API", description="Real-time Crypto Price Prediction Service")

# MLflow ve S3 (MinIO) bağlantı konfigürasyonlarını ortam değişkenlerinden alacak şekilde yapılandırdım.
# Model artifact'lerine güvenli erişim için gerekli olan S3 endpoint ve kimlik bilgilerini buraya tanımladım.
MLFLOW_TRACKING_URI = os.getenv("MLFLOW_TRACKING_URI", "http://mlflow_server:5000")
os.environ["MLFLOW_S3_ENDPOINT_URL"] = os.getenv("MINIO_ENDPOINT", "http://minio:9000")
os.environ["AWS_ACCESS_KEY_ID"] = os.getenv("MINIO_ROOT_USER", "admin")
os.environ["AWS_SECRET_ACCESS_KEY"] = os.getenv("MINIO_ROOT_PASSWORD", "admin12345")

mlflow.set_tracking_uri(MLFLOW_TRACKING_URI)

# Kaynak yönetimini optimize etmek amacıyla Singleton Pattern benzeri bir yapı kullandım.
# Modelleri her tahminde diskten okumak yerine bir kez RAM'e yüklüyorum (In-Memory Caching).
# Bu sayede inference (çıkarım) süresini milisaniyeler mertebesine indirdim.
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
    """
    MLflow Model Registry üzerinden 'Production' etiketine sahip en güncel modeli çeker.
    Model zaten RAM'de mevcutsa doğrudan cache üzerinden döner, değilse indirir.
    """
    if symbol in model_cache:
        return model_cache[symbol]
    
    model_name = f"model_{symbol}"
    try:
        print(f"MLflow'dan {model_name} (Production) indiriliyor...")
        # Model Governance stratejisi gereği sadece Production aşamasındaki modelleri kabul ediyorum.
        model_uri = f"models:/{model_name}/Production"
        model = mlflow.sklearn.load_model(model_uri)
        model_cache[symbol] = model
        print(f"Model başarıyla RAM'e yüklendi: {model_name}")
        return model
    except Exception as e:
        print(f"Model yükleme hatası ({symbol}): {e}")
        return None

@app.post("/predict")
async def predict_price(payload: FeaturePayload):
    """
    Spark Structured Streaming'den gelen özellikleri işleyerek anlık fiyat tahmini üretir.
    Veriyi Scikit-Learn modellerinin beklediği DataFrame formatına dönüştürerek modele iletir.
    """
    model = load_model(payload.symbol)
    
    if not model:
        # Modelin henüz mevcut olmadığı durumlarda sistemin çökmemesi için kontrollü bir hata dönüyorum.
        raise HTTPException(
            status_code=404, 
            detail=f"{payload.symbol} için Production modeli bulunamadı. Eğitim sürecini kontrol edin."
        )
    
    # Spark'tan gelen ham payload verisini Pandas DataFrame yapısına cast ediyorum.
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
        # Prediction süreci tamamen izole edilmiş bir servis üzerinden yürütülür.
        prediction = model.predict(features_df)[0]
        return {
            "symbol": payload.symbol,
            "predicted_price": round(float(prediction), 2)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Tahmin işlemi sırasında hata oluştu: {str(e)}")

@app.get("/health")
async def health_check():
    """Sistemin sağlık durumunu ve o an RAM'de yüklü olan aktif modelleri izlemek için kullandığım endpoint."""
    return {"status": "ok", "loaded_models": list(model_cache.keys())}

@app.post("/reload")
async def reload_models():
    """
    Zero-Downtime Deployment stratejimin en kritik parçası.
    Yeni bir model eğitildiğinde, ml_watcher bu endpoint'i tetikler.
    API'yi kapatıp açmadan RAM'deki cache temizlenir ve modeller bir sonraki istekte taze olarak yüklenir.
    """
    model_cache.clear()
    print("Model cache temizlendi. Yeni modeller MLflow üzerinden taze olarak yüklenecek.")
    return {"status": "success", "message": "Model cache cleared. Ready for fresh load."}
