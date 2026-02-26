import json
import time
import os
import websocket
import logging
from kafka import KafkaProducer
from datetime import datetime

# LOG AYARLARI 
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

KAFKA_SERVER = os.getenv('KAFKA_BOOTSTRAP_SERVERS', 'kafka:9092')
KAFKA_TOPIC = 'market_data'

# KAFKA PRODUCER 
def get_kafka_producer():
    while True:
        try:
            producer = KafkaProducer(
                bootstrap_servers=KAFKA_SERVER,
                value_serializer=lambda x: json.dumps(x).encode('utf-8'),
                # Performans Ayarları
                 # 1 onay yeterli (hız için) ama iki tane daha ozelliği vardır 0 ve all 
                #0= Producer veriyi yollar ve cevabı beklemez. Kafka "Aldım" dese de demese de sonraki veriyi yollar.
                #all=Producer veriyi yollar; hem LEADER, hem de tüm FOLLOWERlar  veriyi diske yazana kadar bekler.
                acks=1, 
                retries=5, # Başarısız olursa 5 kez dene
                compression_type='gzip' # Band genişliği tasarrufu
            )
            logger.info(" Kafka bağlantısı başarıyla kuruldu.")
            return producer
        except Exception as e:
            logger.error(f" Kafka'ya bağlanılamadı, 5 saniye sonra tekrar dene: {e}")
            time.sleep(5)

producer = get_kafka_producer()

def on_message(ws, message):
    try:
        data = json.loads(message)
        
        # Veriyi profesyonel bir formata sokuyoruz
        processed_data = {
            'symbol': data['s'], # Binance'den gelen sembol (örn: BTCUSDT)
            'price': float(data['p']),
            'quantity': float(data['q']),
            'timestamp': datetime.fromtimestamp(data['T'] / 1000).isoformat(),
            'event_time': datetime.utcnow().isoformat(), # Verinin sisteme giriş saati
            'source': 'binance_ws'
        }
        
        # Kafka'ya fırlat
        producer.send(KAFKA_TOPIC, value=processed_data)
        # logger.info(f" Veri Gönderildi: {processed_data['symbol']} -> {processed_data['price']}")

    except Exception as e:
        logger.error(f" Veri işleme hatası: {e}")

def on_error(ws, error):
    logger.error(f" WebSocket Hatası: {error}")

def on_close(ws, close_status_code, close_msg):
    logger.warning("🔌 Bağlantı Kapandı. Yeniden bağlanılıyor...")
    time.sleep(2) # Hemen bağlanıp spam yapmasın

def on_open(ws):
    logger.info(" Binance WebSocket Bağlantısı Açıldı - Akış Başlıyor...")

if __name__ == "__main__":
    # Sadece BTCUSDT
    socket_url = "wss://stream.binance.com/ws/btcusdt@trade"

    while True:
        ws = websocket.WebSocketApp(
            socket_url,

            on_open=on_open,
            on_message=on_message,
            on_error=on_error,
            on_close=on_close
        )
        # ping_interval ve ping_timeout ile bağlantının canlı kalmasını sağlıyoruz
        ws.run_forever(ping_interval=70, ping_timeout=10)
