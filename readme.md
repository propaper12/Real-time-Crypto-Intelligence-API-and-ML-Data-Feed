<img width="2738" height="1656" alt="Ekran görüntüsü 2026-04-11 201616" src="https://github.com/user-attachments/assets/259b5566-9269-4852-818b-bda3c6710ad1" />
<img width="2734" height="1644" alt="Ekran görüntüsü 2026-04-11 201623" src="https://github.com/user-attachments/assets/e6825ff8-45b0-409d-80e5-3a51f75be2a2" />
<img width="2721" height="1636" alt="Ekran görüntüsü 2026-04-11 201649" src="https://github.com/user-attachments/assets/f38fd7f1-6cc1-4e25-8248-eca7ae052018" />
<img width="2766" height="1550" alt="Ekran görüntüsü 2026-04-11 201700" src="https://github.com/user-attachments/assets/5d0efaeb-5e4d-4759-a502-825eacfdaf1c" />
<img width="2782" height="1546" alt="Ekran görüntüsü 2026-04-11 201710" src="https://github.com/user-attachments/assets/bbd20167-43ae-4107-889d-11b2ffe5bc43" />
<img width="2733" height="1633" alt="Ekran görüntüsü 2026-04-11 201608" src="https://github.com/user-attachments/assets/c81c305f-cf03-4067-b85f-ed6360b4a17e" />
<h1 align="center">RadarPro: Real-Time Crypto Intelligence API & MLOps Platform</h1>

<p align="center">
  <i>An Enterprise-Grade Real-Time Data-as-a-Service (DaaS) and MLOps Ecosystem</i>
</p>

<div align="center"> 
  <img src="https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white" /> 
  <img src="https://img.shields.io/badge/Google_Gemini-8E75B2?style=for-the-badge&logo=google&logoColor=white" />
  <img src="https://img.shields.io/badge/Apache_Spark-E25A1C?style=for-the-badge&logo=apache-spark&logoColor=white" /> 
  <img src="https://img.shields.io/badge/Apache_Kafka-231F20?style=for-the-badge&logo=apache-kafka&logoColor=white" /> 
  
  <img src="https://img.shields.io/badge/MinIO-C7202C?style=for-the-badge&logo=minio&logoColor=white" />
  <img src="https://img.shields.io/badge/Delta_Lake-00AEEF?style=for-the-badge&logoColor=white" />
  
  <img src="https://img.shields.io/badge/PostgreSQL-4169E1?style=for-the-badge&logo=postgresql&logoColor=white" /> 
  <img src="https://img.shields.io/badge/TimescaleDB-FDB515?style=for-the-badge&logo=timescaledb&logoColor=black" />
  <img src="https://img.shields.io/badge/Redis-DC382D?style=for-the-badge&logo=redis&logoColor=white" />

  <img src="https://img.shields.io/badge/MLflow-0194E2?style=for-the-badge&logo=mlflow&logoColor=white" />
  <img src="https://img.shields.io/badge/scikit_learn-F7931E?style=for-the-badge&logo=scikit-learn&logoColor=white" />
  <img src="https://img.shields.io/badge/XGBoost-102A44?style=for-the-badge&logo=XGBoost&logoColor=white" />

  <img src="https://img.shields.io/badge/FastAPI-009688?style=for-the-badge&logo=fastapi&logoColor=white" />
  <img src="https://img.shields.io/badge/Streamlit-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white" />
  
  <img src="https://img.shields.io/badge/Docker-2496ED?style=for-the-badge&logo=docker&logoColor=white" /> 
  <img src="https://img.shields.io/badge/Prometheus-E6522C?style=for-the-badge&logo=prometheus&logoColor=white" />
  <img src="https://img.shields.io/badge/Grafana-F46800?style=for-the-badge&logo=grafana&logoColor=white" />
  <img src="https://img.shields.io/badge/Metabase-509EE3?style=for-the-badge&logo=metabase&logoColor=white" />
  <img src="https://img.shields.io/badge/dbt-FF694B?style=for-the-badge&logo=dbt&logoColor=white" />
</div>

<br>

> **Note:** Bu proje, yüksek frekanslı (high-frequency) finansal verileri milisaniyelik gecikmeyle (low-latency) işleyen, depolayan ve DaaS (Data-as-a-Service) modeliyle son kullanıcıya sunan uçtan uca bir veri mühendisliği ve MLOps mimarisidir.

