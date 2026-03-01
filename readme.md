<div align="center"> 
  <img src="https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white" /> 
  <img src="https://img.shields.io/badge/Apache_Spark-E25A1C?style=for-the-badge&logo=apache-spark&logoColor=white" /> 
  <img src="https://img.shields.io/badge/Apache_Kafka-231F20?style=for-the-badge&logo=apache-kafka&logoColor=white" /> 
  <img src="https://img.shields.io/badge/MinIO-C7202C?style=for-the-badge&logo=minio&logoColor=white" />
  <img src="https://img.shields.io/badge/Delta_Lake-00AEEF?style=for-the-badge&logoColor=white" />
  <img src="https://img.shields.io/badge/PostgreSQL-4169E1?style=for-the-badge&logo=postgresql&logoColor=white" /> 
  <img src="https://img.shields.io/badge/TimescaleDB-FDB515?style=for-the-badge&logo=timescaledb&logoColor=black" />
  <img src="https://img.shields.io/badge/MLflow-0194E2?style=for-the-badge&logo=mlflow&logoColor=white" />
  <img src="https://img.shields.io/badge/FastAPI-009688?style=for-the-badge&logo=fastapi&logoColor=white" />
  <img src="https://img.shields.io/badge/Streamlit-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white" />
  <img src="https://img.shields.io/badge/Metabase-509EE3?style=for-the-badge&logo=metabase&logoColor=white" />
  <img src="https://img.shields.io/badge/dbt-FF694B?style=for-the-badge&logo=dbt&logoColor=white" />
  <img src="https://img.shields.io/badge/Docker-2496ED?style=for-the-badge&logo=docker&logoColor=white" /> 
  <img src="https://img.shields.io/badge/Prometheus-E6522C?style=for-the-badge&logo=prometheus&logoColor=white" />
  <img src="https://img.shields.io/badge/Grafana-F46800?style=for-the-badge&logo=grafana&logoColor=white" />
</div>


# Enterprise Real-Time Lakehouse & MLOps Platform

**Özetle Nedir?** Bu proje; verinin üretildiği andan itibaren yakalanıp işlendiği, güvenli bir şekilde depolandığı, yapay zeka algoritmalarından geçirilerek gelecek tahminlerinin üretildiği ve tüm bu sürecin **sadece 5 saniye içerisinde** tamamlanıp ekranlara yansıtıldığı **uçtan uca (End-to-End) bir Veri Mühendisliği ve MLOps ekosistemidir.**

Geleneksel veri projelerinin aksine statik bir yapıya sahip değildir. Sistem; sürekli akan veriyi dinler, yeterli veri biriktiğinde makine öğrenmesi modellerini kendi kendine eğitir (AutoML), veri kalitesini denetler (Data Quality Gate) ve altyapı sağlığını 7/24 izler.

### 🌟 Sistemin Öne Çıkan Özellikleri:

-   **⚡ Gerçek Zamanlı Akış (Low Latency):** Verinin Binance WebSocket veya API'lerden alınıp, Spark ile işlenmesi, ML modellerinden geçirilmesi ve TimescaleDB üzerinden Streamlit dashboard'a düşmesi arasındaki toplam gecikme süresi (End-to-End Latency) ortalama 5 saniyedir.
    
-   **🧬 Şema Bağımsız (Schema Agnostic) Veri Kabulü:** Sistem "Hardcoded" (sabit şemalı) değildir. Sadece kripto para verilerini değil; **Endüstriyel IoT Sensörleri, Sunucu Logları (CPU/RAM) veya Web Trafiği** gibi her türlü JSON verisini dinamik olarak tanır, işler ve Data Lake üzerinde kaynağına göre bölümlendirerek (Partitioned) arşivler.
    
-   **🧠 Otonom Yapay Zeka (Self-Training ML):** Sistemin başında bir veri bilimcinin durmasına gerek yoktur. "ML Watcher" modülü veri havuzunun doluluğunu izler, yeterli veriye ulaşıldığında Apache Spark MLlib üzerindeki 4 farklı algoritmayı (RandomForest, ElasticNet, DecisionTree, GBT) birbirleriyle yarıştırır ve en başarılı (Şampiyon) modeli otomatik olarak canlıya alır.
    
