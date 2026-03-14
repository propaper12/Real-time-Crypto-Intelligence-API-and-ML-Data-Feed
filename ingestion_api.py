import asyncio
import json
import os
import secrets
import time
import hmac
import hashlib
import xml.etree.ElementTree as ET
import redis.asyncio as aioredis
import requests
import asyncpg
import bcrypt
import yfinance as yf
import google.generativeai as genai
import aiohttp

from pydantic import BaseModel
from fastapi import FastAPI, HTTPException, Request, WebSocket, Security, Query
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security.api_key import APIKeyHeader
from aiokafka import AIOKafkaConsumer
from datetime import datetime, timedelta

# ==============================================================================
# 🚀 RADAR GLOBAL - ENTERPRISE DATA GATEWAY (V27 NEWS & PORTFOLIO + SETTINGS)
# ==============================================================================
app = FastAPI(
    title="Radar Global - Data Gateway",
    description="Enterprise Grade Async API with TimescaleDB, Arbitrage, News Scraper, Portfolio & Full Settings.",
    version="27.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"], 
    allow_headers=["*"],
)

KAFKA_SERVER = os.getenv('KAFKA_BOOTSTRAP_SERVERS', 'kafka:9092')
KAFKA_TOPIC = 'market_data'

API_KEY_NAME = "X-API-Key"
api_key_header = APIKeyHeader(name=API_KEY_NAME, auto_error=False)

def hash_password(password: str):
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')

def verify_password(plain_password: str, hashed_password: str):
    return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))

# ==============================================================================
# 📰 ADIM 3: ASENKRON HABER TARAYICI BOTU (RSS SCRAPER)
# ==============================================================================
async def news_scraper_task():
    """ Arka planda çalışır, kripto haberlerini okuyup Redis'e atar. """
    print("📰 Haber Botu Başlatıldı...")
    while True:
        try:
            # CoinTelegraph RSS'ini okuyoruz
            resp = requests.get("https://cointelegraph.com/rss", timeout=10)
            if resp.status_code == 200:
                root = ET.fromstring(resp.content)
                news_list = []
                for item in root.findall('./channel/item')[:5]: # En güncel 5 haber
                    news_list.append({
                        "title": item.find('title').text,
                        "date": item.find('pubDate').text,
                        "link": item.find('link').text
                    })
                
                if getattr(app.state, "redis", None):
                    await app.state.redis.set("LATEST_NEWS", json.dumps(news_list))
                    print("✅ Flaş Haberler Güncellendi!")
        except Exception as e:
            print(f"⚠️ Haber Çekilemedi: {e}")
        
        await asyncio.sleep(300) # Her 5 dakikada bir güncelle

# ==============================================================================
# 🗄️ BAŞLANGIÇ SİSTEMLERİ VE DB GÜNCELLEMELERİ
# ==============================================================================
@app.on_event("startup")
async def startup_event():
    print("🟢 [RADAR] Asenkron Sistemler Ayağa Kalkıyor...")
    for _ in range(5):
        try:
            app.state.db_pool = await asyncpg.create_pool(
                host=os.getenv("POSTGRES_HOST", "postgres"),
                database=os.getenv("POSTGRES_DB", "market_db"),
                user=os.getenv("POSTGRES_USER", "admin_lakehouse"),
                password=os.getenv("POSTGRES_PASSWORD", "SuperSecret_DB_Password_2026"),
                min_size=5, max_size=20 
            )
            print("🟢 PostgreSQL Connection Pool Aktif!")
            
            async with app.state.db_pool.acquire() as conn:
                # 1. TimescaleDB Kurulumu
                await conn.execute("CREATE EXTENSION IF NOT EXISTS timescaledb;")
                await conn.execute("""
                    CREATE TABLE IF NOT EXISTS market_data (
                        symbol VARCHAR(50), average_price DOUBLE PRECISION, volume_usd DOUBLE PRECISION,
                        is_buyer_maker BOOLEAN, trade_side VARCHAR(10), processed_time TIMESTAMP WITHOUT TIME ZONE NOT NULL,
                        volatility DOUBLE PRECISION, predicted_price DOUBLE PRECISION, cvd DOUBLE PRECISION,
                        buy_wall_usd DOUBLE PRECISION, sell_wall_usd DOUBLE PRECISION, imbalance_ratio DOUBLE PRECISION,
                        mark_price DOUBLE PRECISION, funding_rate DOUBLE PRECISION, liq_buy_usd DOUBLE PRECISION,
                        liq_sell_usd DOUBLE PRECISION, vpin_score DOUBLE PRECISION, wall_imbalance DOUBLE PRECISION
                    );
                """)
                try:
                    await conn.execute("SELECT create_hypertable('market_data', 'processed_time', if_not_exists => TRUE);")
                except: pass

                # 2. 💼 Kullanıcı Tablosuna Portföy Anahtarları İçin Sütun Ekle (Çökmeden)
                await conn.execute("ALTER TABLE api_users ADD COLUMN IF NOT EXISTS binance_key VARCHAR(255);")
                await conn.execute("ALTER TABLE api_users ADD COLUMN IF NOT EXISTS binance_secret VARCHAR(255);")
                print("✅ Veritabanı Şemaları Güncel!")
            break
        except Exception as e:
            print(f"⚠️ DB Bekleniyor... {e}")
            await asyncio.sleep(5)

    try:
        app.state.redis = await aioredis.from_url(f"redis://{os.getenv('REDIS_HOST', 'redis')}:6379", decode_responses=True)
        await app.state.redis.ping()
    except:
        app.state.redis = None

    asyncio.create_task(consume_kafka_and_broadcast())
    asyncio.create_task(news_scraper_task()) # 📰 Haber botunu başlat