---

# RadarPro: Real-Time Crypto Intelligence API & MLOps Pipeline


## 📖 RadarPro: Vizyon ve Sistem Felsefesi

**RadarPro**, finansal veri ekosistemlerindeki en kritik darboğazlar olan **yüksek veri gecikmesi (latency)** ve **model drift (performans kaybı)** sorunlarını modernize etmek amacıyla geliştirilmiş, uçtan uca bir **Data Engineering ve MLOps platformudur.**

Platformun temel mimarisi, verinin ham kaynaktan (Binance WebSocket) alınmasından itibaren milisaniyeler içinde işlenmesini, **Medallion Architecture (Bronze/Silver/Gold)** standartlarında depolanmasını ve otonom yapay zeka modelleriyle bir sonraki periyodun (fiyat/anomali) tahmin edilmesini kapsar.

## 🎯 Temel Değer Önerileri

-   **Gerçek Zamanlı Karar Destek:** Geleneksel "Batch" işlemeye dayalı hantal yapıların aksine RadarPro, verinin oluşumu ile işlenmiş analitik çıktıya dönüşmesi arasındaki süreyi **5 saniyenin altına indirir.**
    
-   **Otonom Sistem Mimarisi:** Sistem sadece veri sunmakla kalmaz; **Self-Healing (Kendi Kendini Onaran)** ve **Self-Learning (Kendi Kendini Eğiten)** yapısıyla, veri hacmi arttıkça modellerini otomatik olarak günceller ve üretim hattına (production) kesintisiz dahil eder.
    
-   **Analitik Derinlik:** Sadece fiyat odaklı değil; likidasyon akışları (liquidation clusters), CVD (Cumulative Volume Delta) ve VPIN (Volume-based Probability of Informed Trading) gibi sofistike finansal metrikleri gerçek zamanlı hesaplayarak kurumsal düzeyde bir veri ambarı sunar

----------

🌟 Mühendislik ve Tasarımın Temel Direkleri
⚡ 1. Ultra-Düşük Gecikmeli Veri Akış Hattı (V28 God Mode Ingestion)
Sistem, Binance Futures WebSocket katmanından 25 farklı kripto varlığın anlık işlemlerini (Trade), Emir Defteri (Depth) derinliğini ve Likidasyon verilerini asenkron olarak tüketir. Apache Kafka; yüksek sıkıştırma (gzip), lider onayı (acks=1) ve 1000 mesajlık tetikleyici (maxOffsetsPerTrigger) stratejisiyle veriyi kayıpsız iletir. Bu yapı, ham verinin milisaniyeler içinde işleme katmanına ulaşmasını sağlar.

🚀 2. Model-as-a-Service (MaaS) ve Redis Tabanlı RAM Optimizasyonu
Finansal veri işlemede en büyük maliyet kalemi olan RAM tüketimi, akıllı bir mikroservis ayrımıyla çözülmüştür. Spark motoru üzerindeki ağır çıkarım (inference) yükü, asenkron bir FastAPI çıkarım motoruna (inference_api.py) devredilmiştir. Bu MaaS yaklaşımı, toplam RAM ihtiyacını %60 oranında azaltırken, Redis Pub/Sub üzerinden model senkronizasyonu sağlayarak binlerce tahmini eşzamanlı sunar.

🧠 3. Bilimsel Tahminleme ve Gelişmiş Finansal Metrikler
Sistem, “Data Leakage” (Veri Sızıntısı) riskini Target Shifting ile engellemenin ötesine geçmiştir. Fiyat tahminine ek olarak; CVD (Cumulative Volume Delta), VPIN (Volume-based Probability of Informed Trading) ve Wall Imbalance gibi kurumsal düzeyde metrikler gerçek zamanlı olarak hesaplanır. Ayrıca, türev piyasalar için kritik olan Likidasyon Mıknatısları (10x-100x) otonom olarak belirlenir.

