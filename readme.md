
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



### 🌟 Sistemin Öne Çıkan Özellikleri

-   **🏛️ Lambda Mimarisi & Data Lakehouse:** Gerçek zamanlı akış katmanı (Kafka/Spark) ile yığın (Batch) katmanı (yFinance/Delta Lake) tek bir hibrit ekosistemde birleştirilmiştir. Geçmiş veriler MinIO üzerinde **Rust tabanlı `deltalake`** motoruyla sembol ve zaman bazlı bölümlenerek (partitioning) ultra hızlı sorgulanabilir halde saklanır.
    
-   **🚀 Toplu Çıkarım (Batch Inference) & Kaynak Optimizasyonu:** Spark motoru, tahmin isteklerini API'ye satır satır göndermek yerine vektörel olarak tek bir JSON paketi halinde iletir. Bu "kargo paketi" yaklaşımı, Network I/O darboğazını %99 oranında azaltarak sistemin toplam RAM tüketimini **1 GB seviyesinde** stabilize etmiştir.
    
-   **⚡ Dual-Track UI (Fast vs. Slow Path):** Kullanıcı deneyimi için "Çift Kanallı" veri yolu kurgulanmıştır. Dashboard üzerindeki canlı fiyatlar doğrudan **Kafka'dan (Fast Path)** milisaniyeler içinde okunurken, ağır teknik indikatörler ve AI tahminleri PostgreSQL'den (Slow Path) 5 saniyelik optimize edilmiş cache ile beslenir.
    
-   **🧠 Gerçek Gelecek Tahmini (Data Leakage Fix):** Finansal modellemedeki en büyük risk olan "zaman sızıntısı" problemi; hedef değişkenin zamansal kaydırma tekniğiyle bir sonraki periyoda aktarılmasıyla çözülmüş, makine öğrenmesinin gerçek geleceği öğrenmesi sağlanmıştır.
    
-   **🔄 Zero-Downtime MLOps (Hot-Reload):** "ML Watcher" modülü, Lakehouse üzerindeki veri hacmini izleyerek otonom eğitimi tetikler. Yeni modeller MLflow'a kaydedilir ve canlıdaki API'ye gönderilen bir sinyal ile sistem kapatılmadan (hot-reload) yeni modeller anında devreye alınır.
    
-   **🐳 %100 Mikroservis ve Konteynerizasyon:** Sistem, birbirine tam entegre çalışan **17+ mikroservisten** oluşur. Windows kullanıcıları için özel geliştirilen **DevOps Command Center (.bat)** sayesinde tüm altyapı tek tuşla optimize edilip yönetilebilir.

<img width="2816" height="1536" alt="Architecture" src="https://github.com/user-attachments/assets/0d3cabf3-f35d-4d77-ad85-a01477a16265" />

---

## 📂 Proje Yapısı

```text
├── dashboard_app/              # Streamlit Multi-Page Kullanıcı Arayüzü
│   ├── Home.py                 # Ana Komuta Merkezi
│   ├── utils.py                # CSS ve Veritabanı/S3 Cache Ayarları
│   ├── _Canli_Piyasa.py        # Canlı Fiyat ve İndikatör Takibi
│   ├── Gecmis_Analiz.py        # Geçmiş Veri (CSV) Upload Modülü
│   ├── _Harici_Baglanti.py     # Universal Data Gateway Arayüzü
│   ├── _MLOps_Center.py        # MLflow AutoML Liderlik Tablosu
│   ├── _Sistem_Yonetimi.py     # Enterprise Control Plane & Log İzleme
│   └── KAFDROP.py              # Kafka Universal Data Deck
├── dbt_project/                # Veri Dönüşüm Katmanı (DBT)
├── start_windows.bat           # Windows DevOps Command Center (Otomasyon)
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
├── inference_api.py           	#FastAPI MaaS (Model-as-a-Service) Çıkarım Motoru
├── batch_user_processor.py     # Yfinance Toplu Veri İşleme Motoru
├── train_model.py              # Scikit-Learn + Pandas AutoML Eğitim Fabrikası
├── ml_watcher.py               # Otonom Model Tetikleyici & Hot Reload (CD)
├── quality_gate.py             # Veri Kalite ve Sağlık Kapısı (Data Guard)
└── prometheus.yml              # Altyapı İzleme Konfigürasyonu
```



## 🏗️ Mimari Tasarım (Architecture)

Sistem, yüksek hacimli veri akışlarını yönetmek için **Lambda Mimarisi** prensiplerine göre tasarlanmış olup, her bir modül spesifik bir mühendislik darboğazını (bottleneck) aşmak üzere optimize edilmiştir:

