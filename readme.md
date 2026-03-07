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


## 📖 Proje Özeti ve Vizyonu

**RadarPro**, günümüz finans teknolojilerindeki en büyük darboğazlar olan "yüksek veri gecikmesi" ve "model performans kayıpları" sorunlarını çözmek üzere tasarlanmış uçtan uca (End-to-End) bir **Veri Mühendisliği ve MLOps ekosistemidir.** Bu platform; verinin ham haliyle üretiminden itibaren milisaniyeler içinde yakalanmasını, kurumsal standartlarda (Medallion Architecture) işlenmesini ve otonom yapay zeka modelleriyle bir sonraki periyodun tahmin edilmesini sağlar.

Sistemin temel vizyonu; sadece bir "trading dashboard" sunmak değil, **kendi kendine öğrenen ve iyileşen (Self-Healing & Self-Learning)** bir veri ambarı altyapısı kurmaktır. Geleneksel "Batch" işlemeye dayalı yapıların aksine RadarPro, verinin oluşumu ile terminale yansıması arasındaki süreyi **5 saniyenin altına indirerek** gerçek zamanlı analitiği kurumsal bir standart haline getirir.

----------

### 🌟 Mühendislik ve Tasarımın Temel Direkleri

#### ⚡ 1. Ultra-Düşük Gecikmeli Veri Akış Hattı (Low Latency Ingestion)

Sistem, Binance WebSocket katmanından 25 farklı kripto varlığın canlı "Trade" verisini asenkron olarak tüketir. Apache Kafka, bu verileri yüksek sıkıştırma oranları (`gzip`) ve lider onayı (`acks=1`) stratejisiyle brokerlarına dağıtır. Bu yapı, saniyede binlerce işlemin kayıpsız ve milisaniyelik gecikmelerle işleme katmanına iletilmesini garanti eder.

#### 🚀 2. Model-as-a-Service (MaaS) ve RAM Optimizasyonu

Finansal veri işlemede en büyük maliyet kalemi olan RAM tüketimi, akıllı bir mikroservis ayrımıyla çözülmüştür. Spark Streaming motoru üzerindeki ağır makine öğrenmesi (inference) yükü sökülerek, hafif bir **FastAPI çıkarım motoruna (`inference_api.py`)** devredilmiştir. Bu MaaS (Model-as-a-Service) yaklaşımı sayesinde, sistemin toplam RAM ihtiyacı **15 GB seviyesinden 6 GB'a düşürülerek %60 operasyonel verimlilik** elde edilmiştir.

#### 🧠 3. Bilimsel Tahminleme ve Veri Sızıntısı (Data Leakage) Koruması

Akademik başarı için sistem, finansal modellerin kronik sorunu olan "geleceği geçmişe karıştırma" (Data Leakage) hatasını matematiksel olarak engeller. Model eğitimi sırasında **zamansal kaydırma (`shift(-1)`)** tekniği kullanılarak, algoritmaların o anki fiyatı değil, tam olarak **bir sonraki periyodun (geleceğin)** fiyatını tahmin etmesi sağlanmıştır.

#### 🔄 4. Otonom CD Döngüsü ve Sıfır Kesinti (Zero-Downtime Hot Reload)

Platform, başında bir operatör beklemeden 7/24 otonom çalışacak şekilde kurgulanmıştır. **ML Watcher** modülü, Delta Lake (MinIO) üzerindeki veri hacmini sürekli tarar; yeterli eşiğe (`MIN_ROWS_TO_START`) ulaşıldığında eğitimi tetikler. Yeni model MLflow'da tescillendikten sonra, canlıdaki API'ye `/reload` sinyali gönderilerek eski model RAM'den temizlenir ve sistem duraksamadan güncel modele geçer.

#### 🛡️ 5. Kurumsal Güvenlik, Hız Sınırı ve Veri Kalitesi

Sistem, hem VIP hem de FREE kullanıcılar için optimize edilmiş bir **API Gateway** mimarisine sahiptir. VIP kullanıcılar milisaniyelik Kafka akışlarına WebSocket üzerinden erişebilirken, sistem **Rate Limiting** motoru ile suistimalleri engeller. Ayrıca, **Data Quality Gate** modülü ile bozuk verilerin modellere sızması engellenerek tahmin doğruluğu "saf veri" (clean data) üzerinden korunur.

#### 🖥️ 6. Hibrit Terminal Deneyimi (Web, Mobile & Desktop)

Kullanıcı arayüzü sadece bir web sitesi değil, bir ekosistemdir. **Streamlit** ile kurumsal yönetim paneli ve altyapı izleme süreçleri yönetilirken, **Electron** tabanlı masaüstü uygulaması profesyonel trader'lar için düşük gecikmeli bir masaüstü deneyimi sunar. 
Pro Terminal, HFT (High Frequency Trading) verilerini milisaniyelik hassasiyetle görselleştirir.
<img width="2816" height="1536" alt="Architecture" src="https://github.com/user-attachments/assets/0d3cabf3-f35d-4d77-ad85-a01477a16265" />