🔄 4. Otonom CD Döngüsü ve Redis Pub/Sub Sync
Platform, ML Watcher modülü sayesinde başında bir operatör beklemeden 7/24 otonom çalışır. Delta Lake’de yeterli eşik (MIN_ROWS_TO_START) geçildiğinde eğitim tetiklenir. Yeni model MLflow’da tescillendikten sonra Redis üzerinden RELOAD_MODELS sinyali gönderilir; böylece tüm API worker’ları sıfır kesintiyle en güncel modele geçer.

🛡️ 5. Z-Score Tabanlı Anomali ve Manipülasyon Dedektörü
RadarPro, veriyi sadece işlemez, aynı zamanda denetler. Z-Score Anomali Dedektörü sayesinde; hacim patlamaları (Wash Trading) ve sahte duvarlar (Spoofing) saniyeler içinde tespit edilir. Data Quality Gate modülü ise hatalı verilerin modellere sızmasını engelleyerek tahmin doğruluğunu “saf veri” üzerinden korur.

🖥️ 6. Hibrit Terminal ve Kurumsal API Gateway
Kullanıcı deneyimi ikiye ayrılmıştır:

DaaS API Gateway: VIP/FREE katmanları için özelleştirilmiş, Redis tabanlı Rate Limiting ve Auth katmanına sahip kurumsal API hizmeti.

Pro Terminal: Streamlit ve Electron tabanlı, profesyonel trader’lar için milisaniyelik hassasiyetle görselleştirme sunan masaüstü ve web arayüzü.

🛡️ Redis: Distributed Control Plane (Merkezi Kontrol Düzlemi)
Sistemde Redis, sadece bir önbellek değil; güvenliği, hız sınırlamasını, anlık anomali skorlarını ve modellerin canlı senkronizasyonunu yöneten Merkezi Kontrol Düzlemi olarak konumlandırılmıştır.

⚙️ Temel Özellikler ve Mimari Çözümler
Dağıtık Hız Sınırlama (Distributed Rate Limiting): API Gateway’in yatayda ölçeklenebilir (multi-node) yapısı nedeniyle, kullanıcı istek sayıları yerel bellekte değil, Redis üzerinde Atomic Counters kullanılarak takip edilir. Bu sayede kullanıcı, farklı API instance’larına istek atsa dahi toplam limiti (VIP için saniyede 50, Premium için 10 istek) merkezi olarak korunur.

Otonom Ban ve Kota Mekanizması: Ücretsiz (FREE) katmandaki kullanıcılar için günlük 1000 istek sınırı belirlenmiştir. Redis, bu sınırı aşan anahtarları otomatik olarak tespit eder, ban:email anahtarı ile işaretler ve kullanıcıyı kalıcı olarak sistemden uzaklaştırır.

Tier-Based Access Control (DaaS Logic):

VIP/PREMIUM Tier: Gerçek zamanlı Kafka/WebSocket akışına erişim, sınırsız geçmiş veri indirme ve yapay zeka (ML) tahminlerini içeren tam yetkili erişim.

FREE Tier: 24 saatlik geçmiş veriyle sınırlı, yapay zeka tahminlerinden arındırılmış ve kotalı erişim.

Ultra-Düşük Gecikmeli Doğrulama (In-Memory Auth): Her API isteğinde ana veritabanına (PostgreSQL) yük bindirmek yerine, API Key yetki kontrolleri ve hız limitleri Redis üzerinden RAM hızında (<1ms) gerçekleştirilerek sistem darboğazları önlenir.

🧠 Neden Redis? (Mimari Tercih)
Bir Veri Mühendisi olarak sistemin stateless (durumsuz) kalması, yatayda büyüme (scaling) için zorunluluktur. Redis kullanımıyla sağlanan avantajlar şunlardır:

High Availability (Yüksek Erişilebilirlik): API sunucuları çökse veya yeniden başlasın, kullanıcı limitleri ve ban listeleri merkezi RAM katmanında korunduğu için veri kaybı yaşanmaz.

Consistency (Tutarlılık): Dağıtık mimaride tüm Gateway’ler için tek bir “Doğruluk Kaynağı” (Single Source of Truth) oluşturulur.

Database Protection: Operasyonel veritabanı (PostgreSQL), her saniye gelen binlerce limit kontrol sorgusundan arındırılarak sadece kalıcı finansal veriye odaklanması sağlanır.
---


## 📂 Proje Yapısı (Core Backend & Infrastructure)