@app.on_event("shutdown")
async def shutdown_event():
    if getattr(app.state, "db_pool", None): await app.state.db_pool.close()
    if getattr(app.state, "redis", None): await app.state.redis.close()

async def check_redis_limit(email: str, tier: str):
    r = app.state.redis
    if r is None: return
    if await r.get(f"ban:{email}"): raise HTTPException(status_code=403, detail="⛔ HESABINIZ KALICI OLARAK BANLANDI!")
    if tier == 'VIP':
        usage = await r.incr(f"rate:vip:{email}"); 
        if usage == 1: await r.expire(f"rate:vip:{email}", 1)
        if usage > 50: raise HTTPException(status_code=429, detail="🚨 VIP Sınırı: Saniyede 50 istek!")
        return 
    if tier == 'PREMIUM':
        usage = await r.incr(f"rate:premium:{email}")
        if usage == 1: await r.expire(f"rate:premium:{email}", 1)
        if usage > 10: raise HTTPException(status_code=429, detail="🚨 PREMIUM Sınırı: Saniyede 10 istek!")
        return
    if tier == 'FREE':
        today = datetime.now().strftime("%Y-%m-%d")
        limit_key = f"limit:free:{email}:{today}"
        usage = await r.incr(limit_key)
        if usage == 1: await r.expire(limit_key, 86400)
        if usage > 1000:
            await r.set(f"ban:{email}", "PERMANENT") 
            raise HTTPException(status_code=403, detail="⛔ GÜNLÜK 1000 İSTEK LİMİTİ AŞILDI.")

# ==============================================================================
# 🔐 AUTH & SETTINGS (EKSİKSİZ OLARAK GERİ GELDİ)
# ==============================================================================
class UserRegister(BaseModel): username: str; email: str; password: str
class UserLogin(BaseModel): email: str; password: str
class ProfileUpdate(BaseModel): username: str
class PasswordChange(BaseModel): current_password: str; new_password: str
class TierUpdate(BaseModel): email: str; new_tier: str

@app.post("/api/v1/auth/register")
async def register_user(user: UserRegister, request: Request):
    client_ip = request.client.host if request.client else "unknown"
    r = app.state.redis
    if r and int(await r.get(f"reg_ip:{client_ip}") or 0) >= 3: return {"status": "error", "message": "🚨 Spam Koruması."}
    if not app.state.db_pool: return {"status": "error"}
    try:
        async with app.state.db_pool.acquire() as conn:
            if await conn.fetchrow("SELECT username FROM api_users WHERE email = $1", user.email): return {"status": "error", "message": "Kullanıcı mevcut"}
            new_api_key = f"sk_live_{secrets.token_urlsafe(32)}"
            await conn.execute("INSERT INTO api_users (username, email, api_key, tier, password_hash) VALUES ($1, $2, $3, $4, $5)", user.username, user.email, new_api_key, 'VIP', hash_password(user.password))
        if r: await r.incr(f"reg_ip:{client_ip}"); await r.expire(f"reg_ip:{client_ip}", 3600) 
        return {"status": "success", "api_key": new_api_key}
    except Exception as e: return {"status": "error", "message": str(e)}