---

## 📂 Proje Yapısı (Core Backend & Infrastructure)

RadarPro ekosistemi, **Separation of Concerns (Sorumlulukların Ayrılması)** prensibine uygun olarak modüler bir klasör yapısına sahiptir. Her bir bileşen, sistemin bütününe hizmet eden bağımsız bir mikroservis veya yardımcı araçtır.

Plaintext

```
├── dashboard_app/              # 🎛️ System Control Plane (Streamlit UI)
│   ├── Home.py                  # Platform Ana Giriş ve Altyapı Telemetrisi
│   ├── utils.py                 # CSS Enjeksiyonu, S3 Cache ve Failover Bağlantıları
│   ├── _Canli_Piyasa.py         # Real-Time Kafka Akışı ve Teknik Analiz Görselleştirme
│   ├── Gecmis_Analiz.py         # Delta Lake Arşivi Üzerinden Batch Analiz ve Korelasyon
│   ├── _MLOps_Center.py         # MLflow Model Registry ve AutoML Liderlik Tablosu
│   ├── _Harici_Baglanti.py      # Universal Data Gateway Yönetim Arayüzü
│   ├── _Sistem_Yonetimi.py      # Docker Konteyner Kontrolü ve Veri Bakımı (Optimize/Vacuum)
│   └── KAFDROP.py               # Kafka Universal Data Deck ve Mesaj İzleme
│
├── tests/                      # 🧪 Kalite Güvence ve Test Katmanı
│   ├── test_core.py             # Çekirdek Sistem Fonksiyonlarının Birim Testleri
│   └── test_generic.py          # Schema-Agnostic Veri Girişi ve IoT Simülasyon Testleri
│
├── ingestion_layer/            # 📡 Veri Giriş ve Güvenlik Servisleri
│   ├── producer.py              # Binance WebSocket - High-Frequency Ingestion Motoru
│   ├── universal_producer.py    # Schema-Agnostic / IoT / Log Veri Simülatörü
│   ├── ingestion_api.py         # Enterprise API Gateway (VIP/FREE Auth & Rate Limiting)
│   ├── api_key_manager.py       # API Key Lifecycle (Üretim ve Doğrulama) Yönetimi
│   ├── bulk_keygen.py           # Toplu VIP Müşteri ve API Key Provisioning Aracı
│   └── fake_company.py          # B2B Şirket Verisi Simülasyonu (REST API Client)
│
├── processing_layer/           # ⚙️ Veri İşleme ve Lakehouse Mimari
│   ├── consumer_lake.py         # Bronze Layer (Raw Archive) Spark Streaming Tüketicisi
│   ├── process_silver.py        # Silver Layer (Feature Engineering) & MaaS Entegrasyonu
│   ├── batch_processor.py       # Geçmişe Dönük CSV ETL ve Data Sanitization Motoru
│   ├── batch_user_processor.py  # Kullanıcı Bazlı Analitik Veri İşleme Servisi
│   └── batch_yfinance_etl.py    # yFinance Bridge - 10 Yıllık Tarihsel Veri Aktarıcı
│
├── mlops_layer/                # 🧠 Yapay Zeka ve Otonom MLOps Döngüsü
│   ├── inference_api.py         # FastAPI MaaS Engine (Milisaniyelik AI Tahmin Servisi)
│   ├── train_model.py           # Scikit-Learn + XGBoost + LightGBM AutoML Fabrikası
│   ├── ml_watcher.py            # Otonom Continuous Training (CT) ve Hot-Reload Orkestratörü
│   └── quality_gate.py          # Data Quality Gate (Model Öncesi Veri Güvenlik Kapısı)
│
├── devops_config/              # 🐳 Konteyner Orkestrasyonu ve İzleme
│   ├── docker-compose.yaml      # 17+ Mikroservisin Global Orkestrasyon Dosyası
│   ├── Dockerfile.spark         # Apache Spark & Delta Lake Optimize Edilmiş İmaj
│   ├── Dockerfile.api           # FastAPI & Ingestion Gateway İmajı
│   ├── Dockerfile.ui            # Streamlit Dashboard & System Plane İmajı
│   ├── .env                     # Global Şifreleme ve Çevresel Değişkenler (Şablon)
│   ├── prometheus.yml           # Altyapı Metrik Toplama Yapılandırması
│   ├── start_windows.bat        # Windows DevOps Command Center (Otomasyon Scripti)
│   └── start_unix.sh            # Unix/Mac Kararlı Dağıtım ve Yönetim Scripti
└── readme.md                   # Proje Teknik Dokümantasyonu (Ana Rehber)

```

----------