-   **🐳 %100 İzole ve Ölçeklenebilir Mimari:** Sistem, birbirine tam entegre çalışan tam **17 farklı mikroservisten** oluşmaktadır. Tüm ortam Dockerize edilmiş olup tek bir komutla (`docker-compose up`) herhangi bir işletim sisteminde ayağa kalkabilir.
<img width="2816" height="1504" alt="Gemini_Generated_Image_hn82lvhn82lvhn82" src="https://github.com/user-attachments/assets/3e4de52a-f56d-4885-b7f2-d8e7ee86cb03" />


---

## 📂 Proje Yapısı

```text
├── dashboard_app/              # Streamlit Multi-Page Kullanıcı Arayüzü
│   ├── Home.py                 # Ana Komuta Merkezi
│   ├── utils.py                # CSS ve Veritabanı/S3 Cache Ayarları
│   ├── _Canli_Piyasa.py        # Canlı Fiyat ve İndikatör Takibi
│   ├── _Batch_Yukleme.py       # Geçmiş Veri (CSV) Upload Modülü
│   ├── _Harici_Baglanti.py     # Universal Data Gateway Arayüzü
│   ├── _MLOps_Center.py        # MLflow AutoML Liderlik Tablosu
│   ├── _Sistem_Yonetimi.py     # Enterprise Control Plane & Log İzleme
│   └── KAFDROP.py              # Kafka Universal Data Deck
├── dbt_project/                # Veri Dönüşüm Katmanı (DBT)
├── start_windows.bat           # 🚀 Windows DevOps Command Center (Otomasyon)
├── tests/                      # Birim Testleri (Unit Tests) 
│   └── test_core.py            # Çekirdek Sistem Testleri (Pytest)
├── .env                        # Çevresel Değişkenler (Şifreler & Ayarlar)
├── docker-compose.yaml         # 17+ Servisin Orkestrasyonu
├── Dockerfile.spark            # Spark, ML ve Veri İşleme İmajı
├── Dockerfile.ui               # Streamlit Dashboard İmajı
├── Dockerfile.api              # FastAPI İmajı
├── producer.py                 # Binance WebSocket Real-Time Ingestion
├── universal_producer.py       # IoT/Log/Genel Veri Simülatörü
├── ingestion_api.py            # Harici Şirketler İçin REST API (FastAPI)
├── consumer_lake.py            # Bronze Katman (Ham Veri Kaydedici - Delta)
├── process_silver.py           # Silver Katman & Canlı AI Tahmin Motoru (Spark)
├── batch_processor.py          # CSV Toplu Veri İşleme Motoru
├── train_model.py              # Spark MLlib AutoML Eğitim Fabrikası
├── ml_watcher.py               # Otonom Model Tetikleyici (Event-Driven)
├── quality_gate.py             # Veri Kalite ve Sağlık Kapısı (Data Guard)
└── prometheus.yml              # Altyapı İzleme Konfigürasyonu
```
## 🏗️ Mimari Tasarım (Architecture)
Sistem, veri mühendisliği ve MLOps standartlarına uygun olarak tasarlanmış olup, her bir Python modülü belirli bir kurumsal zorluğu (bottleneck) aşmak üzere kodlanmıştır:

#### 1. Veri Girişi ve API (Ingestion Layer)

-   **`producer.py` (Binance WebSocket Connector):**
    
    -   **Heartbeat & Resilience:** Ağ kopmalarına karşı `ws.run_forever(ping_interval=70, ping_timeout=10)` kullanılarak bağlantının canlı kalması sağlanmıştır.
        
    -   **Kafka Optimizasyonu:** Band genişliği tasarrufu için `compression_type='gzip'` kullanılmıştır. Olası broker kesintilerinde veri kaybını önlemek için `retries=5` ve hız/güvenlik dengesi için `acks=1` (Leader Acknowledgement) yapılandırması mevcuttur.
        
-   **`ingestion_api.py` (Universal API Gateway):**
    
    -   **Asenkron Mimari:** FastAPI kullanılarak `async def` uç noktaları tasarlanmış, binlerce anlık HTTP `POST` isteğini bloklamadan karşılayacak altyapı kurulmuştur.
        
    -   **Singleton Pattern:** Kafka bağlantısının her istekte yeniden açılıp sistemi yormaması için `get_kafka_producer()` fonksiyonunda Singleton tasarım deseni uygulanmıştır.
        
