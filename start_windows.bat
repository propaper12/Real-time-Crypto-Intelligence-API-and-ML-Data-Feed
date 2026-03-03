@echo off
title Financial Lakehouse - Command Center
color 0B
chcp 65001 >nul

:: Dosyanin calistigi dizini her ihtimale karsi ana dizine sabitler
cd /d "%~dp0"

:: --- 1. WSL RAM OPTIMIZASYONU ---
set WSL_CONFIG="%USERPROFILE%\.wslconfig"
if not exist %WSL_CONFIG% (
    echo [ ⚙️ PROCESS ] Sisteminiz icin optimum RAM ayarlari yapiliyor...
    echo [wsl2] > %WSL_CONFIG%
    echo memory=8GB >> %WSL_CONFIG%
    echo processors=4 >> %WSL_CONFIG%
    echo swap=2GB >> %WSL_CONFIG%
    wsl --shutdown
    timeout /t 3 >nul
)

:MENU
cls
echo.
echo  ███████████████████████████████████████████████████████████████████████████
echo  █                                                                         █
echo  █                 F I N A N C I A L   L A K E H O U S E                   █
echo  █                 D e v O p s   C o m m a n d   C e n t e r               █
echo  █                                                                         █
echo  ███████████████████████████████████████████████████████████████████████████
echo.
echo  ╔══════════════════════════════════════╦══════════════════════════════════╗
echo  ║  ⚙️ ALTYAPI KONTROLU                 ║  🔄 HOT RELOAD (GUNCELLEME)      ║
echo  ╠══════════════════════════════════════╬══════════════════════════════════╣
echo  ║  [1] 🟢 Sistemi Baslat (Up)          ║  [5] 🎨 Arayuz (Dashboard)       ║
echo  ║  [2] 🔴 Sistemi Durdur (Stop)        ║  [6] 🧠 AI Motoru (Silver)       ║
echo  ║  [3] ⚠️  Sistemi Sifirla (Down -v)   ║  [7] 📥 Veri Toplayici (Bronze)  ║
echo  ║  [4] 🩺 Saglik Durumu (Health)       ║  [8] 📡 Veri Uretici (Producer)  ║
echo  ║                                      ║  [9] ⚡ TUMUNU GUNCELLE          ║
echo  ╠══════════════════════════════════════╬══════════════════════════════════╣
echo  ║  🤖 MLOps VE YAPAY ZEKA              ║  🛠️ ARACLAR VE RAPORLAMA         ║
echo  ╠══════════════════════════════════════╬══════════════════════════════════╣
echo  ║  [10] 🎯 Toplu Model Egitimi (Tumu)  ║  [15] 📋 Canli Loglari Izle      ║
echo  ║  [11] 🧪 Spesifik Coin Egitimi       ║  [16] 🔗 Sistem Portallari / UI  ║
echo  ║  [12] 👁️ ML Watcher'i Baslat         ║  [17] 📊 CPU/RAM/Network Izle    ║
echo  ║  [13] 🧹 Postgres Temizle (Gold)     ║  [18] 🚪 Sistemden Cikis         ║
echo  ║  [14] 🗑️  MinIO Temizle (Delta)      ║  [19] ⏳ Gecmis Veri (2Y ve 10Y) ║
echo  ╚══════════════════════════════════════╩══════════════════════════════════╝
echo.
set /p secim="  [root@lakehouse]~# Komut Girin (1-19): "

if "%secim%"=="1" goto START_SYS
if "%secim%"=="2" goto STOP_SYS
if "%secim%"=="3" goto RESET_SYS
if "%secim%"=="4" goto HEALTH_CHECK

if "%secim%"=="5" goto UPDATE_UI
if "%secim%"=="6" goto UPDATE_AI
if "%secim%"=="7" goto UPDATE_BRONZE
if "%secim%"=="8" goto UPDATE_PRODUCER
if "%secim%"=="9" goto UPDATE_ALL

if "%secim%"=="10" goto TRAIN_ALL
if "%secim%"=="11" goto TRAIN_SINGLE
if "%secim%"=="12" goto START_WATCHER

if "%secim%"=="13" goto CLEAN_POSTGRES
if "%secim%"=="14" goto CLEAN_MINIO

if "%secim%"=="15" goto READ_LOGS
if "%secim%"=="16" goto LINKS
if "%secim%"=="17" goto RESOURCE_MONITOR
if "%secim%"=="18" exit
if "%secim%"=="19" goto FETCH_HISTORY

goto MENU

:: --- SISTEM KOMUTLARI ---
:START_SYS
cls
echo.
echo  [ ⚙️ PROCESS ] Altyapi servisleri ayaga kaldiriliyor...
docker-compose up -d
echo.
pause
goto MENU

:STOP_SYS
cls
echo.
echo  [ ⚙️ PROCESS ] Konteynerler durduruluyor...
docker-compose stop
echo.
pause
goto MENU