> **💡 Mühendislik Notu:** Bu yapı, **Medallion Architecture** prensiplerine göre kurgulanmış olup; verinin ham haliyle girdiği (Ingestion), işlendiği (Processing) ve zekaya dönüştüğü (MLOps) katmanlar birbirinden fiziksel ve mantıksal olarak tamamen izole edilmiştir.



## 🏗️ Mimari Tasarım (Architecture)

RadarPro ekosistemi, **Veri Mühendisliği (Data Engineering)** ve **MLOps** prensiplerine tam uyumlu olarak tasarlanmıştır. Her Python modülü, kurumsal ölçekli veri platformlarında karşılaşılan spesifik darboğazları (bottlenecks) aşmak üzere özelleştirilmiş bir göreve sahiptir:

### 1. Veri Kaynağı ve İletişim Katmanı (Ingestion & Pub/Sub Layer)

-   **`producer.py` (Binance WebSocket Connector):**
    
    -   **Heartbeat & Resilience:** Ağ kopmalarına karşı `ws.run_forever(ping_interval=70, ping_timeout=10)` mekanizmasıyla kesintisiz bir bağlantı hattı kurar.
        
    -   **High-Volume Streaming:** Binance üzerinden 25 farklı varlığın canlı trade verisini asenkron olarak toplar ve `gzip` sıkıştırma ile Kafka brokerlarına iletir.
        
-   **`universal_producer.py` (Schema-Agnostic Engine):**
    
    -   **Universal Ingestion:** Projenin sadece finans odaklı olmadığını kanıtlayan modüldür. IoT sensörleri, log verileri ve web trafik verilerini sistemin anlayabileceği ortak bir şemaya (`Generic_Data`) normalize eder.
        
    -   **Dynamic Source Simulation:** Farklı frekanslarda veri üreten kaynakları taklit ederek sistemin yük kapasitesini test eder.
        
-   **`fake_company.py` (B2B Data Simulation):**
    
    -   **Tenant Simulation:** Harici bir şirketin (Örn: Tesla Factory) veri üretim hattını simüle eder ve veriyi WebSocket yerine doğrudan **Ingestion API** üzerinden sisteme enjekte eder.
        

### 2. Güvenlik ve API Geçit Katmanı (Security & Gateway Layer)

-   **`ingestion_api.py` (Enterprise Data Gateway):**
    
    -   **Freemium/VIP Logic:** Kullanıcıların API anahtarlarını kontrol ederek, yetkilerine göre (FREE/VIP) farklı veri akış hızları ve içerikleri sunar.
        
    -   **Rate Limiting & Pub/Sub:** Gelen istekleri denetler ve VIP kullanıcılara özel düşük gecikmeli **Kafka WebSocket Stream** bağlantıları sağlar.
        
-   **`api_key_manager.py` & `bulk_keygen.py` (Credential Management):**
    
    -   **Secret Management:** `sk_live_...` formatında kırılması imkansız 64-karakterlik API anahtarları üretir ve PostgreSQL (TimescaleDB) tabanlı güvenlik tablosunda yönetir.
        
    -   **Automated Provisioning:** Toplu kullanıcı oluşturma ve yetkilendirme süreçlerini otomatize ederek SaaS operasyonlarını hızlandırır.
        

### 3. Veri Gölü ve İşleme Katmanı (Lakehouse & Processing Layer)

-   **`consumer_lake.py` (Bronze Layer Ingestion):**
    
    -   **Dumb Consumer Pattern:** Kafka'daki veriyi hiçbir ayrıştırma işlemine sokmadan doğrudan `string` olarak Delta Lake'e (MinIO) arşivler. Bu, olası şema değişikliklerinde (Schema Evolution) veri kaybı riskini ortadan kaldırır.
        
    -   **Backpressure Management:** `maxOffsetsPerTrigger=1000` parametresi ile veri patlamalarında sistemin kaynak tüketimini sabit tutar.
        
-   **`process_silver.py` (Spark Streaming Core):**
    
    -   **Window Aggregation:** 30 saniyelik pencerelerde (Sliding Windows) volatilite, işlem hacmi ve ağırlıklı ortalama fiyatlar gibi kompleks metrikleri saniyeler içinde hesaplar.
        
    -   **Polyglot Persistence:** İşlenmiş veriyi eşzamanlı olarak hem analitik katmana (Delta Lake) hem de operasyonel raporlama katmanına (TimescaleDB) asenkron olarak yazar.
        
-   **`batch_processor.py` & `batch_user_processor.py` (Batch ETL Services):**
    
    -   **Data Sanitization:** Kullanıcılar tarafından yüklenen CSV dosyalarını tarar, Türkçe karakterleri ve hatalı sütun isimlerini Regex tabanlı temizleyerek Lakehouse standartlarına uyarlar.
        
    -   **User Data Analytics:** Kullanıcıların kendi yüklediği verileri de sisteme dahil ederek **Gold Layer** (Analitik Katman) analizi için hazır hale getirir.
        