@app.post("/api/v1/auth/login")
async def login_user(user: UserLogin, request: Request):
    client_ip = request.client.host if request.client else "unknown"
    r = app.state.redis
    if r and int(await r.get(f"bf_lock:{client_ip}") or 0) >= 5: return {"status": "error", "message": "🚨 15 dakika engellendiniz."}
    try:
        async with app.state.db_pool.acquire() as conn:
            record = await conn.fetchrow("SELECT * FROM api_users WHERE email = $1", user.email)
            if record and verify_password(user.password, record['password_hash']): 
                if r: await r.delete(f"bf_lock:{client_ip}") 
                return {"status": "success", "data": {"username": record['username'], "api_key": record['api_key'], "tier": record['tier']}}
            if r: await r.incr(f"bf_lock:{client_ip}"); await r.expire(f"bf_lock:{client_ip}", 900) 
            return {"status": "error", "message": "Hatalı giriş!"}
    except Exception as e: return {"status": "error"}

async def verify_api_key(api_key_header: str = Security(api_key_header)):
    if not api_key_header: raise HTTPException(status_code=401)
    async with app.state.db_pool.acquire() as conn:
        user = await conn.fetchrow("SELECT username, email, tier FROM api_users WHERE api_key = $1", api_key_header)
    if not user: raise HTTPException(status_code=403)
    await check_redis_limit(user['email'], user['tier'])
    return dict(user)

@app.get("/api/v1/auth/me")
async def get_my_profile(user: dict = Security(verify_api_key)):
    r = app.state.redis
    usage = int(await r.get(f"limit:free:{user['email']}:{datetime.now().strftime('%Y-%m-%d')}") or 0) if user['tier'] == 'FREE' and r else 0
    return {"status": "success", "data": {"username": user['username'], "email": user['email'], "tier": user['tier'], "usage": usage}}

@app.post("/api/v1/auth/update_profile")
async def update_profile(data: ProfileUpdate, user: dict = Security(verify_api_key)):
    async with app.state.db_pool.acquire() as conn:
        await conn.execute("UPDATE api_users SET username = $1 WHERE email = $2", data.username, user['email'])
    return {"status": "success"}

@app.post("/api/v1/auth/change_password")
async def change_password(data: PasswordChange, user: dict = Security(verify_api_key)):
    async with app.state.db_pool.acquire() as conn:
        record = await conn.fetchrow("SELECT password_hash FROM api_users WHERE email = $1", user['email'])
        if verify_password(data.current_password, record['password_hash']):
            await conn.execute("UPDATE api_users SET password_hash = $1 WHERE email = $2", hash_password(data.new_password), user['email'])
            return {"status": "success"}
        return {"status": "error", "message": "Mevcut şifre yanlış"}

@app.post("/api/v1/auth/revoke_key")
async def revoke_api_key(user: dict = Security(verify_api_key)):
    new_api_key = f"sk_live_{secrets.token_urlsafe(32)}"
    async with app.state.db_pool.acquire() as conn:
        await conn.execute("UPDATE api_users SET api_key = $1 WHERE email = $2", new_api_key, user['email'])
    return {"status": "success", "new_api_key": new_api_key}

@app.post("/api/v1/auth/admin_update_tier")
async def admin_update_tier(data: TierUpdate):
    # Not: Gerçek bir sistemde buraya özel bir Admin Auth eklenmelidir
    async with app.state.db_pool.acquire() as conn:
        await conn.execute("UPDATE api_users SET tier = $1 WHERE email = $2", data.new_tier, data.email)
    return {"status": "success"}

# ==============================================================================
# 💼 ADIM 2: PORTFÖY VE CÜZDAN ENTEGRASYONU (BINANCE READ-ONLY)
# ==============================================================================
class PortfolioKeys(BaseModel):
    api_key: str
    secret_key: str

