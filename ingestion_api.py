from fastapi import FastAPI, HTTPException, Request
from kafka import KafkaProducer
import json
import os
import time

# Bu modülü, ekosistemimize dış dünyadan (üçüncü parti şirketler veya kurum içi diğer servisler) 
# veri girişini standardize etmek amacıyla bir 'Universal Ingestion Gateway' olarak tasarladım.
app = FastAPI()

# Sistem konfigürasyonlarını ortam değişkenlerinden (Environment Variables) çekerek 
# on-premise veya cloud ortamlara kolayca adapte edilebilir (portable) bir yapı kurdum.
KAFKA_SERVER = os.getenv('KAFKA_BOOTSTRAP_SERVERS', 'kafka:9092')
KAFKA_TOPIC = 'market_data'

# Kaynak yönetimini optimize etmek amacıyla producer nesnesini global olarak tanımladım.
producer = None


def get_kafka_producer():
    """
    Kafka bağlantısını yönetmek için Singleton Pattern benzeri bir yaklaşım tercih ettim. 
    Her HTTP isteğinde yeni bir TCP bağlantısı kurmak yerine, mevcut bağlantıyı 
    tekrar kullanarak (connection pooling mantığıyla) sistem üzerindeki overhead'i minimize ettim.
    """
    global producer
    if producer is None:
        try:
            producer = KafkaProducer(
                bootstrap_servers=KAFKA_SERVER,
                value_serializer=lambda x: json.dumps(x).encode('utf-8')
            )
            print("API Gateway: Kafka bağlantısı başarılı.")
        except Exception as e:
            print(f"Kafka bağlantı hatası: {e}")
    return producer


@app.post("/api/v1/ingest")
async def ingest_data(request: Request):
    """
    Harici sistemlerin verilerini asenkron olarak iletebileceği RESTful uç noktası.
    Gelen veriler üzerinde şema doğrulaması yaparak, hatalı verilerin 
    下游 (downstream) süreçlere (Spark/Lakehouse) sızmasını engelledim.
    """
    data = await request.json()

    # Temel Veri Doğrulama (Basic Validation):
    # Analitik süreçlerin sürekliliği için kritik olan alanları kontrol ediyorum.
    required_fields = ["symbol", "price", "timestamp"]
    if not all(field in data for field in required_fields):
        raise HTTPException(
            status_code=400, 
            detail="Eksik veri formatı. 'symbol', 'price' ve 'timestamp' alanları zorunludur."
        )

    # Esneklik (Flexibility):
    # Opsiyonel alanlar için varsayılan değerler atayarak veri akışının kesilmesini önledim.
    if "quantity" not in data:
        data["quantity"] = 1.0

    try:
        # Veriyi Kafka kuyruğuna (Topic) ileterek, API katmanı ile 
        # veri işleme katmanını (Spark) birbirinden tamamen izole ettim (Decoupling).
        # Bu mimari, sistemin bir parçasında oluşacak yoğunluğun diğerlerini etkilemesini engeller.
        kafka = get_kafka_producer()
        if kafka:
            kafka.send(KAFKA_TOPIC, value=data)
            return {"status": "success", "message": "Veri başarıyla kuyruğa alındı."}
        else:
            raise HTTPException(status_code=500, detail="Kafka bağlantısı kurulamadı.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))