RadarPro ekosistemi, **Separation of Concerns** prensibine uygun olarak modüler bir mikroservis mimarisiyle kurgulanmıştır. Her bileşen, sistemin bütününe hizmet eden bağımsız bir servis olarak tasarlanmıştır.

Plaintext

```
├── dashboard_app/              # 🎛️ Internal Control Plane (PoC Showcase)
│   ├── Home.py                  # Platform Ana Giriş ve Altyapı Telemetrisi 
│   ├── utils.py                 # CSS Enjeksiyonu ve S3/Postgres Bağlantı Cache Katmanı 
│   ├── _Canli_Piyasa.py         # Real-Time Kafka & V28 God Mode Görselleştirme 
│   ├── Gecmis_Analiz.py         # Delta Lake Arşivi Üzerinden Batch Analiz ve Korelasyon 
│   ├── _MLOps_Center.py         # MLflow Model Registry ve AutoML Liderlik Tablosu 
│   └── _Sistem_Yonetimi.py      # Docker Konteyner Kontrolü ve Maintenance (Optimize/Vacuum) 
│
├── ingestion_layer/            # 📡 Data Gateway & Ingestion Services
│   ├── producer.py              # Binance WebSocket - High-Frequency Ingestion Motoru 
│   ├── universal_producer.py    # Schema-Agnostic / IoT / Log Veri Simülatörü 
│   ├── ingestion_api.py         # Enterprise API Gateway (VIP/FREE Auth & Rate Limiting) 
│   └── fake_company.py          # B2B Şirket Verisi Simülasyonu (REST API Client) 
│
├── processing_layer/           # ⚙️ Big Data Processing & Lakehouse Architecture
│   ├── consumer_lake.py         # Bronze Layer (Raw Archive) Spark Streaming Tüketicisi 
│   ├── process_silver.py        # Silver Layer (V28 God Mode) - Feature Engineering & Anomaly Detector 
│   ├── batch_processor.py       # Geçmişe Dönük CSV ETL ve Data Sanitization Motoru 
│   └── batch_yfinance_etl.py    # yFinance Bridge - 10 Yıllık Tarihsel Veri Aktarıcı 
│
├── mlops_layer/                # 🧠 Artificial Intelligence & Autonomous MLOps
│   ├── inference_api.py         # FastAPI MaaS Engine (Milisaniyelik AI Tahmin Servisi) 
│   ├── train_model.py           # XGBoost + LightGBM AutoML Fabrikası 
│   ├── ml_watcher.py            # Otonom Continuous Training (CT) ve Hot-Reload Orkestratörü 
│   └── quality_gate.py          # Data Quality Gate (Model Öncesi Veri Güvenlik Kapısı) 
│
├── devops_config/              # 🐳 Container Orchestration & Monitoring
│   ├── docker-compose.yaml      # 15+ Mikroservisin Global Orkestrasyonu 
│   ├── Dockerfile.spark         # Apache Spark & Delta Lake Optimize Edilmiş İmaj 
│   ├── Dockerfile.api           # FastAPI & Ingestion Gateway İmajı [cite: 
│   ├── Dockerfile.ui            # Streamlit Dashboard İmajı 
│   ├── prometheus.yml           # Altyapı Metrik Toplama Yapılandırması 
│   └── start_unix.sh            # Unix/Mac DevOps Command Center Scripti 
└── readme.md                   # Proje Teknik Dokümantasyonu (Ana Rehber) 

```

----------

> **💡 Mühendislik Notu:** Bu yapı, **Medallion Architecture** prensiplerine göre kurgulanmıştır. Verinin ham haliyle girdiği (Ingestion), analitik metriklerin ve anomalilerin hesaplandığı (Processing) ve otonom zekaya dönüştüğü (MLOps) katmanlar birbirinden fiziksel olarak izole edilmiştir. Bu izolasyon, sistemin herhangi bir katmanının diğerini etkilemeden bağımsız olarak ölçeklenmesini (Horizontal Scaling) sağlar.




## 🏗️ Mimari Tasarım (Architecture)

RadarPro ekosistemi, **Veri Mühendisliği (Data Engineering)** ve **MLOps** prensiplerine tam uyumlu, dağıtık bir mikroservis yapısıyla tasarlanmıştır. Her modül, kurumsal veri platformlarında karşılaşılan ölçeklenebilirlik ve gecikme darboğazlarını aşmak için optimize edilmiştir:

## 1. Veri Kaynağı ve İletişim Katmanı (Ingestion & Pub/Sub Layer)

-   **`producer.py` (Binance Futures Connector):**
    
    -   **Resilience:** Ağ kopmalarına karşı `ping_interval` mekanizmasıyla kesintisiz bir WebSocket hattı kurar.
        
    -   **Multi-Asset Ingestion:** 25 farklı kripto varlığın anlık işlem, emir defteri derinliği ve likidasyon verilerini asenkron olarak toplar ve Kafka'ya `gzip` sıkıştırma ile iletir.
        
-   **`universal_producer.py` (Schema-Agnostic Engine):**
    
    -   **Generic Ingestion:** Finans dışı verileri (IoT, Log) sistemin anlayabileceği ortak bir şemaya normalize ederek platformun esnekliğini kanıtlar.
        
-   **`fake_company.py` (B2B Data Simulation):**
    
    -   **Tenant Simulation:** Harici şirketlerin veri üretim hattını taklit ederek veriyi doğrudan **Ingestion API** üzerinden sisteme enjekte eder.
        

## 2. Güvenlik ve API Geçit Katmanı (Security & Gateway Layer)

-   **`ingestion_api.py` (Enterprise Data Gateway):**
    
    -   **DaaS Logic:** Redis tabanlı **Rate Limiting** ve **Auth** katmanı ile FREE/VIP kullanıcılar için özelleştirilmiş veri erişimi sağlar.
        
    -   **Real-Time Broadcast:** VIP kullanıcılara özel, düşük gecikmeli Kafka akışlarını WebSocket üzerinden anlık yayınlar.
        
-   **`bulk_keygen.py` (Credential Provisioning):**
    
    -   **Security Management:**  `sk_live_...` formatında 64 karakterlik kriptografik API anahtarları üreterek SaaS operasyonlarını yönetir.
        

## 3. Veri Gölü ve İşleme Katmanı (Lakehouse & Processing Layer)

-   **`consumer_lake.py` (Bronze Layer - Raw Archive):**
    
    -   **Schema-on-Read:** Kafka verisini ayrıştırmadan "Raw" (ham) haliyle Delta Lake'e arşivleyerek şema değişikliklerine karşı koruma sağlar.
        
    -   **Backpressure Control:**  `maxOffsetsPerTrigger` parametresiyle veri patlamalarında sistemin çökmesini engeller.
        
-   **`process_silver.py` (V28 God Mode Core):**
    
    -   **Advanced Analytics:** Sliding Windows kullanarak **CVD**, **VPIN** ve **Anomali Skorlarını** (Z-Score) saniyeler içinde hesaplar.
        
    -   **Polyglot Persistence:** İşlenmiş veriyi analitik için Delta Lake'e, operasyonel raporlama için TimescaleDB'ye eşzamanlı yazar.
        
-   **`batch_yfinance_etl.py` (Historical Bridge):**
    
    -   **Backtesting Infrastructure:** Yahoo Finance üzerinden 10 yıllık tarihsel veriyi çekerek Delta Lake ambarını zenginleştirir.
        

## 4. Otonom MLOps ve AI Katmanı (Intelligence Layer)

-   **`inference_api.py` (FastAPI MaaS Engine):**
    
    -   **RAM Optimization:** Spark üzerindeki çıkarım yükünü devralarak sistem belleğini **%60 optimize eder** ve milisaniyelik tahminler sunar.
        
-   **`train_model.py` (AutoML Factory):**
    
    -   **Algorithm League:** XGBoost ve LightGBM algoritmalarını yarıştırarak her varlık için en düşük **RMSE** değerine sahip modeli seçer.
        
-   **`ml_watcher.py` (CD Orchestrator):**
    
    -   **Autonomous Lifecycle:** Veri gölündeki büyümeyi izler, eğitimi tetikler ve **Redis Pub/Sub** üzerinden API'ye model yenileme sinyali gönderir.
        

## 5. İzleme, Kalite ve Kontrol (Governance Layer)