@app.post("/api/v1/portfolio/setup")
async def setup_portfolio(data: PortfolioKeys, user: dict = Security(verify_api_key)):
    """ Kullanıcının Binance API anahtarlarını veritabanına kaydeder """
    async with app.state.db_pool.acquire() as conn:
        await conn.execute("UPDATE api_users SET binance_key = $1, binance_secret = $2 WHERE email = $3", data.api_key, data.secret_key, user['email'])
    return {"status": "success", "message": "Binance Cüzdanı Bağlandı!"}

@app.get("/api/v1/portfolio/me")
async def get_portfolio(user: dict = Security(verify_api_key)):
    """ Binance üzerinden anlık cüzdan bakiyesini çeker """
    async with app.state.db_pool.acquire() as conn:
        record = await conn.fetchrow("SELECT binance_key, binance_secret FROM api_users WHERE email = $1", user['email'])
    
    if not record or not record['binance_key']:
        raise HTTPException(status_code=400, detail="Önce cüzdanınızı bağlayın (/portfolio/setup)")
    
    # Binance Güvenli İmza Oluşturma
    ts = int(time.time() * 1000)
    query_string = f"timestamp={ts}"
    signature = hmac.new(record['binance_secret'].encode('utf-8'), query_string.encode('utf-8'), hashlib.sha256).hexdigest()
    headers = {"X-MBX-APIKEY": record['binance_key']}
    
    try:
        r = requests.get(f"https://api.binance.com/api/v3/account?{query_string}&signature={signature}", headers=headers, timeout=5)
        if r.status_code != 200: return {"status": "error", "message": "Geçersiz veya süresi dolmuş API Anahtarı"}
        
        # Sadece bakiyesi 0'dan büyük olan coinleri getir
        balances = [b for b in r.json().get('balances', []) if float(b['free']) > 0 or float(b['locked']) > 0]
        return {"status": "success", "data": balances}
    except Exception as e:
        return {"status": "error", "message": str(e)}

# ==============================================================================
# 📰 HABER UÇ NOKTASI (NEWS ENDPOINT)
# ==============================================================================
@app.get("/api/v1/news")
async def get_latest_news():
    """ Arayüz için son haberleri döndürür """
    if getattr(app.state, "redis", None):
        news = await app.state.redis.get("LATEST_NEWS")
        if news: return {"status": "success", "data": json.loads(news)}
    return {"status": "error", "message": "Haber verisi bekleniyor."}

# ==============================================================================
# 📡 TÜNELLER, ARBİTRAJ VE CSV EXPORT (GERİ GELDİ)
# ==============================================================================
@app.get("/api/v1/download/market")
async def download_market_data(user: dict = Security(verify_api_key)):
    if user['tier'] == 'FREE': raise HTTPException(status_code=403, detail="Sadece VIP/PREMIUM")
    time_limit = "12 hours" if user['tier'] == "PREMIUM" else "24 hours"
    async def iter_csv():
        yield "symbol,price,volume_usd,cvd,vpin\n"
        async with app.state.db_pool.acquire() as conn:
            async with conn.transaction():
                async for row in conn.cursor(f"SELECT symbol, average_price, volume_usd, cvd, vpin_score FROM market_data WHERE processed_time >= NOW() - INTERVAL '{time_limit}'"):
                    yield f"{row['symbol']},{row['average_price']},{row['volume_usd']},{row['cvd']},{row['vpin_score']}\n"
    return StreamingResponse(iter_csv(), media_type="text/csv", headers={"Content-Disposition": "attachment; filename=radar_extract.csv"})

@app.get("/api/v1/history/{symbol}")
async def get_historical_data(symbol: str, interval: str = "1h", period: str = "1d", user: dict = Security(verify_api_key)):
    """ YFinance Geçmiş Verisi (Eski Sistem Uyumluluğu) """
    if user['tier'] != 'FREE': raise HTTPException(status_code=403, detail="VIP iseniz chart_history kullanın.")
    ticker = yf.Ticker(symbol.replace("USDT", "-USD"))
    df = ticker.history(period=period, interval=interval).reset_index()
    df['Date'] = df.iloc[:,0].dt.strftime('%Y-%m-%d %H:%M:%S')
    return {"status": "success", "tier": "FREE", "data": df[['Date', 'Open', 'High', 'Low', 'Close', 'Volume']].to_dict(orient='records')}