-   **`batch_yfinance_etl.py` (Historical Data Bridge):**
    
    -   **Backtesting Infrastructure:** Yapay zeka eğitiminde kullanılmak üzere Yahoo Finance üzerinden 2 yıllık saatlik ve 10 yıllık günlük geçmiş verileri çekerek Delta Lake ambarını zenginleştirir.
        

### 4. Otonom MLOps ve AI Katmanı (Intelligence Layer)

-   **`inference_api.py` (FastAPI MaaS Engine):**
    
    -   **Model-as-a-Service (MaaS):** Spark Streaming üzerindeki ağır makine öğrenmesi yükünü alarak RAM tüketimini **%60 optimize eden** çıkarım motorudur. MLflow'dan en güncel "Production" modelini RAM'e yükler ve milisaniyelik tahminler döner.
        
-   **`train_model.py` (AutoML Factory):**
    
    -   **Algorithm League:** XGBoost, LightGBM ve GradientBoosting algoritmalarını her varlık için birbiriyle yarıştırır. En düşük **RMSE** değerine sahip şampiyon modeli otomatik seçer.
        
    -   **Data Leakage Fix:** Zaman serisi verilerinde en büyük hata olan "gelecek verisinin sızması" sorununu **Target Shifting (`shift(-1)`)** tekniğiyle tamamen çözmüştür.
        
-   **`ml_watcher.py` (CD Orchestrator):**
    
    -   **Autonomous Lifecycle:** Veri gölündeki büyüme hızını izler. Yeterli veri biriktiğinde eğitimi tetikler ve eğitim bitince canlıdaki Inference API'ye `/reload` sinyali göndererek sistemi durdurmadan yeni modeli devreye alır.
        

### 5. İzleme, Kalite ve Kontrol (Governance Layer)

-   **`quality_gate.py` (Offline Data Quality Guard):**
    
    -   **Data Reliability:** Makine öğrenmesi öncesinde Delta Lake'i tarar; negatif fiyatlar, boş (Null) volatilite verileri veya bozuk zaman damgaları gibi "kirli verileri" raporlayarak model doğruluğunu garanti eder.
        
-   **`Home.py` & Streamlit Module Ecosystem (Control Plane):**
    
    -   **Infrastructure Telemetry:** `psutil` entegrasyonu ile sunucunun RAM/CPU durumunu, `docker-py` ile konteynerlerin durumunu canlı olarak terminal üzerinden yönetir.
        
    -   **Interactive Analysis:** `_Canli_Piyasa.py` ve `Gecmis_Analiz.py` modülleri ile hem Kafka akışını hem de 10 yıllık Delta Lake arşivi üzerinde kompleks SQL sorgularını görselleştirir.
## 🛠️ Setup & Operations Guide (DevOps Command Center)

RadarPro ekosistemi, kurumsal veri platformu standartlarında, 17+ mikroservisin Docker üzerinde orkestre edilmesiyle çalışır. Sistemin kurulumu, veri toplama süreçleri ve otonom döngüleri aşağıda adım adım açıklanmıştır.

### 1. Pre-Deployment: System Optimization (WSL2 & RAM)

Sistemi çalıştırmadan önce, Docker'ın (özellikle Windows/WSL2 üzerinde) kaynakları verimli kullanması için şu optimizasyonu manuel olarak veya `start_windows.bat` üzerinden yapmalısınız:

-   **Windows Kullanıcıları:** `%USERPROFILE%\.wslconfig` dosyasını şu şekilde yapılandırın:
    
    Ini, TOML
    
    ```
    [wsl2]
    memory=6GB        # Spark ve Kafka için ideal limit
    processors=2      # İşlemci çekirdek sayısı
    swap=4GB          # M2-SSD tabanlı sanal bellek
    autoMemoryReclaim=dropcache
    
    ```
    
-   Yapılandırmadan sonra terminalde `wsl --shutdown` komutu ile motoru yeniden başlatın.
    

----------

### 2. Infrastructure Deployment (Initial Start)

Tüm altyapıyı (Kafka, Spark, MLflow, MinIO, Postgres vb.) inşa etmek ve servisleri arka planda (detached) başlatmak için:

Bash

```
docker-compose up -d --build

```

_Bu aşamada 17 servis izole bir ağda birbirine bağlanır. Postgres'in hazır olması için sistem otomatik olarak 15 saniye bekleyecektir._

----------

### 3. Database Schema Provisioning (Kritik İlk Kurulum)

Sistem ayağa kalktıktan sonra, verinin kaydedileceği **TimescaleDB Hypertables** ve kullanıcıların yetkilendirileceği **Security** tabloları manuel olarak tetiklenmelidir:

#### A. Market Data & Time-Series Engine

Bash