#### 1. Veri Girişi ve Mesajlaşma (Ingestion Layer)

-   **`producer.py` (Multi-Stream Binance Connector):**
    
    -   **Multi-Stream Support:** Tek bir bağlantı üzerinden 10+ farklı varlığın (`btcusdt`, `ethusdt`, vb.) eşzamanlı takibini yapar.
        
    -   **Heartbeat & Resilience:** Ağ kopmalarına karşı `ping_interval=70` ve `ping_timeout=10` konfigürasyonuyla WebSocket bağlantısının sürekliliği garanti altına alınmıştır.
        
    -   **Kafka Efficiency:** Veri paketleri `gzip` ile sıkıştırılarak iletilir; `acks=1` ve `retries=5` ayarları ile hız ve veri güvenliği arasında optimum denge kurulmuştur.
        

#### 2. Veri İşleme ve Lakehouse Katmanları (Processing & Storage)

-   **`consumer_lake.py` (Bronze Layer):**
    
    -   **Schema Agnostic Recording:** Kafka'daki veriyi ham haliyle (raw) Delta Lake formatında MinIO'ya yazar.
        
    -   **Backpressure Control:** `maxOffsetsPerTrigger=1000` parametresi ile ani veri patlamalarında sistemin aşırı yüklenmesi (spike) önlenir.
        
-   **`process_silver.py` (Batch-Inference Spark Engine):**
    
    -   **Vectorized Inference:** Saniyeler içinde biriken veriler `iterrows` gibi yavaş döngüler yerine toplu bir JSON paketi (Batch) haline getirilerek API'ye fırlatılır.
        
    -   **Network I/O Optimization:** Bu mimari, ağ üzerindeki HTTP isteği sayısını %99 azaltarak ağ gecikmesini minimize eder ve RAM tüketimini stabilize eder.
        
    -   **Polyglot Persistence:** İşlenmiş veriler hem analitik sorgular için **Delta Lake**'e (MinIO) hem de canlı dashboard beslemesi için **TimescaleDB**'ye (PostgreSQL) eşzamanlı yazılır.
        
-   **`batch_yfinance_etl.py` (Batch Layer / Rust-Powered):**
    
    -   **Historical Ingestion:** 10 yıllık ve 2 yıllık geçmiş verileri Spark maliyetine girmeden doğrudan Rust tabanlı `deltalake` motoruyla S3 üzerine aktarır.
        
    -   **Partitioning Strategy:** Veriler `symbol` ve `year` bazlı bölümlenerek (partitioned), gelecekteki analizlerde sadece ilgili dosyaların taranması (Predicate Pushdown) sağlanır.
        

#### 3. Çıkarım ve Otonom MLOps (Inference & AI Orchestration)

-   **`inference_api.py` (FastAPI MaaS Engine):**
    
    -   **Batch Prediction Support:** Tek bir istek içinde gelen çok sayıda satırı Pandas vektörel gücüyle milisaniyeler içinde tahminler.
        
    -   **Model Caching:** En son "Production" etiketli modeli MLflow'dan çekerek RAM'de hazır bekletir.
        
-   **`ml_watcher.py` (CD Orchestrator):**
    
    -   **Zero-Downtime Hot Reload:** Yeni model eğitildiğinde API'ye `/reload` sinyali göndererek sistem kapatılmadan yeni modelin devreye alınmasını sağlar.
        
-   **`train_model.py` (AutoML Factory):**
    
    -   **Data Leakage Fix:** Hedef değişken zamansal olarak kaydırılarak (`shift(-1)`) modelin "geçmişe bakarak geleceği tahmin etmesi" garanti edilir.
        

#### 4. Sunum ve İzleme (Serving & Observability)

-   **`_Canli_Piyasa.py` (Dual-Track UI):**
    
    -   **Fast Path (Kafka):** Canlı fiyatlar doğrudan Kafka kuyruğundan okunarak saniyede bir güncellenir.
        
    -   **Slow Path (PostgreSQL):** AI tahminleri ve teknik analiz grafikleri veritabanından 5 saniyelik cache ile beslenir.
        
    -   **Session State:** Kullanıcı seçimleri (coin seçimi vb.) sayfa yenilenmelerinde hafızada tutulur.
        
-   **`start_windows.bat` (DevOps Control Plane):**
    
    -   **Orchestration:** 19 farklı operasyonel komutu (build, train, log izleme, data clean) tek merkezden yöneten interaktif komuta merkezidir.