@app.get("/api/v1/futures/{symbol}")
async def get_futures_extra(symbol: str):
    try: return requests.get(f"https://fapi.binance.com/fapi/v1/openInterest?symbol={symbol.upper()}", timeout=3).json()
    except: return {"openInterest": "0"}

@app.get("/api/v1/chart_history/{symbol}")
async def get_chart_history(symbol: str, interval: str = "1m"):
    try: return requests.get(f"https://api.binance.com/api/v3/klines?symbol={symbol.upper()}&interval={interval}&limit=500", timeout=5).json()
    except: return []

@app.get("/api/v1/market/{symbol}")
async def get_market_data(symbol: str, user: dict = Security(verify_api_key)):
    r = app.state.redis
    if r:
        cached = await r.get(f"GOD_MODE_{symbol.upper()}")
        if cached: return {"status": "success", "data": json.loads(cached)}
    return {"status": "error"}

@app.get("/api/v1/arbitrage/{symbol}")
async def get_arbitrage_opportunities(symbol: str, user: dict = Security(verify_api_key)):
    if user['tier'] == 'FREE': raise HTTPException(status_code=403, detail="Arbitraj VIP özelliğidir.")
    base = symbol.replace("USDT", "")
    prices = {}
    async def fetch_price(session, exchange, url, extract_func):
        try:
            async with session.get(url, timeout=2) as response:
                if response.status == 200: prices[exchange] = extract_func(await response.json())
        except: pass

    async with aiohttp.ClientSession() as session:
        tasks = [
            fetch_price(session, "Binance", f"https://api.binance.com/api/v3/ticker/price?symbol={symbol.upper()}", lambda d: float(d['price'])),
            fetch_price(session, "OKX", f"https://www.okx.com/api/v5/market/ticker?instId={base}-USDT", lambda d: float(d['data'][0]['last'])),
            fetch_price(session, "Bybit", f"https://api.bybit.com/v5/market/tickers?category=spot&symbol={symbol.upper()}", lambda d: float(d['result']['list'][0]['lastPrice'])),
            fetch_price(session, "KuCoin", f"https://api.kucoin.com/api/v1/market/orderbook/level1?symbol={base}-USDT", lambda d: float(d['data']['price'])),
            fetch_price(session, "Gate.io", f"https://api.gateio.ws/api/v4/spot/tickers?currency_pair={base}_USDT", lambda d: float(d[0]['last'])),
            fetch_price(session, "MEXC", f"https://api.mexc.com/api/v3/ticker/price?symbol={symbol.upper()}", lambda d: float(d['price'])),
        ]
        await asyncio.gather(*tasks)
    
    if len(prices) < 2: return {"status": "error"}
    mi, ma = min(prices, key=prices.get), max(prices, key=prices.get)
    spread_pct = ((prices[ma] - prices[mi]) / prices[mi]) * 100
    signal = f"🚨 FIRSAT: {ma}'den SAT, {mi}'den AL" if spread_pct > 0.05 else "DENGELİ"
    return {"status": "success", "data": {"prices": prices, "min_exchange": mi, "max_exchange": ma, "spread_usd": round(prices[ma]-prices[mi], 4), "spread_pct": round(spread_pct, 4), "signal": signal}}

# ==============================================================================
# ⏱️ BACKTEST MOTORU
# ==============================================================================
class BacktestRequest(BaseModel):
    symbol: str; strategy: str; days: int = 7