```
docker exec -it postgres psql -U admin_lakehouse -d market_db -c "
CREATE TABLE IF NOT EXISTS market_data (
    symbol VARCHAR(20),
    average_price DOUBLE PRECISION,
    predicted_price DOUBLE PRECISION,
    volatility DOUBLE PRECISION,
    volume_usd DOUBLE PRECISION,    
    is_buyer_maker BOOLEAN,
    trade_side VARCHAR(10),          
    processed_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
CREATE EXTENSION IF NOT EXISTS timescaledb;
SELECT create_hypertable('market_data', 'processed_time', if_not_exists => TRUE);
"

```

#### B. API Auth & VIP Provisioning

Sistemin milisaniyelik verilerine tam erişim sağlamak için (Test modunda tüm kullanıcıları VIP yapar):

Bash

```
docker exec -it postgres psql -U admin_lakehouse -d market_db -c "
CREATE TABLE IF NOT EXISTS api_users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    api_key VARCHAR(64) UNIQUE NOT NULL,
    tier VARCHAR(20) DEFAULT 'FREE',
    password_hash VARCHAR(256),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
UPDATE api_users SET tier = 'VIP';
"

```

----------

### 4. Data Ingestion & ETL Operations

Sisteme veri pompalamak ve geçmiş verileri göle (Data Lake) indirmek için kullanılan komutlar:

-   **Historical Data ETL (yFinance):** Son 10 yıllık günlük ve son 2 aylık saatlik borsa verilerini MinIO'ya indirir.
    
    Bash
    
    ```
    docker exec -it spark-silver python /app/batch_yfinance_etl.py
    
    ```
    
-   **Universal Data Ingestion (IoT/Log Sim):** Sadece kripto değil, IoT ve genel veri tiplerini test etmek için.
    
    Bash
    
    ```
    docker exec -it spark-silver python universal_producer.py
    
    ```
    
-   **B2B Company Simulation (External API):** Dışarıdaki bir fabrikadan API ile veri geliyor gibi simüle etmek için.
    
    Bash
    
    ```
    python fake_company.py
    
    ```
    

----------

### 5. MLOps: Continuous Training & Hot-Reload

Modelleri eğitmek ve canlı sistemi durdurmadan yeni zekayı devreye almak için:

-   **Full AutoML Engine:** Tüm piyasadaki coinler için en iyi modeli (XGBoost/LightGBM) yarıştırır ve Production'a alır.
    
    Bash
    
    ```
    docker exec -it spark-silver python /app/train_model.py ALL
    
    ```
    
-   **Autonomous ML Watcher (CD Pipeline):** Göl biriktikçe otonom eğitimi başlatır ve canlı API'ye `/reload` sinyali gönderir.
    
    Bash
    
    ```
    docker exec -d spark-silver python /app/ml_watcher.py
    
    ```
    
-   **Data Quality Gate:** Modeller eğitilmeden önce kirli verileri (negatif fiyatlar, bozuk timestamps) tarar.
    
    Bash
    
    ```
    docker exec -it spark-silver python quality_gate.py
    
    ```
    

----------

### 6. Service Management & Maintenance (Hot-Reload)

Kod üzerinde değişiklik yaptığınızda sistemi kapatmadan güncelleyebilirsiniz:

-   **Dashboard Update:** `docker-compose up -d --build dashboard`
    
-   **Inference API Update:** `docker-compose up -d --build inference_api`
    
-   **Data Lake Cleanup:** Veri gölünü tamamen sıfırlamak için:
    
    Bash
    
    ```
    docker exec -it minio mc rm -r --force s3/market-data/raw_layer_delta s3/market-data/silver_layer_delta
    
    ```
    

----------

### 7. Frontend & Desktop Terminal Setup (Electron)

Web tabanlı terminalin yanı sıra kurumsal masaüstü deneyimi için:

