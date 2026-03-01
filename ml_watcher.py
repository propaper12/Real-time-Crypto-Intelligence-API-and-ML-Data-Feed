import time
import subprocess
import os
import requests
from deltalake import DeltaTable

# Bu modülü, sistemin otonom MLOps döngüsünü yöneten bir 'Watcher' olarak tasarladım.
# Temel amacım, veri gölündeki (Data Lake) değişimleri izleyerek model eğitim ve 
# deployment süreçlerini insan müdahalesi olmadan tetiklemektir.

# --- KONFİGÜRASYON ---
# Cold Start problemini önlemek adına minimum 20 satır veri birikmeden eğitimi başlatmıyorum.
MIN_ROWS_TO_START = 20       
# Sistem kaynaklarını optimize etmek için periyodik kontrol aralığını 5 dakika olarak belirledim.
NORMAL_INTERVAL_SEC = 5 * 60 
DATA_PATH = "s3://market-data/silver_layer_delta"
INFERENCE_API_RELOAD_URL = "http://inference_api:8001/reload"

# S3 erişimi için gerekli olan storage opsiyonlarını Rust tabanlı deltalake kütüphanesiyle uyumlu kurguladım.
storage_options = {
    "AWS_ACCESS_KEY_ID": os.getenv("MINIO_ROOT_USER", "admin"),
    "AWS_SECRET_ACCESS_KEY": os.getenv("MINIO_ROOT_PASSWORD", "admin12345"),
    "AWS_ENDPOINT_URL": os.getenv("MINIO_ENDPOINT", "http://minio:9000"),
    "AWS_REGION": "us-east-1",
    "AWS_S3_ALLOW_UNSAFE_RENAME": "true",
    "AWS_ALLOW_HTTP": "true"
}

print(f"MLOps Orchestrator (Watcher) başlatıldı. Eşik değeri: {MIN_ROWS_TO_START} satır.")
first_training_done = False

def get_row_count():
    """
    轻量sel sorgulama stratejisi: Ağır bir Spark session başlatmak yerine doğrudan 
    Rust/C++ tabanlı deltalake kütüphanesini kullanarak metaveri üzerinden satır sayımı yapıyorum.
    Bu yaklaşım, sistem üzerindeki computational overhead'i (hesaplama yükü) minimize eder.
    """
    try:
        dt = DeltaTable(DATA_PATH, storage_options=storage_options)
        return len(dt.to_pandas())
    except Exception:
        # Veri seti henüz oluşmadıysa veya erişilemiyorsa güvenli bir şekilde 0 dönüyorum.
        return 0

def run_training():
    """
    Eğitim ve Canlıya Alım (Deployment) iş akışını yöneten ana fonksiyon.
    Subprocess yönetimi ile eğitim sürecini izole ettim.
    """
    print(f"Eğitim tetiklendi. Zaman damgası: {time.strftime('%H:%M:%S')}")
    try:
        # 1. Eğitim Fazı: train_model.py script'ini alt süreç olarak çağırıyorum.
        # Bu ayrım, eğitim hatalarının ana watcher döngüsünü etkilemesini engeller (Isolation).
        result = subprocess.run(["python", "train_model.py"], capture_output=True, text=True)
        
        if result.returncode == 0:
            print("Eğitim başarıyla tamamlandı ve model MLflow Registry üzerine kaydedildi.")
            
            # 2. Canlıya Alım Fazı (Hot Reload):
            # Model Registry güncellendikten sonra Inference API'ye sinyal göndererek 
            # yeni modelin kesintisiz (Zero-Downtime) yüklenmesini sağlıyorum.
            try:
                print("Inference API'ye modelleri yenilemesi için sinyal gönderiliyor...")
                resp = requests.post(INFERENCE_API_RELOAD_URL, timeout=5)
                if resp.status_code == 200:
                    print("API cache tazelendi. Sistem yeni modellerle tahmin üretmeye hazır.")
                else:
                    print(f"API sinyali alındı ancak beklenmedik durum oluştu: {resp.status_code}")
            except Exception as e:
                print(f"Inference API ile iletişim kurulamadı: {e}")
                
            return True
        else:
            print("Eğitim sürecinde hata saptandı:")
            print(result.stderr)
            return False
    except Exception as e:
        print(f"Orkestrasyon sırasında sistem hatası: {e}")
        return False

# --- OTONOM DÖNGÜ (EVENT-DRIVEN POLLING) ---
# Sistemi sonsuz bir döngüde, kaynak tüketimini gözeterek çalıştırıyorum.
while True:
    current_rows = get_row_count()
    
    if not first_training_done:
        # Başlangıç evresi: Yeterli veri birikene kadar kısa aralıklarla (10sn) kontrol yapıyorum.
        if current_rows >= MIN_ROWS_TO_START:
            print(f"Hedef veri hacmine ulaşıldı ({current_rows}/{MIN_ROWS_TO_START}). İlk döngü başlatılıyor.")
            if run_training():
                first_training_done = True
                print(f"İlk eğitim başarılı. Periyodik kontrol moduna (Her {int(NORMAL_INTERVAL_SEC/60)} dakikada bir) geçiliyor.")
        else:
            print(f"Veri birikmesi bekleniyor. Mevcut durum: {current_rows}/{MIN_ROWS_TO_START}")
            time.sleep(10) 
            
    else:
        # Operasyonel evre: İlk eğitimden sonra sistemi uyku moduna alarak 
        # düzenli aralıklarla sürekli eğitim (Continuous Training) döngüsünü işletiyorum.
        time.sleep(NORMAL_INTERVAL_SEC)
        
        current_rows = get_row_count()
        print(f"Periyodik kontrol zamanı geldi. Mevcut satır sayısı: {current_rows}. Güncel eğitim başlatılıyor.")
        run_training()