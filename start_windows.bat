@echo off
TITLE RADARPRO TITAN - KONTROL MERKEZI

:MENU
cls
color 0B
echo ************************************************************
echo   RADARPRO TITAN - KURUMSAL KONTROL MERKEZI v3.0
echo ************************************************************
echo.
echo   1. SISTEMI BASLAT (Full Rebuild)
echo   2. CANLI ARBITRAJ TERMINALI (Live Data)
echo   3. AI PIYASA RAPORU (Gemini Analysis)
echo   4. WEB DASHBOARD AC (Streamlit)
echo   5. SISTEM LOGLARINI IZLE (Live Logs)
echo   6. SISTEMI DURDUR (Clean Stop)
echo   7. STANDALONE TRADING BOTU BASLAT (Auto Trade)
echo   8. ULTRA-FAST HFT BOT (WebSocket - Milliseconds)
echo   9. GRAND INTELLIGENCE DASHBOARD AC (Web UI)
echo.
echo   X. CIKIS
echo.
echo ************************************************************
set "choice="
set /p "choice=Seciminizi yapin (1-9): "

if "%choice%"=="1" goto START_SYSTEM
if "%choice%"=="2" goto LIVE_DATA
if "%choice%"=="3" goto AI_REPORT
if "%choice%"=="4" goto OPEN_WEB
if "%choice%"=="5" goto SHOW_LOGS
if "%choice%"=="6" goto STOP_SYSTEM
if "%choice%"=="7" goto START_BOT
if "%choice%"=="8" goto START_HFT
if "%choice%"=="9" goto OPEN_DASHBOARD
if /i "%choice%"=="X" exit
goto MENU

:OPEN_DASHBOARD
echo.
echo 💎 RadarPro Tactical Terminal Aciliyor...
start http://localhost:8000/dashboard
goto MENU

:START_SYSTEM
echo.
echo Temizlik yapiliyor...
docker rm -f zookeeper kafka redis_cache postgres api_gateway binance_producer radar_ai_agent arbitrage_scanner telegram_bot webhook_gateway
echo Sistem yukleniyor...
docker-compose up --build -d
echo Islem tamam.
pause
goto MENU

:LIVE_DATA
echo.
echo Canli Veri Akisi (Docker uzerinden)...
docker-compose exec api-gateway python terminal_dashboard.py
pause
goto MENU

:AI_REPORT
echo.
echo Gemini AI Raporu...
docker-compose exec api-gateway python -c "import redis,json; r=redis.Redis(host='redis_cache', decode_responses=True); report=r.get('ai_last_report'); print(json.loads(report)['content'] if report else 'Henuz rapor yok.')"
pause
goto MENU

:OPEN_WEB
start http://localhost:8501
goto MENU

:SHOW_LOGS
docker-compose logs -f telegram-bot arbitrage-scanner radar-ai-agent
goto MENU

:STOP_SYSTEM
docker-compose down
pause
goto MENU

:START_BOT
echo.
echo 🤖 Standalone Trading Bot Baslatiliyor (Docker uzerinden)...
docker-compose exec api-gateway python radarpro_executor.py
pause
goto MENU

:START_HFT
echo.
echo 🏎️ Ultra-Fast HFT Engine Baslatiliyor (WebSocket)...
docker-compose exec api-gateway python radarpro_hft.py
pause
goto MENU