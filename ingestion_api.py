import asyncio
import json
import os
import secrets
import base64
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
import ccxt.async_support as ccxt

from pydantic import BaseModel
from fastapi import FastAPI, HTTPException, Request, WebSocket, Security, Query
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, StreamingResponse
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
    """ Haberleri okur, Gemini ile analiz eder ve duygu skorunu Redis'e yazar. """
    print("📰 AI Sentiment Engine Başlatıldı...")
    while True:
        try:
            resp = requests.get("https://cointelegraph.com/rss", timeout=10)
            if resp.status_code == 200:
                root = ET.fromstring(resp.content)
                news_list = []
                for item in root.findall('./channel/item')[:5]:
                    title = item.find('title').text
                    news_list.append(title)
                
                # Gemini ile Sentiment Analizi
                if ai_model and news_list:
                    prompt = f"Aşağıdaki kripto haber başlıklarını analiz et ve piyasa duygu skorunu (-1.0 ile +1.0 arası) tek bir sayı olarak döndür: {', '.join(news_list)}"
                    response = await ai_model.generate_content_async(prompt)
                    sentiment_score = response.text.strip()
                    
                    if getattr(app.state, "redis", None):
                        await app.state.redis.set("GLOBAL_SENTIMENT", sentiment_score)
                        await app.state.redis.set("LATEST_NEWS", json.dumps(news_list))
                        print(f"✅ AI Duygu Analizi Tamamlandı: {sentiment_score}")
        except Exception as e:
            print(f"⚠️ Sentiment Analizi Başarısız: {e}")
        
        await asyncio.sleep(300) 

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

                # 2. 💼 Kullanıcı Tablosuna Portföy ve Webhook İçin Sütun Ekle
                await conn.execute("ALTER TABLE api_users ADD COLUMN IF NOT EXISTS binance_key VARCHAR(255);")
                await conn.execute("ALTER TABLE api_users ADD COLUMN IF NOT EXISTS binance_secret VARCHAR(255);")
                await conn.execute("ALTER TABLE api_users ADD COLUMN IF NOT EXISTS webhook_url TEXT;")
                
                # 🤖 Otonom HFT Bot Ayarları Kolonları
                await conn.execute("ALTER TABLE api_users ADD COLUMN IF NOT EXISTS bot_active BOOLEAN DEFAULT FALSE;")
                await conn.execute("ALTER TABLE api_users ADD COLUMN IF NOT EXISTS bot_sim_mode BOOLEAN DEFAULT TRUE;")
                await conn.execute("ALTER TABLE api_users ADD COLUMN IF NOT EXISTS bot_min_spread DOUBLE PRECISION DEFAULT 0.15;")
                await conn.execute("ALTER TABLE api_users ADD COLUMN IF NOT EXISTS bot_min_trust INTEGER DEFAULT 80;")
                await conn.execute("ALTER TABLE api_users ADD COLUMN IF NOT EXISTS binance_key_enc TEXT;")
                await conn.execute("ALTER TABLE api_users ADD COLUMN IF NOT EXISTS binance_secret_enc TEXT;")
                await conn.execute("ALTER TABLE api_users ADD COLUMN IF NOT EXISTS okx_key_enc TEXT;")
                await conn.execute("ALTER TABLE api_users ADD COLUMN IF NOT EXISTS okx_secret_enc TEXT;")
                await conn.execute("ALTER TABLE api_users ADD COLUMN IF NOT EXISTS okx_pass_enc TEXT;")
                
                # 📈 Bot İşlem Geçmişi Tablosu
                await conn.execute("""
                    CREATE TABLE IF NOT EXISTS bot_trades (
                        id SERIAL PRIMARY KEY,
                        email VARCHAR(255) NOT NULL,
                        symbol VARCHAR(50) NOT NULL,
                        buy_exchange VARCHAR(50),
                        sell_exchange VARCHAR(50),
                        spread_pct DOUBLE PRECISION,
                        profit_usd DOUBLE PRECISION,
                        mode VARCHAR(20) NOT NULL,
                        status VARCHAR(20) NOT NULL,
                        processed_time TIMESTAMP WITHOUT TIME ZONE DEFAULT NOW()
                    );
                """)
                print("✅ Veritabanı Şemaları Kurumsal Mod ve HFT Bot İçin Güncellendi!")
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