-   **`quality_gate.py` (Data Quality Guard):**
    
    -   **Reliability:** ML eğitimi öncesinde negatif fiyatlar veya bozuk zaman damgaları gibi "kirli verileri" filtreler.
        
-   **`Home.py` & Dashboard Ecosystem (Control Plane):**
    
    -   **Infrastructure Telemetry:** Sunucu kaynaklarını ve konteyner durumlarını canlı izleyerek sistemin operasyonel sağlığını yönetir.
      

Aşağıdaki metin, paylaştığın teknik detayları profesyonel bir GitHub `README.md` formatına dönüştürülmüş halidir. Bu yapıyı doğrudan kopyalayıp dosyana yapıştırabilirsin.

----------

## 🛠️ Setup & Operations Guide (DevOps Command Center)

RadarPro ekosistemi, kurumsal veri platformu standartlarında, 17+ mikroservisin Docker üzerinde orkestre edilmesiyle çalışır. Sistemin kurulumu, veri toplama süreçleri ve otonom döngüleri aşağıda adım adım açıklanmıştır.

## 1. Pre-Deployment: System Optimization (WSL2 & RAM)

Sistemi çalıştırmadan önce, Docker'ın (özellikle Windows/WSL2 üzerinde) kaynakları verimli kullanması için şu optimizasyonu manuel olarak veya `start_windows.bat` üzerinden yapmalısınız:

-   **Windows Kullanıcıları:** `%USERPROFILE%\.wslconfig` dosyasını şu şekilde yapılandırın:
    

Ini, TOML

```
[wsl2]
memory=8GB        # Spark ve Kafka için optimize edilmiş limit
processors=2      # İşlemci çekirdek sayısı
swap=4GB          # M2-SSD tabanlı sanal bellek
autoMemoryReclaim=dropcache

```

> **Not:** Yapılandırmadan sonra terminalde `wsl --shutdown` komutu ile motoru yeniden başlatın.

----------

## 2. Infrastructure Deployment (Initial Start)

Tüm altyapıyı (Kafka, Spark, MLflow, MinIO, Postgres, Redis vb.) inşa etmek ve servisleri arka planda (detached) başlatmak için:

Bash

```
docker-compose up -d --build

```

**Önemli:** Bu aşamada 17 servis izole bir `data-network` ağında birbirine bağlanır. `db-init` servisi, Postgres'in hazır olmasını bekler ve tabloları otomatik olarak kurmaya başlar.

----------

## 3. Database Schema Provisioning (V13 God Mode)

Sistem ayağa kalktığında `db-init` konteyneri aşağıdaki tabloları ve **TimescaleDB Hypertable** yapısını otomatik olarak kurar. Manuel müdahale gerekirse şu komutlar kullanılır:

#### A. Market Data & Hypertable Setup

SQL

```
-- TimescaleDB uzantısını etkinleştir ve hypertable oluştur
CREATE TABLE IF NOT EXISTS market_data (
    symbol VARCHAR(20), 
    average_price DOUBLE PRECISION, 
    predicted_price DOUBLE PRECISION,
    volatility DOUBLE PRECISION, 
    volume_usd DOUBLE PRECISION, 
    trade_side VARCHAR(10),
    vpin_score DOUBLE PRECISION, 
    processed_time TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

SELECT create_hypertable('market_data', 'processed_time', if_not_exists => TRUE);

```

#### B. API Users & DaaS Security Table

SQL

```
-- Müşteri ve API anahtar yönetim tablosu
CREATE TABLE IF NOT EXISTS api_users (
    id SERIAL PRIMARY KEY, 
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL, 
    api_key VARCHAR(64) UNIQUE NOT NULL,
    tier VARCHAR(20) DEFAULT 'FREE', 
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

```

----------

## 4. Data Ingestion & ETL Operations

-   **Historical Data ETL (yFinance):** Son 10 yıllık borsa verilerini Delta Lake'e (MinIO) indirir.
    
    Bash
    
    ```
    docker exec -it spark-silver python /app/batch_yfinance_etl.py
    
    ```
    
-   **Universal Data Ingestion:** IoT ve genel veri tiplerini simüle etmek için kullanılır.
    
    Bash
    
    ```
    docker exec -it spark-silver python test_generic.py
    
    ```
    
