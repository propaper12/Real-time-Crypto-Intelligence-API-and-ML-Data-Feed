import json
import time
import os
import websocket
import logging
from kafka import KafkaProducer
from datetime import datetime

# Sistem izlenebilirliğini sağlamak amacıyla logging altyapısını kurdum.
# Uygulamanın çalışma anındaki durumunu ve olası hataları bu standart üzerinden takip ediyorum.
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

KAFKA_SERVER = os.getenv('KAFKA_BOOTSTRAP_SERVERS', 'kafka:9092')
KAFKA_TOPIC = 'market_data'

def get_kafka_producer():
    """
    Kafka bağlantısını kurarken hata toleranslı (fault-tolerant) bir yapı tasarladım.
    Bağlantı kopmalarına karşı sonsuz döngü içerisinde yeniden deneme (retry) mekanizması ekledim.
    """
    while True:
        try:
            # Performans ve güvenilirlik dengesini sağlamak için özel ayarlar yapılandırdım.
            producer = KafkaProducer(
                bootstrap_servers=KAFKA_SERVER,
                value_serializer=lambda x: json.dumps(x).encode('utf-8'),
                # acks=1 seçerek hız ve güvenlik arasında optimal bir denge kurdum.
                # All yerine 1 kullanarak gecikmeyi (latency) düşürürken, leader onayı ile veri güvenliğini sağladım.
                acks=1, 
                # Geçici ağ kesintilerine karşı sistemin 5 kez yeniden denemesini sağladım.
                retries=5, 
                # Ağ trafiğini minimize etmek ve bant genişliğini verimli kullanmak için gzip sıkıştırma ekledim.
                compression_type='gzip' 
            )
            logger.info("Kafka bağlantısı başarıyla kuruldu.")
            return producer
        except Exception as e:
            logger.error(f"Kafka'ya bağlanılamadı, 5 saniye sonra tekrar denenecek: {e}")
            time.sleep(5)

# Uygulama genelinde tek bir producer instance'ı kullanmak için Singleton mantığıyla başlattım.
producer = get_kafka_producer()

def on_message(ws, message):
    """
    WebSocket üzerinden gelen ham veriyi işleyerek sistemin iç formatına normalize ediyorum.
    """
    try:
        data = json.loads(message)
        
        # Binance'den gelen ham JSON verisini, veri gölü (Lakehouse) standartlarıma uygun
        # profesyonel bir şemaya dönüştürüyorum. Bu aşama,下游 (downstream) süreçlerin 
        # (Spark/ML) veriyi kolayca işlemesini sağlar.
        processed_data = {
            'symbol': data['s'], 
            'price': float(data['p']),
            'quantity': float(data['q']),
            'timestamp': datetime.fromtimestamp(data['T'] / 1000).isoformat(),
            'event_time': datetime.utcnow().isoformat(), # Verinin sisteme giriş zamanını takip için ekledim.
            'source': 'binance_ws'
        }
        
        # İşlenen veriyi asenkron olarak Kafka topic'ine iletiyorum.
        producer.send(KAFKA_TOPIC, value=processed_data)

    except Exception as e:
        logger.error(f"Veri işleme hatası: {e}")

def on_error(ws, error):
    logger.error(f"WebSocket hatası saptandı: {error}")

def on_close(ws, close_status_code, close_msg):
    """
    Bağlantı kapandığında sistemin durmaması için otomatik yeniden bağlanma stratejisi kurguladım.
    """
    logger.warning("Baglanti kapandi. Yeniden baglanma sureci baslatiliyor.")
    time.sleep(2) 

def on_open(ws):
    logger.info("Binance WebSocket baglantisi acildi. Veri akisi basliyor.")

if __name__ == "__main__":
    # Su an icin sadece BTCUSDT trade stream'ini hedefledim.
    socket_url = "wss://stream.binance.com/ws/btcusdt@trade"

    # WebSocket baglantisinin kopmasi durumunda sonsuz dongu ile sistemi canli tutuyorum.
    while True:
        ws = websocket.WebSocketApp(
            socket_url,
            on_open=on_open,
            on_message=on_message,
            on_error=on_error,
            on_close=on_close
        )
        # Heartbeat mekanizması: ping_interval ve ping_timeout kullanarak 
        # idle durumdaki baglantilarin firewall veya router tarafindan kesilmesini onledim.
        ws.run_forever(ping_interval=70, ping_timeout=10)