async def verify_api_key(api_key_header: str = Security(api_key_header), request: Request = None):
    # Geliştirici Modu Kontrolü (Localhost üzerinden kolay erişim için)
    if os.getenv("DEV_MODE", "false").lower() == "true":
        return {"username": "dev_user", "email": "dev@radarpro.io", "tier": "VIP", "api_key": "sk_live_dev"}

    if not api_key_header: raise HTTPException(status_code=401)
    
    r = getattr(app.state, "redis", None)
    cache_key = f"auth:api_key:{api_key_header}"
    
    if r:
        try:
            cached_user = await r.get(cache_key)
            if cached_user:
                user_dict = json.loads(cached_user)
                await check_redis_limit(user_dict['email'], user_dict['tier'])
                return user_dict
        except Exception as e:
            print(f"⚠️ Redis auth cache okuma hatası: {e}")

    async with app.state.db_pool.acquire() as conn:
        user = await conn.fetchrow("SELECT username, email, tier FROM api_users WHERE api_key = $1", api_key_header)
    if not user: raise HTTPException(status_code=403)
    
    user_dict = dict(user)
    user_dict["api_key"] = api_key_header  # İptal/Güncelleme işlemlerinde önbellek silmek için ekliyoruz
    
    if r:
        try:
            await r.set(cache_key, json.dumps(user_dict), ex=300)
        except Exception as e:
            print(f"⚠️ Redis auth cache yazma hatası: {e}")
            
    await check_redis_limit(user_dict['email'], user_dict['tier'])
    return user_dict

# ==============================================================================
# 🦾 RADARPRO MASTER EXECUTIONER (GERÇEK TİCARET MOTORU)
# ==============================================================================
active_exchanges = {} # Hafızada tutulan aktif borsa bağlantıları

class TradeRequest(BaseModel):
    exchange: str
    api_key: str
    secret_key: str
    passphrase: str = None

class ExecutionRequest(BaseModel):
    symbol: str
    buy_ex: str
    sell_ex: str
    amount: float = 10.0 # Örn: 10 USDT'lik işlem