@app.post("/api/v1/backtest")
async def run_timescaledb_backtest(payload: BacktestRequest, user: dict = Security(verify_api_key)):
    if user['tier'] == 'FREE': raise HTTPException(status_code=403)
    if not getattr(app.state, "db_pool", None): raise HTTPException(status_code=500)
    
    query = ""
    if payload.strategy == "cvd_bullish":
        query = f"WITH buckets AS (SELECT time_bucket('5 minutes', processed_time) AS bucket, last(average_price, processed_time) as close_price, sum(cvd) as total_cvd, avg(buy_wall_usd) as avg_buy_wall, avg(sell_wall_usd) as avg_sell_wall FROM market_data WHERE symbol = $1 AND processed_time > NOW() - INTERVAL '{payload.days} days' GROUP BY bucket ORDER BY bucket ASC) SELECT COUNT(*) as total_signals, SUM(CASE WHEN close_price < lead(close_price, 6) OVER (ORDER BY bucket) THEN 1 ELSE 0 END) as winning_trades FROM buckets WHERE total_cvd > 100000 AND avg_buy_wall > avg_sell_wall;"
    elif payload.strategy == "vpin_toxic":
        query = f"WITH buckets AS (SELECT time_bucket('5 minutes', processed_time) AS bucket, last(average_price, processed_time) as close_price, max(vpin_score) as peak_vpin FROM market_data WHERE symbol = $1 AND processed_time > NOW() - INTERVAL '{payload.days} days' GROUP BY bucket ORDER BY bucket ASC) SELECT COUNT(*) as total_signals, SUM(CASE WHEN close_price > lead(close_price, 6) OVER (ORDER BY bucket) THEN 1 ELSE 0 END) as winning_trades FROM buckets WHERE peak_vpin > 0.80;"
    else: raise HTTPException(status_code=400)

    async with app.state.db_pool.acquire() as conn:
        try:
            result = await conn.fetchrow(query, payload.symbol.upper())
            total = result['total_signals'] or 0; wins = result['winning_trades'] or 0
            return {"status": "success", "strategy": payload.strategy, "results": {"total_signals": total, "successful_trades": wins, "win_rate": round((wins/total*100) if total>0 else 0, 2)}}
        except Exception as e: raise HTTPException(status_code=500, detail=str(e))

# --- WEBSOCKET & AI ---
class ConnectionManager:
    def __init__(self): self.active_connections = {}
    async def connect(self, websocket: WebSocket, symbol: str, tier: str):
        await websocket.accept(); self.active_connections.setdefault(symbol, []).append((websocket, tier))
    def disconnect(self, websocket: WebSocket, symbol: str):
        if symbol in self.active_connections: self.active_connections[symbol] = [c for c in self.active_connections[symbol] if c[0] != websocket]

manager = ConnectionManager()

@app.websocket("/api/v1/stream/{symbol}")
async def stream_live_data(websocket: WebSocket, symbol: str, api_key: str = Query(None)):
    if not api_key: return await websocket.close(code=1008)
    async with app.state.db_pool.acquire() as conn:
        user = await conn.fetchrow("SELECT tier FROM api_users WHERE api_key = $1", api_key)
        if not user or user['tier'] not in ['PREMIUM', 'VIP']:
            await websocket.accept(); await websocket.send_json({"error": "Sadece VIP"}); return await websocket.close(code=1008)
        await manager.connect(websocket, symbol.upper(), user['tier'])
    try:
        while True: await websocket.receive_text()
    except: manager.disconnect(websocket, symbol.upper())

async def consume_kafka_and_broadcast():
    while True:
        try:
            consumer = AIOKafkaConsumer(KAFKA_TOPIC, bootstrap_servers=KAFKA_SERVER, value_deserializer=lambda m: json.loads(m.decode('utf-8')))
            await consumer.start()
            async for msg in consumer:
                symbol = msg.value.get("symbol", "").upper()
                if symbol in manager.active_connections:
                    for ws, tier in manager.active_connections[symbol]: await ws.send_json({"type": "LIVE_STREAM", "data": msg.value})
        except: await asyncio.sleep(3)

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
ai_model = genai.GenerativeModel('gemini-2.5-flash') if GEMINI_API_KEY else None
class AIQuestion(BaseModel): symbol: str; question: str; frontend_context: str = ""

@app.post("/api/v1/ask_ai")
async def ask_radar_ai(payload: AIQuestion, user: dict = Security(verify_api_key)):
    if not ai_model: raise HTTPException(status_code=503, detail="Yapay Zeka Kapalı")
    r = app.state.redis
    c = json.loads(await r.get(f"GOD_MODE_{payload.symbol.upper()}") or "{}") if r else {}
    current_state = f"Fiyat:{c.get('p')} CVD:{c.get('cvd')} VPIN:{c.get('vpin')} Imb:{c.get('imb')}"
    try:
        response = await ai_model.generate_content_async(f"Quant Trader olarak yanıtla. Veri: {current_state}. Soru: {payload.question}", generation_config={"temperature": 0.7})
        return {"status": "success", "ai_response": response.text.strip()}
    except Exception as e: raise HTTPException(status_code=500, detail=str(e))