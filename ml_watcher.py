import time
import subprocess
import os
import requests
from deltalake import DeltaTable

# --- AYARLAR ---
MIN_ROWS_TO_START = 20       
NORMAL_INTERVAL_SEC = 5 * 60 
DATA_PATH = "s3://market-data/silver_layer_delta"
INFERENCE_API_RELOAD_URL = "http://inference_api:8001/reload"

storage_options = {
    "AWS_ACCESS_KEY_ID": os.getenv("MINIO_ROOT_USER", "admin"),
    "AWS_SECRET_ACCESS_KEY": os.getenv("MINIO_ROOT_PASSWORD", "admin12345"),
    "AWS_ENDPOINT_URL": os.getenv("MINIO_ENDPOINT", "http://minio:9000"),
    "AWS_REGION": "us-east-1",
    "AWS_S3_ALLOW_UNSAFE_RENAME": "true",
    "AWS_ALLOW_HTTP": "true"
}

print(f"🤖 MLOps Orchestrator (Watcher) Başladı - Hedef: {MIN_ROWS_TO_START} Satır")
first_training_done = False

def get_row_count():
    try:
        dt = DeltaTable(DATA_PATH, storage_options=storage_options)
        return len(dt.to_pandas())
    except Exception:
        return 0

def run_training():
    print(f"\n🚀 EĞİTİM TETİKLENDİ Saat: {time.strftime('%H:%M:%S')}")
    try:
        # 1. Eğitimi Başlat (Pandas + Sklearn scripti)
        result = subprocess.run(["python", "train_model.py"], capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ Eğitim Başarıyla Tamamlandı, MLflow'a kaydedildi.")
            
            # 2. API'Yİ GÜNCELLE (HOT RELOAD)
            try:
                print("📡 Inference API'ye 'Modelleri Yenile' sinyali gönderiliyor...")
                resp = requests.post(INFERENCE_API_RELOAD_URL, timeout=5)
                if resp.status_code == 200:
                    print("🔄 API başarıyla güncellendi. Yeni tahminler taze modelle yapılacak!")
                else:
                    print(f"⚠️ API sinyali aldı ama hata döndü: {resp.status_code}")
            except Exception as e:
                print(f"⚠️ Inference API'ye ulaşılamadı (API kapalı olabilir): {e}")
                
            return True
        else:
            print("❌ Eğitimde Hata Oldu")
            print(result.stderr)
            return False
    except Exception as e:
        print(f"Sistem Hatası: {e}")
        return False

# --- ANA DÖNGÜ ---
while True:
    current_rows = get_row_count()
    
    if not first_training_done:
        if current_rows >= MIN_ROWS_TO_START:
            print(f"🎯 HEDEF ULAŞILDI! ({current_rows}/{MIN_ROWS_TO_START} satır). İlk eğitim başlıyor...")
            if run_training():
                first_training_done = True
                print(f"✅ İlk döngü bitti. Artık {int(NORMAL_INTERVAL_SEC/60)} dakikada bir kontrol edeceğim.")
        else:
            print(f"⏳ Veri Bekleniyor... Mevcut: {current_rows}/{MIN_ROWS_TO_START} (Kontrol: 10sn)")
            time.sleep(10) 
            
    else:
        print(f"💤 Uyku Modu ({int(NORMAL_INTERVAL_SEC/60)} dk)...")
        time.sleep(NORMAL_INTERVAL_SEC)
        
        current_rows = get_row_count()
        print(f"⏰ Vakit geldi! Veri durumu: {current_rows} satır. Yeni eğitim başlatılıyor...")
        run_training()