@app.post("/api/v1/trade/connect")
async def connect_exchange(data: TradeRequest, user: dict = Security(verify_api_key)):
    """ Bir borsayı API anahtarlarıyla sisteme bağlar """
    try:
        ex_class = getattr(ccxt, data.exchange.lower())
        ex = ex_class({
            'apiKey': data.api_key,
            'secret': data.secret_key,
            'password': data.passphrase,
            'enableRateLimit': True
        })
        # Bağlantıyı test et (Bakiye çekerek)
        await ex.fetch_balance()
        active_exchanges[data.exchange.lower()] = ex
        return {"status": "success", "message": f"{data.exchange} başarıyla bağlandı!"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Bağlantı Hatası: {str(e)}")

@app.post("/api/v1/trade/kill")
async def kill_all_trades(user: dict = Security(verify_api_key)):
    """ Tüm borsa bağlantılarını keser ve sistemi durdurur """
    global active_exchanges
    try:
        # Önce borsa bağlantılarını kapat (async)
        for ex in active_exchanges.values():
            await ex.close()
        active_exchanges = {}
        return {"status": "success", "message": "EMERGENCY STOP: Tüm sistemler durduruldu ve bağlantılar kesildi!"}
    except Exception as e:
        return {"status": "error", "message": str(e)}

@app.post("/api/v1/trade/execute")
async def execute_arbitrage(data: ExecutionRequest, user: dict = Security(verify_api_key)):
    """ Arbitraj emrini borsalara iletir (AL ve SAT eş zamanlı) """
    buy_ex_id = data.buy_ex.lower()
    sell_ex_id = data.sell_ex.lower()

    if buy_ex_id not in active_exchanges or sell_ex_id not in active_exchanges:
        return {"status": "error", "message": "İlgili borsalar bağlı değil. Lütfen API bağlayın."}

    b_ex = active_exchanges[buy_ex_id]
    s_ex = active_exchanges[sell_ex_id]

    try:
        # 🚀 EŞ ZAMANLI İNFAZ (AL & SAT)
        tasks = [
            b_ex.create_market_buy_order(data.symbol, data.amount),
            s_ex.create_market_sell_order(data.symbol, data.amount)
        ]
        results = await asyncio.gather(*tasks)
        
        return {
            "status": "success", 
            "message": "Arbitraj Başarıyla İnfaz Edildi!",
            "buy_order": results[0]['id'],
            "sell_order": results[1]['id']
        }
    except Exception as e:
        return {"status": "error", "message": f"İşlem Başarısız: {str(e)}"}


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
        
    r = getattr(app.state, "redis", None)
    if r and "api_key" in user:
        try:
            await r.delete(f"auth:api_key:{user['api_key']}")
        except Exception as e:
            print(f"⚠️ Redis auth cache silme hatası (revoke_api_key): {e}")
            
    return {"status": "success", "new_api_key": new_api_key}

@app.post("/api/v1/auth/admin_update_tier")
async def admin_update_tier(data: TierUpdate):
    # Not: Gerçek bir sistemde buraya özel bir Admin Auth eklenmelidir
    r = getattr(app.state, "redis", None)
    async with app.state.db_pool.acquire() as conn:
        user_record = await conn.fetchrow("SELECT api_key FROM api_users WHERE email = $1", data.email)
        await conn.execute("UPDATE api_users SET tier = $1 WHERE email = $2", data.new_tier, data.email)
        
    if user_record and r:
        try:
            await r.delete(f"auth:api_key:{user_record['api_key']}")
        except Exception as e:
            print(f"⚠️ Redis auth cache silme hatası (admin_update_tier): {e}")
            
    return {"status": "success"}

# ==============================================================================
# 🤖 OTONOM HFT BOT & ŞİFRELİ API ANAHTARI YÖNETİMİ
# ==============================================================================
BOT_SECRET_KEY = os.getenv("BOT_SECRET_KEY", "SuperSecretRadarProBotKey_2026")

def encrypt_key(plain_text: str) -> str:
    if not plain_text: return ""
    key_len = len(BOT_SECRET_KEY)
    xor_bytes = bytearray(ord(c) ^ ord(BOT_SECRET_KEY[i % key_len]) for i, c in enumerate(plain_text))
    return base64.b64encode(xor_bytes).decode('utf-8')

def decrypt_key(cipher_text: str) -> str:
    if not cipher_text: return ""
    try:
        xor_bytes = base64.b64decode(cipher_text.encode('utf-8'))
        key_len = len(BOT_SECRET_KEY)
        plain_bytes = bytearray(b ^ ord(BOT_SECRET_KEY[i % key_len]) for i, b in enumerate(xor_bytes))
        return plain_bytes.decode('utf-8')
    except:
        return ""

class BotSettingsUpdate(BaseModel):
    bot_active: bool
    bot_sim_mode: bool
    bot_min_spread: float
    bot_min_trust: int

class BotKeysUpdate(BaseModel):
    binance_key: str = ""
    binance_secret: str = ""
    okx_key: str = ""
    okx_secret: str = ""
    okx_pass: str = ""

@app.get("/api/v1/bot/settings")
async def get_bot_settings(user: dict = Security(verify_api_key)):
    async with app.state.db_pool.acquire() as conn:
        record = await conn.fetchrow(
            "SELECT bot_active, bot_sim_mode, bot_min_spread, bot_min_trust FROM api_users WHERE email = $1",
            user['email']
        )
        if record:
            return {"status": "success", "data": dict(record)}
    return {"status": "error", "message": "Kullanıcı bulunamadı"}

@app.post("/api/v1/bot/settings")
async def update_bot_settings(data: BotSettingsUpdate, user: dict = Security(verify_api_key)):
    async with app.state.db_pool.acquire() as conn:
        await conn.execute(
            """UPDATE api_users SET 
               bot_active = $1, bot_sim_mode = $2, bot_min_spread = $3, bot_min_trust = $4 
               WHERE email = $5""",
            data.bot_active, data.bot_sim_mode, data.bot_min_spread, data.bot_min_trust, user['email']
        )
    return {"status": "success", "message": "Bot ayarları güncellendi"}

@app.post("/api/v1/bot/keys")
async def update_bot_keys(data: BotKeysUpdate, user: dict = Security(verify_api_key)):
    bin_k = encrypt_key(data.binance_key)
    bin_s = encrypt_key(data.binance_secret)
    okx_k = encrypt_key(data.okx_key)
    okx_s = encrypt_key(data.okx_secret)
    okx_p = encrypt_key(data.okx_pass)
    
    async with app.state.db_pool.acquire() as conn:
        await conn.execute(
            """UPDATE api_users SET 
               binance_key_enc = $1, binance_secret_enc = $2, 
               okx_key_enc = $3, okx_secret_enc = $4, okx_pass_enc = $5
               WHERE email = $6""",
            bin_k, bin_s, okx_k, okx_s, okx_p, user['email']
        )
    return {"status": "success", "message": "Borsa API anahtarları şifrelenerek kaydedildi"}

@app.get("/api/v1/bot/trades")
async def get_bot_trades(user: dict = Security(verify_api_key)):
    async with app.state.db_pool.acquire() as conn:
        rows = await conn.fetch(
            "SELECT * FROM bot_trades WHERE email = $1 ORDER BY processed_time DESC LIMIT 50",
            user['email']
        )
        trades = [dict(r) for r in rows]
        for t in trades:
            if isinstance(t.get("processed_time"), datetime):
                t["processed_time"] = t["processed_time"].strftime("%Y-%m-%d %H:%M:%S")
        
        # İstatistikleri hesapla
        stats_row = await conn.fetchrow(
            """SELECT COUNT(*) as total, 
                      COUNT(CASE WHEN status = 'SUCCESS' THEN 1 END) as success,
                      SUM(profit_usd) as total_profit
               FROM bot_trades WHERE email = $1""",
            user['email']
        )
        stats = {
            "total_trades": stats_row["total"] or 0,
            "successful_trades": stats_row["success"] or 0,
            "total_profit_usd": float(stats_row["total_profit"] or 0.0)
        }
        return {"status": "success", "trades": trades, "stats": stats}

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
# 🔌 WEBHOOK GATEWAY (KURUMSAL ENTEGRASYON)
# ==============================================================================
class WebhookUpdate(BaseModel):
    url: str

@app.post("/api/v1/settings/webhook")
async def update_webhook_url(data: WebhookUpdate, user: dict = Security(verify_api_key)):
    """ Geliştiricilerin sinyal push bildirimi alacağı URL'yi kaydeder """
    if not data.url.startswith("http"):
        raise HTTPException(status_code=400, detail="Geçersiz URL formatı")
    
    async with app.state.db_pool.acquire() as conn:
        await conn.execute("UPDATE api_users SET webhook_url = $1 WHERE email = $2", data.url, user['email'])
    
    # Redis Cache'e de atalım ki scanner hızlıca erişsin
    r = app.state.redis
    if r: await r.set(f"webhook:{user['email']}", data.url)
    
    return {"status": "success", "message": "Webhook URL başarıyla kaydedildi!"}
@app.get("/dashboard")
async def get_dashboard_page():
    return FileResponse("dashboard.html")

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
    symbol = symbol.upper()
    tier = user.get("tier", "FREE")
    r = app.state.redis
    
    # 1. Try to get the live/latest data first
    live_data = None
    if r:
        try:
            cached = await r.get(f"GOD_MODE_{symbol}")
            if cached:
                live_data = json.loads(cached)
                # Map keys for compatibility
                if "p" in live_data and "average_price" not in live_data:
                    live_data["average_price"] = live_data["p"]
                if "volume_usd" not in live_data:
                    live_data["volume_usd"] = live_data.get("vol", 0.0)
                if "processed_time" not in live_data:
                    live_data["processed_time"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        except Exception as e:
            print(f"Redis error: {e}")
            
    if not live_data and getattr(app.state, "db_pool", None):
        try:
            async with app.state.db_pool.acquire() as conn:
                row = await conn.fetchrow(
                    "SELECT * FROM market_data WHERE symbol = $1 ORDER BY processed_time DESC LIMIT 1",
                    symbol
                )
                if row:
                    live_data = dict(row)
                    if isinstance(live_data.get("processed_time"), datetime):
                        live_data["processed_time"] = live_data["processed_time"].strftime("%Y-%m-%d %H:%M:%S")
        except Exception as e:
            print(f"DB error: {e}")

    # Fallback to hardcoded mock base prices if database and Redis are completely empty
    if not live_data:
        fallback_p = 96200.0 if symbol == "BTCUSDT" else (3450.0 if symbol == "ETHUSDT" else 178.0)
        live_data = {
            "average_price": fallback_p,
            "volume_usd": 1500000.0,
            "processed_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }

    # 2. If the user is FREE, calculate delayed price and 24h stats
    if tier == "FREE":
        free_data = {}
        if getattr(app.state, "db_pool", None):
            try:
                async with app.state.db_pool.acquire() as conn:
                    # 1 minute delayed price
                    delayed_row = await conn.fetchrow(
                        "SELECT average_price, processed_time FROM market_data WHERE symbol = $1 AND processed_time <= NOW() - INTERVAL '1 minute' ORDER BY processed_time DESC LIMIT 1",
                        symbol
                    )
                    if delayed_row:
                        free_data["delayed_price"] = delayed_row["average_price"]
                        free_data["processed_time"] = delayed_row["processed_time"].strftime("%Y-%m-%d %H:%M:%S")
                    else:
                        free_data["delayed_price"] = live_data["average_price"] * 0.998
                        free_data["processed_time"] = live_data["processed_time"]

                    # 24h stats (average, max, min)
                    stats_row = await conn.fetchrow(
                        "SELECT AVG(average_price) as avg_p, MAX(average_price) as max_p, MIN(average_price) as min_p FROM market_data WHERE symbol = $1 AND processed_time >= NOW() - INTERVAL '24 hours'",
                        symbol
                    )
                    if stats_row and stats_row["avg_p"] is not None:
                        free_data["avg_p"] = stats_row["avg_p"]
                        free_data["max_p"] = stats_row["max_p"]
                        free_data["min_p"] = stats_row["min_p"]
                    else:
                        p = live_data["average_price"]
                        free_data["avg_p"] = p * 0.995
                        free_data["max_p"] = p * 1.025
                        free_data["min_p"] = p * 0.965
            except Exception as e:
                print(f"DB Free stats error: {e}")
        
        if "delayed_price" not in free_data:
            p = live_data["average_price"]
            free_data["delayed_price"] = p * 0.998
            free_data["processed_time"] = live_data["processed_time"]
            free_data["avg_p"] = p * 0.995
            free_data["max_p"] = p * 1.025
            free_data["min_p"] = p * 0.965
            
        return {"status": "success", "tier": tier, "data": free_data}

    # 3. For VIP, PRO, PREMIUM, etc. return real-time live data
    return {"status": "success", "tier": tier, "data": live_data}


def calculate_trust_score(god_data: dict) -> dict:
    """
    Arbitraj sinyalinin güvenilirliğini 0-100 arası puanlar.
    Kriterler: VPIN (Toksisite), Anomali (Sahte Hacim), Derinlik (Emir Defteri).
    """
    score = 100
    reasons = []

    vpin = god_data.get("vpin", 0)
    anomaly_wash = god_data.get("anomaly_wash", False)
    anomaly_spoof = god_data.get("anomaly_spoof", False)
    buy_wall = god_data.get("buy_wall_usd", 0)
    sell_wall = god_data.get("sell_wall_usd", 0)
    volatility = god_data.get("volatility", 0)

    # 1. VPIN (Akış Toksisitesi) Kontrolü
    if vpin > 0.8:
        score -= 40
        reasons.append("Yüksek Toksik Akış (VPIN > 0.8)")
    elif vpin > 0.6:
        score -= 20
        reasons.append("Orta Derece Toksisite")

    # 2. Anomali Kontrolü (Wash Trading / Spoofing)
    if anomaly_wash:
        score -= 50
        reasons.append("Wash Trading Saptandı")
    if anomaly_spoof:
        score -= 30
        reasons.append("Spoofing (Sahte Duvar) Saptandı")

    # 3. Likidite Derinliği Kontrolü
    if buy_wall < 50000 or sell_wall < 50000:
        score -= 25
        reasons.append("Düşük Likidite Derinliği")
    
    # 4. Volatilite Kontrolü
    if volatility > 0.05: # %5 üstü anlık volatilite risklidir
        score -= 15
        reasons.append("Aşırı Volatilite")

    score = max(0, score)
    
    status = "GÜVENLİ" if score >= 80 else ("RİSKLİ" if score >= 50 else "TEHLİKELİ")
    return {"score": score, "status": status, "warnings": reasons}

@app.get("/api/v1/arbitrage")
async def get_all_arbitrage(user: dict = Security(verify_api_key)):
    """ Tüm aktif arbitraj fırsatlarını listeler (Scanner verisi) """
    r = app.state.redis
    if not r: return {"status": "error", "message": "Redis yok"}
    
    keys = await r.keys("ARB_STATE_*")
    results = []
    for key in keys:
        raw = await r.get(key)
        if raw: results.append(json.loads(raw))
    
    results.sort(key=lambda x: x.get("spread_pct", 0), reverse=True)
    return {"status": "success", "count": len(results), "data": results}

@app.get("/api/v1/arbitrage/{symbol}")
async def get_single_arbitrage(symbol: str, user: dict = Security(verify_api_key)):
    """ Belirli bir coin için 10 borsa verisini döndürür """
    r = app.state.redis
    if not r: return {"status": "error"}
    
    raw = await r.get(f"ARB_STATE_{symbol.upper()}")
    if not raw: return {"status": "error", "message": "Veri bulunamadı. Scanner çalışıyor mu?"}
    
    return {"status": "success", "data": json.loads(raw)}

@app.get("/api/v1/arbitrage/all/safe")
async def get_all_safe_arbitrage(min_score: int = Query(75), min_spread: float = Query(0.1), user: dict = Security(verify_api_key)):
    """
    Dış trading botları için global tarama. 
    Redis'teki ARB_STATE_* anahtarlarını tarar ve filtrelenmiş sonuçları döner.
    """
    if user['tier'] == 'FREE': raise HTTPException(status_code=403)
    
    r = app.state.redis
    if not r: return {"status": "error", "message": "Redis bağlantısı yok"}
    
    keys = await r.keys("ARB_STATE_*")
    safe_opportunities = []
    
    for key in keys:
        raw = await r.get(key)
        if raw:
            data = json.loads(raw)
            # Filtreleme: Güven Skoru ve Spread kontrolü
            if data.get("trust_score", 0) >= min_score and data.get("spread_pct", 0) >= min_spread:
                safe_opportunities.append(data)
                
    # En karlı olanı en başa al
    safe_opportunities.sort(key=lambda x: x.get("spread_pct", 0), reverse=True)
    
    return {
        "status": "success", 
        "count": len(safe_opportunities),
        "data": safe_opportunities
    }

# ==============================================================================
# 🤖 RADARAI - AGENT VALIDATION API
# ==============================================================================
class TradeProposal(BaseModel):
    symbol: str
    buy_exchange: str
    sell_exchange: str
    spread_pct: float

@app.post("/api/v1/agent/validate")
async def validate_trade_with_ai(proposal: TradeProposal, user: dict = Security(verify_api_key)):
    """
    Dış botların 'AI Onayı' alabileceği endpoint. 
    Gemini; VPIN, Anomali ve Haberler eşliğinde kararı onaylar veya reddeder.
    """
    if not ai_model: raise HTTPException(status_code=503, detail="AI Kapalı")
    
    r = app.state.redis
    symbol = proposal.symbol.upper()
    
    # 1. Market Context Topla
    god_raw = await r.get(f"GOD_MODE_{symbol}") if r else None
    god_data = json.loads(god_raw) if god_raw else {}
    
    news_raw = await r.get("LATEST_NEWS") if r else None
    news = json.loads(news_raw) if news_raw else []
    
    context = {
        "price": god_data.get("p"),
        "vpin": god_data.get("vpin"),
        "anomaly": "VAR" if god_data.get("anomaly_wash") or god_data.get("anomaly_spoof") else "YOK",
        "imbalance": god_data.get("wall_imbalance"),
        "latest_news": [n['title'] for n in news[:3]]
    }

    # 2. Gemini'ye Soru Sor
    prompt = f"""
    SİSTEM: RadarPro Quant AI Agent
    GÖREV: Trade Onayı / Reddi
    
    PROPOSAL: {symbol} için {proposal.buy_exchange} -> {proposal.sell_exchange} arasında %{proposal.spread_pct} arbitraj makası.
    MARKET CONTEXT: {json.dumps(context)}
    
    KARAR KURALLARI:
    1. VPIN > 0.8 ise REDDET.
    2. Anomali varsa REDDET.
    3. Haberler aşırı negatifse REDDET.
    
    YANIT FORMATI (JSON):
    {{
        "decision": "APPROVED" | "REJECTED",
        "confidence": 0-100,
        "reason": "Kısa ve öz teknik açıklama",
        "risk_level": "LOW" | "MEDIUM" | "HIGH"
    }}
    """
    
    try:
        response = await ai_model.generate_content_async(prompt, generation_config={"response_mime_type": "application/json"})
        return {"status": "success", "ai_decision": json.loads(response.text)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

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
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)
    ai_model = genai.GenerativeModel('gemini-1.5-flash')
else:
    ai_model = None
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

@app.post("/reload")
@app.post("/api/v1/reload")
async def trigger_model_reload():
    """ train_model.py tarafından çağrılır, Redis Pub/Sub üzerinden model yenileme sinyali gönderir """
    r = getattr(app.state, "redis", None)
    if r:
        try:
            await r.publish("model_updates", "RELOAD_MODELS")
            return {"status": "success", "message": "Model reload published successfully"}
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
    return {"status": "warning", "message": "Redis connection not available, reload not published"}