-   **B2B API Simulation:** Harici bir kaynaktan API yoluyla veri girişi simüle eder.
    
    Bash
    
    ```
    python fake_company.py
    
    ```
    

----------

## 5. MLOps: Continuous Training & Hot-Reload

-   **Full AutoML Engine:** Tüm coinler için en iyi modeli (XGBoost/LightGBM) yarıştırır ve MLflow'a kaydeder.
    
    Bash
    
    ```
    docker exec -it spark-silver python /app/train_model.py ALL
    
    ```
    
-   **ML Watcher (CD Pipeline):** Veri biriktikçe eğitimi başlatır ve **Redis Pub/Sub** üzerinden canlı API'ye `RELOAD_MODELS` sinyali gönderir.
    
    Bash
    
    ```
    docker exec -d spark-silver python /app/ml_watcher.py
    
    ```
    
-   **Data Quality Gate:** Kirli verileri (negatif fiyatlar, null değerler) tarar.
    
    Bash
    
    ```
    docker exec -it spark-silver python quality_gate.py
    
    ```
    

----------

## 6. Service Management & Maintenance

-   **Hot Reload (Update):** Kod değişikliği sonrası servisi kapatmadan güncelleme:
    
    Bash
    
    ```
    docker-compose up -d --build dashboard
    
    ```
    
-   **Redis Cache Flush:** Tüm API limitlerini ve önbelleği sıfırlamak için:
    
    Bash
    
    ```
    docker-compose exec redis redis-cli flushall
    
    ```
    
-   **Data Lake Cleanup:** Delta Lake katmanlarını temizlemek için:
    
    Bash
    
    ```
    docker exec -it minio mc rm -r --force s3/market-data/raw_layer_delta
    ```

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



Bu bölüm, RadarPro’nun teknik olgunluğunu ve bir hobi projesinden profesyonel bir **Data-as-a-Service (DaaS)** platformuna dönüşümünü kanıtlayan en kritik kısımdır. Senior bir bakış açısıyla, buradaki maddeleri kurumsal veri yönetişimi (Data Governance) ve modern ön yüz mimarisi standartlarına göre güncelledim.

----------

## ⚡ Enterprise-Grade Data Governance & Platform Features

RadarPro, v6.0 sürümü ile birlikte veri yönetişimi ve operasyonel verimlilik konularında endüstriyel standartlara ulaşmıştır. Bu özellikler, platformun ticari bir veri sağlayıcısı olarak ölçeklenmesini sağlar:

## 1. 🧬 Generic Producer & Schema-Agnostic Ingestion

Sistemin veri giriş katmanı, katı şema zorunluluklarından arındırılarak **Schema-on-Read** prensibine taşınmıştır.

-   **Data Agnostic:** Sistem, JSON paketleri içerisindeki `data_type` etiketine göre veriyi otonom olarak sınıflandırır (Crypto, IoT, Web Log, Server Telemetry).
    
-   **Universal Carrier:** Kafka ve Bronze katmanı şemadan bağımsız birer taşıyıcı olarak konumlandırılmıştır; bu sayede yeni bir veri kaynağı eklemek için merkezi kod tabanında değişiklik yapılmasına gerek duyulmaz.
    

## 2. 🗄️ Multi-Tenant Data Lake Architecture (Partitioning)

MinIO (S3) üzerindeki Delta Lake katmanı, yüksek performanslı analitik sorgular için **Multi-tenant** yapısına uygun olarak bölümlenmiştir:

-   **Dynamic Partitioning:** Veriler; kaynağına, varlık sembolüne ve zaman damgasına (yıl) göre otomatik olarak dizinlenir (Örn: `source=binance/symbol=BTCUSDT/year=2026/`).
    
-   **I/O Optimization:** Spark motoru, 10 yıllık bir arşiv içerisinde arama yaparken "Partition Pruning" tekniği sayesinde sadece ilgili bölüme odaklanır ve sorgu performansını %80 artırır.
    

## 3. 🛡️ Autonomous Lakehouse Maintenance (Self-Healing)

Büyük veri sistemlerinin kronik sorunu olan "küçük dosya problemi" (Small File Problem), otonom bakım görevleriyle çözülmüştür:

-   **Optimize:** S3 üzerindeki parçalı binlerce küçük dosya, arka planda birleştirilerek tek bir optimize edilmiş Parquet dosyasına dönüştürülür.
    