-   **`universal_producer.py` (Polymorphic Generator):**
    
    -   **Schema-Agnostic Veri Üretimi:** Sistem sadece kripto paraya bağımlı değildir. Borsa, IoT Sensörleri, Sunucu Metrikleri ve Web Trafiği gibi farklı veri yapılarını tek bir modül üzerinden dinamik olarak (`math.sin`, `random.uniform` ile) simüle edip Kafka'ya basar.
        

#### 2. Veri İşleme ve Storage (Processing & Lakehouse)

-   **`consumer_lake.py` (Bronze Layer / Raw Archive):**
    
    -   **Dumb Consumer Pattern:** Kafka'daki veriyi hiçbir ayrıştırma (parse) işlemine sokmadan doğrudan `string` olarak okur. Bu, şema değişikliklerinde veri kaybı riskini sıfıra indirir.
        
    -   **Backpressure (Geri Basınç) Yönetimi:** `maxOffsetsPerTrigger=1000` parametresi ile anlık veri patlamalarında (Spike) Spark motorunun çökmesi engellenmiştir.
        
-   **`process_silver.py` (Silver Layer & In-Flight AI):**
    
    -   **Sliding Window & Watermarking:** Geç gelen verilerin sistemi bozmasını engellemek için `.withWatermark("timestamp", "1 minute")` kullanılmıştır. Veriler 30 saniyelik pencerelerde `stddev_pop` fonksiyonu ile gruplanarak canlı volatilite hesaplaması yapılır.
        
    -   **In-Flight Prediction & Model Caching:** Canlı akış sırasında, MinIO'dan en son eğitilen ML modelleri `get_model_for_symbol` ile belleğe (Cache) alınır ve Spark DataFrame üzerinden `VectorAssembler` ile 7-boyutlu bir özellik vektörüne dönüştürülüp anlık fiyat tahmini yapılır.
        
    -   **Polyglot Persistence:** İşlenmiş veri, asenkron `foreachBatch` döngüsü içinde hem MinIO'ya (Analitik için Delta Lake `append` modu), hem de Streamlit paneli için **TimescaleDB**'ye (PostgreSQL Hypertable JDBC) eşzamanlı yazılır.
        
-   **`batch_processor.py` (ETL & Sanitization):**
    
    -   **Data Sanitization:** Geçmişe dönük yüklenen CSV'lerdeki hatalı ve Türkçe karakterleri, Regex (`re.sub`) tabanlı `clean_column_name` fonksiyonu ile DB formatına otonom olarak uyarlar.
        

#### 3. MLOps ve Otomasyon (AI Orchestration)

-   **`ml_watcher.py` (Event-Driven Orchestrator):**
    
    -   **Lightweight Querying:** Spark motorunu gereksiz yere ayağa kaldırmamak için doğrudan `deltalake` kütüphanesini (Rust tabanlı) kullanarak MinIO'ya bağlanır ve maliyetsiz satır sayımı (`len(dt.to_pandas())`) yapar.
        
    -   **Subprocess Management:** Belirlenen eşik (Threshold) aşıldığında `train_model.py` dosyasını alt süreç (Subprocess) olarak tetikler. "Avcı" (Hunter) ve "Devriye" (Patrol) modları ile sistem kaynaklarını tüketmeden arka planda sürekli veri durumunu denetler.
        
-   **`train_model.py` (Spark MLlib AutoML):**
    
    -   **Time-Series Split (Veri Sızıntısı Koruması):** Makine öğrenmesinde klasik Random Split kullanmak finansal verilerde sızıntıya (Data Leakage) yol açar. Bu modülde `Window.orderBy("processed_time")` ve `row_number()` fonksiyonları kullanılarak veri kronolojik olarak %80 Eğitim / %20 Test olacak şekilde profesyonelce ayrıştırılır.
        
    -   **AutoML League:** ElasticNet, DecisionTree, RandomForest ve GBTRegressor algoritmalarını paralel döngüde çalıştırıp yarıştırır. En düşük RMSE değerini alanı `best_model` seçer ve MLflow Registry'ye kaydeder.
        

#### 4. İzleme, Kalite ve DevOps (Observability & Data Quality)