:RESET_SYS
cls
color 0C
echo.
echo  ██ KRITIK UYARI: DB, Kafka ve MinIO tamamen SIFIRLANACAKTIR! ██
echo.
set /p onay="  [root@lakehouse]~# Onayliyor musunuz? (E/H): "
if /I "%onay%"=="E" (
    docker-compose down -v
    echo  [ 🟢 OK ] Sistem sifirlandi.
)
color 0B
pause
goto MENU

:HEALTH_CHECK
cls
echo.
echo  [ 🩺 HEALTH ] Konteyner Saglik Durumu
docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
echo.
pause
goto MENU

:: --- GUNCELLEME KOMUTLARI ---
:UPDATE_UI
cls
echo [ ⚙️ PROCESS ] Dashboard derleniyor...
docker-compose up -d --build dashboard
pause
goto MENU

:UPDATE_AI
cls
echo [ ⚙️ PROCESS ] AI Motoru derleniyor...
docker-compose up -d --build spark-silver
pause
goto MENU

:UPDATE_BRONZE
cls
echo [ ⚙️ PROCESS ] Veri Toplayici derleniyor...
docker-compose up -d --build spark-consumer
pause
goto MENU

:UPDATE_PRODUCER
cls
echo [ ⚙️ PROCESS ] Producer derleniyor...
docker-compose up -d --build producer
pause
goto MENU

:UPDATE_ALL
cls
echo [ ⚙️ PROCESS ] TUM SERVISLER DERLENIYOR...
docker-compose up -d --build dashboard spark-silver spark-consumer producer
pause
goto MENU

:: --- MLOps / DataOps KOMUTLARI ---
:TRAIN_ALL
cls
echo.
echo  [ 🤖 MLOps ] Enterprise AutoML Engine Baslatiliyor (TUM COINLER)...
echo  ──────────────────────────────────────────────────────────────────
docker exec -it spark-silver python /app/train_model.py ALL
pause
goto MENU

:TRAIN_SINGLE
cls
echo.
set /p coin_name="  Egitilecek Coini Yaziniz (Orn: BTCUSDT): "
docker exec -it spark-silver python /app/train_model.py %coin_name%
pause
goto MENU

:START_WATCHER
cls
echo.
echo  [ 👁️ MLOps ] ML Watcher Aktif Ediliyor...
docker exec -d spark-silver python /app/ml_watcher.py
echo  [ 🟢 OK ] Watcher arka planda sessizce calismaya basladi!
pause
goto MENU

:CLEAN_POSTGRES
cls
echo [ 🗄️ DataOps ] Postgres temizleniyor...
docker exec -it postgres psql -U admin_lakehouse -d market_db -c "TRUNCATE TABLE market_data;"
pause
goto MENU

:CLEAN_MINIO
cls
echo [ 🗄️ DataOps ] Delta Lake temizleniyor...
docker exec -it minio mc rm -r --force s3/market-data/raw_layer_delta s3/market-data/silver_layer_delta
pause
goto MENU

:: --- ARACLAR ---
:READ_LOGS
cls
echo.
echo  [ 📋 LOG PANELI ]
echo    [1] Dashboard          [3] Spark-Bronze
echo    [2] Spark-Silver       [4] Producer
echo.
set /p log_secim="  Seciminiz (1-4): "
if "%log_secim%"=="1" docker logs --tail 50 -f dashboard
if "%log_secim%"=="2" docker logs --tail 50 -f spark-silver
if "%log_secim%"=="3" docker logs --tail 50 -f spark-consumer
if "%log_secim%"=="4" docker logs --tail 50 -f producer
pause
goto MENU

:RESOURCE_MONITOR
cls
echo.
echo  [ 📊 METRICS ] Canli Sistem Kaynaklari (CPU / RAM / AĞ)
echo    CIKMAK ICIN "CTRL + C" BASIP "N" (Hayir) SECIN!
echo  ───────────────────────────────────────────────────────────────────────────
docker stats
goto MENU

:LINKS
cls
echo.
echo  [ 🔗 SISTEM LINKLERI ]
echo  📊 Dashboard: http://localhost:8501
echo  🗄️ MinIO: http://localhost:9001
echo  📨 Kafka: http://localhost:9010
echo.
pause
goto MENU

:FETCH_HISTORY
cls
echo.
echo  [ ⏳ BATCH ETL ] Yfinance uzerinden 2 Yillik (Saatlik) ve 10 Yillik (Gunluk) veriler cekiliyor...
echo  Bu islem internet hiziniza bagli olarak 1-2 dakika surebilir. Lutfen bekleyin...
echo  ──────────────────────────────────────────────────────────────────
docker exec -it spark-silver python /app/batch_yfinance_etl.py
echo.
pause
goto MENU