## 🛠️ Kurulum ve Operasyonel Yönetim (DevOps Command Center)

Sistemin tüm yaşam döngüsü, mikroservis mimarisinin gerektirdiği izolasyon ve ölçeklenebilirlik prensiplerine uygun olarak **Docker** üzerinde kurgulanmıştır. Karmaşık konteyner ağını yönetmek için hem otomatize edilmiş scriptler hem de manuel terminal komutları optimize edilmiştir.

----------

### 🪟 Windows Ortamı (Otomatik Orkestrasyon)

Windows kullanıcıları için tüm operasyonel süreci tek bir merkezden yöneten **`start_windows.bat`** DevOps komuta merkezini hazırladım. Bu araç sadece bir başlatıcı değil, aynı zamanda bir altyapı optimizasyon servisidir:

1.  **WSL2 Altyapı Optimizasyonu:** Sistem, `.wslconfig` dosyasını otomatik olarak yapılandırarak Docker motoru için **8GB RAM** ve **4 Çekirdek** ataması yapar; böylece ağır Spark iş yükleri için donanımı stabilize eder.
    
2.  **Bütünsel Yaşam Döngüsü Yönetimi:** İnteraktif menü üzerinden sistemi başlatma, durdurma, log izleme ve model eğitimi gibi **19 farklı kritik operasyonu** tek tuşla gerçekleştirmenizi sağlar.
    
3.  **Hızlı Erişim:** Ana dizindeki `start_windows.bat` dosyasına çift tıklayarak tüm Lakehouse ekosistemini saniyeler içinde ayağa kaldırabilirsiniz.
    

----------

### 🐧 Linux / Mac ve Manuel Terminal Yönetimi

Konteynerler üzerinde tam granüler kontrol sağlamak isteyen profesyoneller için temel yaşam döngüsü komutları aşağıda kategorize edilmiştir:

#### 🟢 1. Servis Orkestrasyonu ve Altyapı Döngüsü

-   **Ekosistemi Başlat (Up):** Tüm 17+ servisi (Kafka, Spark, MinIO, vb.) asenkron olarak ayağa kaldırır.
    
    Bash
    
    ```
    docker-compose up -d
    
    ```
    
-   **Servisleri Durdur (Stop):** Veri bütünlüğünü bozmadan konteynerleri uyku moduna alır.
    
    Bash
    
    ```
    docker-compose stop
    
    ```
    
-   **Sistemi Fabrika Ayarlarına Döndür (Hard Reset):** ⚠️ **KRİTİK:** Tüm veritabanı hacimlerini (Volumes), MinIO arşivini ve Kafka kuyruklarını kalıcı olarak siler.
    
    Bash
    
    ```
    docker-compose down -v
    
    ```
    
-   **Altyapı Sağlık Denetimi (Health Check):** Çalışan servislerin durumunu ve port eşleşmelerini listeleyerek sistemi doğrular.
    
    Bash
    
    ```
    docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
    
    ```
    

#### 🔄 2. Hot-Reload (Sıfır Kesinti ile Güncelleme)

Kod tabanında yapılan değişiklikleri sisteme yansıtmak için tüm yapıyı kapatmaya gerek yoktur. Hedeflenen servisi yeniden derlemek için şu komutlar kullanılır:

-   **Arayüzü Güncelle:** `docker-compose up -d --build dashboard`
    
-   **AI Motorunu Güncelle:** `docker-compose up -d --build spark-silver`
    
-   **Producer Katmanını Güncelle:** `docker-compose up -d --build producer`
    

#### 🧠 3. MLOps ve DataOps Yönetimi

-   **Toplu Model Eğitimi (AutoML):** Lakehouse üzerindeki tüm verileri kullanarak modelleri rekabete sokar.
    
    Bash
    
    ```
    docker exec -it spark-silver python /app/train_model.py ALL
    
    ```
    
-   **Otonom ML Watcher:** Veri biriktikçe eğitimi arka planda otomatik tetikler.
    
    Bash
    
    ```
    docker exec -d spark-silver python /app/ml_watcher.py
    
    ```
    
-   **Lambda Batch ETL:** 10 yıllık ve 2 yıllık geçmiş veriyi Data Lake'e (MinIO) tek hamlede transfer eder.
    
    Bash
    
    ```
    docker exec -it spark-silver python /app/batch_yfinance_etl.py
    
    ```
    
-   **Veri Temizliği (Cleanse):** Postgres tablolarını veya MinIO Delta klasörlerini temizleyerek sistemi yeni testlere hazırlar.
    