-   **`quality_gate.py` (Offline Data Quality Gate):**
    
    -   Büyük veri projelerindeki _"Garbage In, Garbage Out"_ (Çöp giren çöp çıkar) riskine karşı devre kesici olarak yazılmıştır. Delta Lake'i Spark ile okuyup; sıfırın altındaki fiyatları, null (eksik) volatilite değerlerini ve bozuk zaman damgalarını tarayıp terminale/loglara CI/CD tarzı PASS/FAIL raporu basar.
        
-   **`_Sistem_Yonetimi.py` & Streamlit Stack (Control Plane):**
    
    -   **Docker SDK Integration:** `docker.from_env()` kullanılarak Python içinden doğrudan Docker soketine bağlanılır. Kullanıcı, arayüz üzerinden Spark konteynerine `exec_run` ile komut (örn: `maintenance_job.py`) gönderebilir veya konteyner loglarını canlı çekebilir.
        
    -   **Host Telemetry:** `psutil` kütüphanesi entegrasyonu ile dashboard üzerinden sunucunun anlık CPU, RAM ve Disk kullanımı izlenebilir.
        
    -   **Failover Mechanism (`utils.py`):** MLflow servisine bağlanırken önce dış DNS (`http://mlflow_server:5000`), başarısız olursa internal Docker köprüsü (`http://host.docker.internal:5000`) denenerek hata toleranslı (Fault-tolerant) bir yapı kurulmuştur.
----------

## 🛠️ Kurulum ve Çalıştırma Rehberi (DevOps Command Center)

Sistemi ayağa kaldırmak ve yönetmek için tüm mikroservis mimarisi Docker üzerinden kurgulanmıştır.

### 🪟 Windows Kullanıcıları İçin (Otomatik Kurulum)

Windows ortamında tek tıkla kurulum ve yönetim için `start_windows.bat` komuta merkezini hazırladım. Bu script:

1.  Docker WSL2 motoru için ideal RAM ve CPU optimizasyonunu (`.wslconfig` dosyasına 8GB RAM ve 4 Çekirdek yazarak) otomatik yapar.
    
2.  İnteraktif bir menü sunarak sistemi başlatma, durdurma, log okuma ve model eğitme gibi 18 farklı komutu tek tuşla yönetmenizi sağlar.
    
3.  :    start_windows.bat dosyasına çift tıklayarak baslatabılır her seyi tek yerden yönetebilrsiniz.


### 🐧 Linux / Mac ve Manuel Kullanım İçin (Kopyala & Yapıştır Komutlar)

Eğer `.bat` dosyasını kullanamıyorsanız veya terminal üzerinden tam kontrol istiyorsanız, sistemin yeteneklerini aşağıdaki komutlarla kullanabilirsiniz:

#### 🟢 1. Altyapı Kontrolü ve Sistem Döngüsü

Sistemi başlatmak, durdurmak ve izlemek için temel Docker komutları:

-   **Sistemi Başlat (Up):** Tüm 17+ servisi arka planda ayağa kaldırır.
    
    Bash
    
    ```
    docker-compose up -d
    
    ```
    
-   **Sistemi Durdur (Stop):** Veri kaybetmeden servisleri uykuya alır.
    
    Bash
    
    ```
    docker-compose stop
    
    ```
    
-   **Sistemi Sıfırla (Hard Reset):** ⚠️ DİKKAT! Tüm veritabanı, MinIO Data Lake ve Kafka kuyrukları silinir!
    
    Bash
    
    ```
    docker-compose down -v
    
    ```
    
-   **Sağlık Durumu (Health Check):** Çalışan servislerin portlarını ve durumlarını temiz bir tablo halinde listeler.
    
    Bash
    
    ```
    docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
    
    ```
    

#### 🔄 2. Hot Reload (Sistemi Kapatmadan Güncelleme)

Kodlarda bir değişiklik yaptığınızda tüm sistemi kapatmanıza gerek yoktur. Sadece ilgili servisi yeniden derleyip başlatabilirsiniz:

-   **Arayüzü (Dashboard) Güncelle:**
    
    Bash
    
    ```
    docker-compose up -d --build dashboard
    
    ```
    
-   **Yapay Zeka Motorunu (Silver Layer) Güncelle:**
    
    Bash
    
    ```
    docker-compose up -d --build spark-silver
    
    ```
    