-   **Vacuum:** Delta Lake günlüklerindeki geçersiz veri sürümleri temizlenerek depolama maliyetleri düşürülür ve veri gölünde "Storage Leak" oluşması engellenir.
    

## 🔒 4. Enterprise Rate Limiting & Security Gateway

Dış dünyaya açık API katmanı, kurumsal sınıf koruma ve yetkilendirme katmanlarıyla güçlendirilmiştir:

-   **Distributed Rate Limiter:** Kullanıcıların abonelik seviyelerine (FREE/VIP) göre saniyelik istek sınırları Redis üzerinde atomik sayaçlarla yönetilir.
    
-   **Credential Vault:** Tüm API anahtarları PostgreSQL üzerinde güvenli bir şekilde saklanır ve WebSocket bağlantılarında milisaniyelik yetkilendirme (auth) kontrolleri yapılır.
    

----------

## 🎨 Frontend Ecosystem & Client-Side Architecture

RadarPro, düşük gecikmeli (low-latency) veri akışlarını görselleştirmek için optimize edilmiş hibrit bir arayüz ekosistemine sahiptir.

## 1. Teknolojik Altyapı (Tech Stack)

-   **Lightweight Charts (TradingView):** Milisaniyelik fiyat hareketlerini tarayıcıyı yormadan render eden yüksek performanslı grafik motoru.
    
-   **Electron.js:** Web teknolojilerini yerel bir masaüstü uygulamasına dönüştüren ve CORS kısıtlamalarını aşarak API ile doğrudan haberleşen "Desktop Wrapper" katmanı.
    
-   **WebSockets & Redis Pub/Sub:** VIP kullanıcılar için saniyelik veri akışı ve anlık model güncelleme bildirimleri.
    

## 2. Modüler Sayfa Yapısı ve İşlevsellik

#### 🏛️ Pro Terminal (Institutional Dashboard)

-   **Fonksiyon:** 25 farklı varlığın canlı fiyatlarını, teknik indikatörlerini ve yapay zeka (AI) fiyat tahminlerini tek ekranda sunan ana merkezdir.
    
-   **Öne Çıkan Özellik:** Veri hattından gelen "Predicted Price" verisini canlı grafiğe bir "Gölge Fiyat" olarak işleyerek trader'lara görsel rehberlik sağlar.
    

#### 🔍 Asset Intelligence (L1 Detail)

-   **Order Book (L1):** Alıcı ve satıcı dengesini (Bids/Asks) milisaniyelik hassasiyetle görselleştirir.
    
-   **Technical Integration:** Gelişmiş teknik analiz araçlarıyla tam entegre çalışarak derinlemesine varlık incelemesi sunar.
    

----------

## 🖥️ Masaüstü Uygulaması (Electron Desktop App)

RadarPro, profesyonel kullanıcıların tarayıcı sekmeleri arasında kaybolmasını önlemek için bağımsız bir uygulama olarak paketlenmiştir:

-   **Web Security Bypass:**  `webSecurity: false` konfigürasyonu ile yerel ağdaki API ve Kafka kaynaklarına hiçbir tarayıcı engeli (CORS) olmadan en yüksek hızda bağlanır.
    
-   **Native Experience:** Tam ekran terminal deneyimi için optimize edilmiş bir kullanıcı arayüzü sunar.
    

----------

## 🤝 Katkıda Bulunun (Contributing)

Bu proje, bir **Yönetim Bilişim Sistemleri (YBS)** öğrencisi tarafından geliştirilmiş, akademik disiplin ile mühendislik pratiğini birleştiren açık kaynaklı bir platformdur. Bitirme tezi kapsamında geliştirilen bu yapının büyümesi için her türlü katkıya açığız.

-   **Geliştirici:** Ömer Çakan
    
-   **LinkedIn:** [Ömer Çakan - Profiline Git](https://www.google.com/search?q=https://www.linkedin.com/in/%25C3%25B6mer-%2525C3%2525A7akan-819751261)
    
-   **Destek:** Eğer bu proje size veri mühendisliği yolculuğunuzda ilham verdiyse, lütfen bir ⭐ bırakmayı unutmayın!
    
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
