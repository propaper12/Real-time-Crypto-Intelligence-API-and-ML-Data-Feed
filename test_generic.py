import json
import time
import random
from kafka import KafkaProducer
from datetime import datetime

# Bu modülü, sistemin 'Schema-Agnostic' (Sema Bagimsiz) yapısını test etmek ve 
# Endüstriyel IoT (IIoT) senaryolarını simüle etmek amacıyla kurguladım. 
# Sistem sadece finansal verileri değil, karmaşık ve iç içe geçmiş (nested) 
# her türlü JSON verisini işleyebilecek esnekliktedir.

# Kafka Yapılandırması:
# Veri üretim katmanını, asenkron bir yapıda Kafka broker'ına bağlayarak 
# sistemin yüksek hacimli veri giriş (ingestion) kapasitesini simüle ediyorum.
producer = KafkaProducer(
    bootstrap_servers='kafka:9092',
    value_serializer=lambda x: json.dumps(x).encode('utf-8')
)

# Fabrika Envanteri (Static Metadata):
# Gerçekçi bir telemetri akışı sağlamak adına sabit cihaz kimlikleri ve 
# metaveriler (lokasyon, firmware versiyonu vb.) tanımladım.
DEVICES = [
    {"id": "ROBOT-ARM-01", "location": "Factory_A", "type": "Welder", "firmware": "v2.1"},
    {"id": "CONVEYOR-BELT-04", "location": "Factory_A", "type": "Motor", "firmware": "v1.0"},
    {"id": "PAINT-SPRAYER-02", "location": "Factory_B", "type": "Sprayer", "firmware": "v3.5"},
    {"id": "HVAC-MAIN-01", "location": "Roof_1", "type": "Climate", "firmware": "v1.2"},
]

print("Endüstriyel IoT simülasyonu başlatıldı. Veri akışı Kafka üzerinden yönetiliyor.")

try:
    while True:
        # Rastgele cihaz seçimi ile dinamik bir veri akışı sağlıyorum.
        device = random.choice(DEVICES)
        
        # Simülasyon Stratejisi 1: Sensör Drift (Dalgalanma)
        # Fiziksel sensörlerdeki doğal sapmaları modellemek adına baz değerler üzerine 
        # rastgele dalgalanmalar ekledim.
        base_temp = 65.0 if device['type'] == 'Welder' else 25.0
        current_temp = base_temp + random.uniform(-2.0, 2.0)

        # Simülasyon Stratejisi 2: Anomali ve Outlier Üretimi
        # Downstream (aşağı akış) sistemlerdeki 'Quality Gate' ve 'Anomaly Detection' 
        # algoritmalarını test etmek amacıyla %1 ihtimalle hatalı veri (999.9) üretiyorum.
        if random.random() < 0.01:
            current_temp = 999.9 
            status = "ERROR"
            error_code = "E-501"
        else:
            status = "OK"
            error_code = None

        # Simülasyon Stratejisi 3: Diagnostik Metrikler
        # Sadece ana ölçümleri değil, cihaz sağlığı için kritik olan batarya ve 
        # çalışma süresi (uptime) gibi diagnostik verileri de sürece dahil ettim.
        battery = round(random.uniform(10.0, 100.0), 1)

        # Karmaşık Payload Yapılandırması:
        # Veri gölünde (Data Lake) depolanacak olan veriyi hiyerarşik bir yapıda hazırladım.
        # 'data_type' etiketi ile sistemin veriyi kaynağına göre ayrıştırmasını (partitioning) sağlıyorum.
        iot_payload = {
            "device_id": device['id'],
            "factory_loc": device['location'],  
            "sensor_type": device['type'],
            "readings": {
                "temperature": round(current_temp, 2),
                "vibration": round(random.uniform(0.1, 5.0), 3),
                "rpm": random.randint(1000, 5000) if device['type'] == 'Motor' else 0
            },
            "diagnostics": {
                "battery_level": battery,
                "status": status,
                "error_code": error_code,
                "uptime_seconds": random.randint(100, 99999)
            },
            "event_time": datetime.utcnow().isoformat(),
            "data_type": "IOT" 
        }

        # Hazırlanan telemetri paketini Kafka broker'ına iletiyorum.
        producer.send('market_data', value=iot_payload)
        
        if status == "ERROR":
            print(f"Kritik hata simülasyonu: {device['id']} -> Beklenmedik değer saptandı.")
        else:
            print(f"Veri akışı sağlandı: {device['id']} | Sıcaklık: {iot_payload['readings']['temperature']}")

        # Veri frekansını saniyede 2 mesaj olacak şekilde (0.5sn) optimize ederek 
        # gerçekçi bir endüstriyel ağ trafiği simüle ediyorum.
        time.sleep(0.5)

except KeyboardInterrupt:
    print("Simülasyon kullanıcı tarafından durduruldu.")