-   **Veri Toplayıcıyı (Bronze Layer) Güncelle:**
    
    Bash
    
    ```
    docker-compose up -d --build spark-consumer
    
    ```
    

#### 🧠 3. MLOps ve Yapay Zeka (Model Eğitimi)

Sistemde yeterli veri biriktiğinde (Lakehouse dolduğunda) AI modellerini eğitmek veya otonom bırakmak için:

-   **Toplu Model Eğitimi (Tüm Coinler/Veriler İçin):** Enterprise AutoML motorunu başlatır.
    
    Bash
    
    ```
    docker exec -it spark-silver python /app/train_model.py ALL
    
    ```
    
-   **Spesifik Varlık Eğitimi:** Sadece belirli bir sembol (Örn: BTCUSDT veya Tesla) için modelleri yarıştırır.
    
    Bash
    
    ```
    docker exec -it spark-silver python /app/train_model.py BTCUSDT
    
    ```
    
-   **Otonom ML Watcher'ı Başlat:** Veri biriktikçe kendi kendine eğitim yapmasını arka planda başlatır.
    
    Bash
    
    ```
    docker exec -d spark-silver python /app/ml_watcher.py
    
    ```
    

#### 🧹 4. DataOps (Veri Yönetimi ve Temizlik)

Test süreçlerinde şişen veri havuzlarını temizlemek için:

-   **PostgreSQL (Gold Layer) Temizliği:** Dashboard üzerindeki verileri sıfırlar.
    
    Bash
    
    ```
    docker exec -it postgres psql -U admin_lakehouse -d market_db -c "TRUNCATE TABLE market_data;"
    
    ```
    
-   **MinIO Delta Lake Temizliği:** S3 Bucket üzerindeki ham ve işlenmiş Lakehouse verilerini kökten siler.
    
    Bash
    
    ```
    docker exec -it minio mc rm -r --force s3/market-data/raw_layer_delta s3/market-data/silver_layer_delta
    
    ```
    

#### 📋 5. Araçlar ve Raporlama (Monitoring)

Hata ayıklama (Debug) ve canlı kaynak izleme:

-   **Canlı Log Okuma:** Belirli bir servisin (örn: `spark-silver`, `dashboard`, `producer`) son 50 satır logunu canlı olarak ekrana basar.
    
    Bash
    
    ```
    docker logs --tail 50 -f spark-silver
    
    ```
    
-   **Canlı CPU/RAM ve Ağ İzleme (Resource Monitor):** Tüm konteynerlerin anlık kaynak tüketimlerini gösterir. Çıkmak için `CTRL + C` yapabilirsiniz.
    
    Bash
    
    ```
    docker stats
    
    ```
    