1.  **Web Access:** [http://localhost:8501](https://www.google.com/search?q=http://localhost:8501)
    
2.  **Masaüstü Terminali (Electron):**
    
    Bash
    
    ```
    cd frontend
    npm install        # Bağımlılıkları kur (Sadece bir kez)
    npm start          # Masaüstü uygulamasını fırlat
    
    ```
    
    _`main.js` sayesinde CORS kısıtlamaları otomatik aşılır ve API'ye tam yetkiyle bağlanılır._


## 📊 Servis ve Altyapı Erişim Matrisi (Eksiksiz Liste)

Sistem `docker-compose up` ile ayağa kalktığında, aşağıdaki servisler belirtilen portlar üzerinden hizmet vermeye başlar. Her bir servis, ekosistemin farklı bir katmanını (Ingestion, Processing, Analytics, MLOps) temsil eder.

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

### 🔑 Kritik Yönetim Bilgileri (Default Credentials)

Sisteme ilk kez girecek olan geliştiriciler için varsayılan giriş bilgileri:

-   **MinIO Console:** `admin` / `admin12345`
    
-   **Grafana:** `grafana_admin` / `SuperSecret_Grafana_2026`
    
-   **PostgreSQL:** `admin_lakehouse` / `SuperSecret_DB_Password_2026`
    
-   **API Gateway:** Kayıt olduktan sonra portal üzerinden alacağınız `sk_live_...` anahtarı.
----------


## ⚡ Enterprise-Grade Data Governance & New Features

RadarPro v6.0 ile gelen bu özellikler, platformu hobi projesinden çıkarıp ticari bir **Data-as-a-Service (DaaS)** altyapısına dönüştürür:

### 1. 🧬 Generic Producer & Schema-Agnostic Ingestion

Sistemin veri giriş katmanı artık tamamen esnektir. Sabit kodlu şemalar terk edilerek **Schema-on-Read** prensibine geçilmiştir.

-   **Data Agnostic:** Sistem; JSON içindeki `data_type` etiketine göre veriyi otonom olarak tanır (Crypto, IoT, Web Log, Server Telemetry).
    
-   **Universal Carrier:** Kafka ve Bronze katmanı sadece taşıyıcıdır; yeni bir veri kaynağı eklemek için backend kodunda değişiklik yapmaya gerek yoktur.
    

### 2. 🗄️ Multi-Tenant Data Lake Architecture (Partitioning)

MinIO (S3) üzerindeki Delta Lake dosyaları, yüksek performanslı sorgulama için rastgele tutulmaz. **Multi-tenant** yapısına uygun olarak bölümlenir:

-   **Dynamic Partitioning:** Veriler kaynağına, sembolüne ve yılına göre otomatik olarak klasörlenir (`source=binance/symbol=BTCUSDT/year=2026/`).
    
-   **I/O Optimization:** Bu mimari sayesinde Spark, 10 yıllık veri içinde arama yaparken tüm diski taramak yerine sadece ilgili bölüme (partition) giderek sorgu hızını %80 artırır.
    

### 3. 🛡️ Autonomous Lakehouse Maintenance (Optimize & Vacuum)

Büyük veri sistemlerindeki "küçük dosya problemi" (Small File Problem), sistem tarafından otonom olarak çözülür:

-   **Optimize:** S3 üzerindeki binlerce küçük Parquet dosyası, yönetim panelinden tetiklenen bir görevle birleştirilerek tek bir büyük, optimize edilmiş dosyaya dönüştürülür.
    
-   **Vacuum:** Delta Lake loglarındaki eski ve geçersiz veri sürümleri temizlenerek depolama maliyetleri düşürülür ve "Storage Leak" engellenir.
    

### 🔒 4. Enterprise Rate Limiting & Security Gateway

Dış dünyaya açık olan API katmanı, kurumsal seviyede koruma altındadır:

-   **Rate Limiter:** Kullanıcıların `tier` seviyesine göre (FREE/VIP) saniyelik istek sınırları uygulanır.
    
-   **Credential Vault:** Tüm API anahtarları PostgreSQL üzerinde hash'lenmiş olarak saklanır ve WebSocket bağlantılarında milisaniyelik doğrulama (auth) yapılır.

## 🎨 Frontend Ecosystem & Client-Side Architecture

RadarPro, sadece bir web arayüzü değil; düşük gecikmeli veri akışını (Low Latency Stream) görselleştirmek için optimize edilmiş, **Hybrid UI** mimarisine sahip bir ekosistemdir. Tasarım dili olarak finans dünyasının standardı olan "Bloomberg/TradingView" koyu tema disiplini benimsenmiştir.

### 1. Teknolojik Altyapı (Tech Stack)

-   **Tailwind CSS:** Modern, performanslı ve responsive tasarım iskeleti.
    
-   **Lightweight Charts (TradingView):** Milisaniyelik fiyat hareketlerini tarayıcıyı yormadan render eden yüksek performanslı grafik motoru.
    
-   **Electron.js:** Web teknolojilerini yerel bir masaüstü uygulamasına dönüştüren ve CORS kısıtlamalarını aşarak API ile doğrudan haberleşen "Desktop Wrapper" katmanı.
    
-   **WebSockets & REST:** VIP kullanıcılar için saniyelik veri akışı ve geçmiş analizler için asenkron API iletişimi.
    

----------

### 2. Modüler Sayfa Yapısı ve İşlevsellik

#### 🏛️ **Pro Terminal (Institutional Dashboard)**

-   **Dosya:** `index.html`
    
-   **Fonksiyon:** Bloomberg V18 stiliyle tasarlanmış, 25 farklı varlığın canlı fiyatlarını, teknik indikatörlerini (RSI, MACD, Bollinger Bands) ve yapay zeka (AI) fiyat tahminlerini tek ekranda sunan ana operasyon merkezidir.
    
-   **Öne Çıkan Özellik:** Veri hattından gelen "Predicted Price" (AI Tahmini) verisini canlı grafiğe bir "Gölge Fiyat" olarak işler.
    

#### 🔍 **Asset Intelligence (L1 Detail)**

-   **Dosya:** `coin_detail.html`
    
-   **Fonksiyon:** Tek bir varlığa odaklanan derinlemesine analiz sayfasıdır.
    
-   **Order Book (L1):** Alıcı ve satıcı dengesini (Bids/Asks) milisaniyelik görselleştirir.
    
-   **Technical Integration:** TradingView'in gelişmiş grafik kütüphanesiyle (TV Widget) tam entegre çalışır.
    

#### 🔐 **User Portal & Security Center**

-   **Dosya:** `portal.html`, `settings.html`, `login.html`
    
-   **Fonksiyon:** Kullanıcıların API anahtarlarını (`X-API-Key`) yönettiği, paket seviyelerini (FREE/VIP) gördüğü ve güvenlik ayarlarını yapılandırdığı yönetim katmanıdır.
    
-   **Auth System:** `ingestion_api.py` üzerindeki hash'lenmiş veritabanıyla tam uyumlu giriş ve kayıt döngüsü sağlar.
    

----------

### 3. 🖥️ Masaüstü Uygulaması (Electron Desktop App)

RadarPro, profesyonel trader'ların tarayıcı sekmeleri arasında kaybolmasını önlemek için bağımsız bir masaüstü uygulaması olarak paketlenmiştir:

-   **Web Security Bypass:** `webSecurity: false` konfigürasyonu sayesinde, yerel ağdaki (Localhost) API ve Kafka kaynaklarına hiçbir tarayıcı engeli (CORS) olmadan en yüksek hızda bağlanır.
    
-   **Native Experience:** `autoHideMenuBar` özelliği ile standart pencere görünümünden kurtulup, tam ekran bir terminal deneyimi sunar.
    

----------

### 🛠️ Frontend Kurulum ve Çalıştırma

Terminal arayüzünü masaüstü uygulaması olarak başlatmak için aşağıdaki adımları izleyin:

1.  **Bağımlılıkların Yüklenmesi:**
    
    Bash
    
    ```
    cd frontend
    npm install
    
    ```
    
2.  **Masaüstü Uygulamasının Başlatılması:**
    
    Bash
    
    ```
    npm start
    
    ```
    
    _Bu komut, Electron motorunu tetikleyerek `home.html` üzerinden sistemi ayağa kaldırır._
    
3.  **Web Üzerinden Erişim:** Docker ayağa kalktığında, herhangi bir kuruluma gerek kalmadan `http://localhost:8501` adresinden kurumsal yönetim paneline erişilebilir.


----------

## 🤝 Katkıda Bulunun (Contributing)

Bu proje, bir **Yönetim Bilişim Sistemleri (YBS)** öğrencisi tarafından geliştirilmiş, akademik disiplin ile mühendislik pratiğini birleştiren açık kaynaklı bir framework'tür. Bitirme tezi kapsamında geliştirilen bu yapının büyümesi için her türlü PR (Pull Request) ve fikre kapımız açıktır.

-   **Geliştirici:** Ömer Çakan
    
-   **LinkedIn:** [Ömer Çakan - Profiline Git](https://www.google.com/search?q=https://www.linkedin.com/in/%25C3%25B6mer-%2525C3%2525A7akan-819751261)
    
-   **Destek:** Eğer bu proje size veri mühendisliği veya MLOps yolculuğunuzda ilham verdiyse, lütfen depoya bir ⭐ bırakmayı unutmayın!
    

### 🛠️ Geliştiriciler İçin Kod Talimatı

Sistem üzerinde geliştirme yapmak istiyorsanız lütfen aşağıdaki iş akışını takip edin:

1.  **Projeyi Fork'layın ve Yerelinize İndirin:**
    
    Bash
    
    ```
    git clone https://github.com/propaper12/An-Open-Source-Real-Time-Financial-Lakehouse-Project.git
    
    ```
    
2.  **Yeni Özellik İçin İzole Bir Branch Açın:** _(Lütfen `main` branch'ine doğrudan push yapmayın)_
    
    Bash
    
    ```
    git checkout -b dev/isminiz_ve_ozellik_adi
    
    ```
    
3.  **Geliştirmenizi Yapın ve Değişiklikleri Push'layın:**
    
    Bash
    
    ```
    git add .
    git commit -m "feat: [Modül Adı] Yeni özellik açıklaması"
    git push origin dev/isminiz_ve_ozellik_adi
    
    ```
    
4.  **Pull Request Gönderin:** Değişiklikleriniz incelendikten sonra ana projeye dahil edilecektir.
    

----------

_© 2026 RadarPro Ecosystem - Real-Time Intelligence for Everyone._

## 🤝 Projenin görselleri:
<img width="2879" height="1530" alt="Ekran görüntüsü 2026-03-05 161743" src="https://github.com/user-attachments/assets/e8480dd7-0c9b-485f-b542-47a96ad13c0f" />
![Uplo<img width="2783" height="1545" alt="Ekran görüntüsü 2026-03-05 162814" src="https://github.com/user-attachments/assets/54d68605-2c1b-4328-9593-1d64399c24b0" />
ading Ekran g<img width="2792" height="1537" alt="Ekran görüntüsü 2026-03-05 162932" src="https://github.com/user-attachments/assets/9fb3cc13-a4c0-4b9c-8b9a-fbdc352991c3" />
<img width="2790" height="1536" alt="Ekran görüntüsü 2026-03-05 162940" src="https://github.com/user-attachments/assets/0a9a6676-b610-44f3-b06b-3dacbe7043b3" />
<img width="2793" height="1541" alt="Ekran görüntüsü 2026-03-05 162948" src="https://github.com/user-attachments/assets/f38ed7c0-9c46-4cbd-8db5-2d506d43ed8d" />
<img width="2792" height="1530" alt="Ekran görüntüsü 2026-03-05 163003" src="https://github.com/user-attachments/assets/7c4bf4c9-1560-488f-924e-9e8e768e068f" />
<img width="2776" height="1531" alt="Ekran görüntüsü 2026-03-05 163014" src="https://github.com/user-attachments/assets/74aa16bf-019b-4cbe-abe7-dacd1d76b086" />
<img width="2784" height="1543" alt="Ekran görüntüsü 2026-03-05 163023" src="https://github.com/user-attachments/assets/89518172-f7a5-4770-83ef-7c6c390ef3b2" />
<img width="2792" height="1533" alt="Ekran görüntüsü 2026-03-05 163133" src="https://github.com/user-attachments/assets/da1d66e7-9870-4510-89e4-8a07f7c651ca" />
<img width="2780" height="1546" alt="Ekran görüntüsü 2026-03-05 163144" src="https://github.com/user-attachments/assets/4185d561-2608-4193-a62b-454a5af0f856" />
<img width="2764" height="1542" alt="Ekran görüntüsü 2026-03-05 163202" src="https://github.com/user-attachments/assets/41afe0c7-039b-457d-a9b6-cab18ecc2275" />
<img width="2757" height="1545" alt="Ekran görüntüsü 2026-03-05 163211" src="https://github.com/user-attachments/assets/8ab6df55-3537-4417-9325-e609016b4740" />
<img width="2773" height="1545" alt="Ekran görüntüsü 2026-03-05 163239" src="https://github.com/user-attachments/assets/ca8c242a-1fe0-4020-9980-7e35a8ff0f36" />
<img width="2793" height="1535" alt="Ekran görüntüsü 2026-03-05 162823" src="https://github.com/user-attachments/assets/dd84e964-4d05-4db2-9194-2a1b4f0786f6" />
<img width="2793" height="1547" alt="Ekran görüntüsü 2026-03-05 162843" src="https://github.com/user-attachments/assets/334ae1d2-c7a8-4ad4-a830-733bb5be6961" />
<img width="2775" height="1547" alt="Ekran görüntüsü 2026-03-05 162853" src="https://github.com/user-attachments/assets/6adca6a8-413e-4337-b428-784ad2a36c88" />
<img width="2775" height="1531" alt="Ekran görüntüsü 2026-03-05 162923" src="https://github.com/user-attachments/assets/87a1439a-d3ae-4769-b5fa-0e1dccc1e7a9" />
örüntüsü 2026-03-05 161743.png…]()

![Uploading Ekran görüntüsü 2026-03-05 165629.png…]()
<img width="2677" height="1691" alt="Ekran görüntüsü 2026-03-05 165637" src="https://github.com/user-attachments/assets/1e67686c-17f8-4138-ba40-6c8055d2be28" />
<img width="2780" height="1525" alt="Ekran görüntüsü 2026-03-05 165413" src="https://github.com/user-attachments/assets/79111f69-d40d-4cb8-b2ef-73a4e2980139" />

<img width="2787" height="1545" alt="Ekran görüntüsü 2026-03-05 165421" src="https://github.com/user-attachments/assets/26e9c0d9-a0db-4ec7-af4a-06493d7ca368" />
<img width="2268" height="1220" alt="Ekran görüntüsü 2026-03-05 165531" src="https://github.com/user-attachments/assets/e5e0d42d-386e-4a25-ba86-c7bfaeea3bd7" />
<img width="2879" height="1704" alt="Ekran görüntüsü 2026-03-05 165602" src="https://github.com/user-attachments/assets/c1b3d7dc-57e3-4c4c-934c-efea9a5ffbf6" />






<img width="2772" height="1476" alt="Ekran görüntüsü 2026-02-05 170637" src="https://github.com/user-attachments/assets/6548da13-a35f-4d57-ac58-c02da3c0969e" />