#### 📋 4. İzlenebilirlik ve Metrikler (Observability)

-   **Canlı Log Akışı:** Hata ayıklama için servisin iç loglarını canlı izler.
    
    Bash
    
    ```
    docker logs --tail 50 -f [servis_adi]
    
    ```
    
-   **Kaynak Tüketimi (Resource Monitor):** Konteyner bazlı anlık CPU, RAM ve Ağ trafiklerini izleyerek darboğazları tespit eder.
    
    Bash
    
    ```
    docker stats
    
    ```
    

> **Not:** Sistemin ilk kurulumunda `db-init` servisi, PostgreSQL üzerinde gerekli TimescaleDB hiper-tablolarını ve şemalarını otomatik olarak kurgular.

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


## ⚡ "Enterprise-Grade" Yeni Özellikler

Bu sürümle birlikte sistem, akademik bir projeden endüstriyel standartlarda bir **Data & MLOps Framework**'üne dönüştürülmüştür:

-   **🏛️ Lambda Mimarisi (Batch + Speed Layer):** Sistem, saniyelik akan veriyi (Speed Layer) işlerken aynı zamanda 10 yıllık devasa geçmiş verileri (Batch Layer) analiz edebilecek hibrit bir yapıya kavuşturulmuştur.
    
-   **📦 Vektörel Toplu Çıkarım (Batch Inference):** Spark Streaming motoru, tahmin için API'ye her satır için ayrı istek atmak yerine verileri JSON paketleri halinde "koliyle" gönderir. Bu sayede Network I/O darboğazı giderilmiş ve RAM kullanımı **1 GB** seviyesinde sabitlenmiştir.
    
-   **⚡ Dual-Track UI (Fast Path / Slow Path):** Dashboard mimarisi ikiye bölünmüştür; anlık fiyatlar PostgreSQL'i pas geçerek doğrudan **Kafka'dan** milisaniyeler içinde okunurken, AI tahminleri ve teknik analizler DB'den 5 saniyelik cache ile beslenir.
    
-   **🦀 Rust Tabanlı Delta Lake Ingestion:** 100.000+ satırlık geçmiş veriler, JVM maliyetine girilmeden doğrudan **Rust tabanlı `deltalake`** motoruyla MinIO'ya (S3) aktarılır. Veriler `symbol` ve `year` bazlı bölümlenerek (partitioned) depolanır.
    
-   **🎯 Predicate Pushdown Optimizasyonu:** Geçmiş analiz modülünde S3 üzerindeki tüm veri taranmaz; sorgu anında sadece ilgili yılın ve coinin klasörü okunarak (Pushdown) devasa veriler milisaniyeler içinde RAM'e alınır.
    
-   **🛡️ Otonom Bakım (DataOps):** Delta Lake üzerindeki küçük parçalı dosyaların birleştirilmesi (Optimize) ve atık verilerin temizlenmesi (Vacuum) işlemleri Streamlit yönetim panelinden tek tuşla tetiklenebilir.
    

----------

## 🤝 Katkıda Bulunun (Contributing)

Bu proje bir **YBS öğrencisi** tarafından geliştirilmiş, kurumsal veri mimarilerini demokratikleştirmeyi hedefleyen açık kaynaklı bir framework'tür. Her türlü fikir, hata raporu ve PR (Pull Request) değerlidir.

-   **Geliştirici:** Ömer Çakan
    
-   **LinkedIn:** [Ömer Çakan - Profil Linki](https://www.google.com/search?q=https://www.linkedin.com/in/%25C3%25B6mer-%25C3%25C3akan-819751261)
    
-   **Destek:** Eğer bu altyapı size yardımcı olduysa depoya bir ⭐ bırakarak destek olabilirsiniz!
    

### 🛠️ Geliştirici Talimatları

Kendi özelliklerinizi eklemek için aşağıdaki iş akışını takip edebilirsiniz:

1.  **Projeyi Forklayın:** Repository'yi kendi hesabınıza kopyalayın.
    
2.  **Branch Oluşturun:** `main` branch'ine dokunmadan yeni bir çalışma alanı açın:
    
    Bash
    
    ```
    git checkout -b dev/isminiz_ve_ozellik
    
    ```
    
3.  **Test Edin:** Değişikliklerinizi `start_windows.bat` üzerindeki **[15] Canlı Logları İzle** ve **[4] Sağlık Durumu** seçenekleriyle mutlaka test edin.
    
4.  **Push ve PR:** Geliştirmenizi pushlayın ve bir Pull Request oluşturun.

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