_(Not: Sistemin ilk kurulumunda `db-init` servisi PostgreSQL üzerinde gerekli `market_data` tablosunu ve TimescaleDB hypertable'ını otomatik olarak kuracaktır)._

----------

## 📊 İzleme ve Analiz Panelleri (Servisler)

Sistem ayağa kalktıktan sonra aşağıdaki linklerden tüm ekosistemi yönetebilirsiniz:

| Servis Adı | Port / Link | Açıklama |
| :--- | :--- | :--- |
| **Streamlit Dashboard** | [http://localhost:8501](http://localhost:8501) | Ana Komuta Merkezi, Canlı Piyasa, Sistem Yönetimi |
| **MLflow Registry** | [http://localhost:5000](http://localhost:5000) | Makine Öğrenmesi Model Takibi ve Versiyonlama |
| **MinIO Console** | [http://localhost:9001](http://localhost:9001) | S3 Object Storage Browser *(User: admin / Pass: admin12345)* |
| **Metabase BI** | [http://localhost:3005](http://localhost:3005) | Gelişmiş SQL Raporlama ve İş Zekası (Varsa) |
| **Grafana Monitor** | [http://localhost:3001](http://localhost:3001) | CPU, RAM, Ağ Metrikleri ve Altyapı İzleme |
| **KAFDROP / Data Deck** | [http://localhost:9010](http://localhost:9010) | Kafka Topic ve Mesaj İçeriği İzleme |
| **FastAPI Swagger** | [http://localhost:8000/docs](http://localhost:8000/docs) | API Gateway Dokümantasyonu |
| **cAdvisor** | [http://localhost:8090/containers/](http://localhost:8090/containers/) | Konteyner Performans Metrikleri |

----------

## ⚡ Eklenen Yeni "Enterprise" Özellikler

1.  **🧬 Generic Producer & Schema Agnostic Ingestion:** Eski sabit kodlu yapı terk edildi. Producer ve Kafka katmanı artık sadece taşıyıcıdır. Sistem JSON içindeki `data_type` etiketine göre veriyi tanır (Crypto, IoT, Log).
    
2.  **🗄️ Multi-Tenant Data Lake Storage:** MinIO üzerindeki Delta Lake dosyaları rastgele tutulmaz, kaynağına göre otomatik Partitioned (Bölümlenmiş) olarak saklanır (`source=binance`, vb.).
    
3.  **🛡️ Otonom Bakım (Maintenance Job):** Streamlit yönetim panelinden "Delta Lake Bakım Motoru" çalıştırılarak S3 üzerindeki küçük parçalı dosyalar birleştirilir (Optimize) ve çöpler temizlenir (Vacuum).
    

----------

## 🤝 Katkıda Bulunun (Contributing)

Bu proje bir **YBS öğrencisi** tarafından geliştirilmiş açık kaynaklı bir framework'tür. Her türlü katkıya, fikre ve PR'a açıktır.

-   **Geliştirici:** Ömer Çakan
    
-   **LinkedIn:** [Ömer Çakan](https://www.google.com/search?q=https://www.linkedin.com/in/%25C3%25B6mer-%25C3%25A7akan-819751261)
    
-   **Destek:** Proje size yardımcı olduysa depoya bir ⭐ bırakmayı unutmayın!
    

### Katılımcılara Özel Kod Talimatı

Kendi branch'inizi açın, ama `main` branch'ine dokunmayın:

Bash

```
# Projeyi indirin
git clone [https://github.com/propaper12/An-Open-Source-Real-Time-Financial-Lakehouse-Project.git](https://github.com/propaper12/An-Open-Source-Real-Time-Financial-Lakehouse-Project.git)

# Kendi adınıza yeni bir branch açın
git checkout -b dev/isminiz_ve_ozellik

# Geliştirmenizi yapın ve pushlayın
git push origin dev/isminiz_ve_ozellik

```
## 🤝 Projenin görselleri:
<img width="1530" height="654" alt="Ekran görüntüsü 2026-02-05 174921" src="https://github.com/user-attachments/assets/d5e0de38-6b3d-4caf-aff0-bcbfeb7d27c6" />
<img width="2790" height="1415" alt="Ekran görüntüsü 2026-02-05 171703" src="https://github.com/user-attachments/assets/f86b504f-9564-41b1-8b5a-86956aba1515" />
<img width="2563" height="1467" alt="Ekran görüntüsü 2026-02-05 171629" src="https://github.com/user-attachments/assets/100441f6-084d-4f43-9fef-88006e93f122" />
<img width="2560" height="1457" alt="Ekran görüntüsü 2026-02-05 171614" src="https://github.com/user-attachments/assets/e2db796b-3dcd-452e-96b8-07e9a54289c3" />
<img width="2785" height="1454" alt="Ekran görüntüsü 2026-02-05 171552" src="https://github.com/user-attachments/assets/c4658139-de33-40a2-a99d-4a7210ae44f1" />
<img width="1095" height="730" alt="Ekran görüntüsü 2026-02-05 171448" src="https://github.com/user-attachments/assets/ab8210ca-9b1c-471c-a487-fc46b80bf481" />
<img width="1081" height="1280" alt="Ekran görüntüsü 2026-02-05 171440" src="https://github.com/user-attachments/assets/1c3657d4-c6c0-404f-af50-fd1f2c28c2fc" />
<img width="2793" height="1455" alt="Ekran görüntüsü 2026-02-05 171227" src="https://github.com/user-attachments/assets/22a9d585-84bc-424f-a320-424fc3e17227" />
<img width="2772" height="1476" alt="Ekran görüntüsü 2026-02-05 170637" src="https://github.com/user-attachments/assets/6548da13-a35f-4d57-ac58-c02da3c0969e" />
