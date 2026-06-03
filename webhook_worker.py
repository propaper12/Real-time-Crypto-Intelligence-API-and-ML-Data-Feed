import asyncio
import json
import os
import aiohttp
import redis.asyncio as aioredis
import asyncpg
from datetime import datetime

# ==============================================================================
# 📡 RADARPRO WEBHOOK GATEWAY - PUSH NOTIFICATION WORKER
# ==============================================================================

REDIS_URL = os.getenv("REDIS_URL", "redis://redis:6379")
PG_HOST = os.getenv("POSTGRES_HOST", "postgres")
PG_DB = os.getenv("POSTGRES_DB", "market_db")
PG_USER = os.getenv("POSTGRES_USER", "admin_lakehouse")
PG_PASS = os.getenv("POSTGRES_PASSWORD", "SuperSecret_DB_Password_2026")

async def get_db_pool():
    return await asyncpg.create_pool(
        host=PG_HOST, database=PG_DB, user=PG_USER, password=PG_PASS
    )

async def webhook_push_worker():
    print("📡 Webhook Gateway Başlatıldı. Sinyaller PUSH edilecek...")
    redis = await aioredis.from_url(REDIS_URL, decode_responses=True)
    pubsub = redis.pubsub()
    await pubsub.subscribe("arbitrage_alerts")
    
    db_pool = await get_db_pool()
    
    async with aiohttp.ClientSession() as session:
        async for message in pubsub.listen():
            if message["type"] != "message":
                continue
            
            try:
                alert_data = json.loads(message["data"])
                print(f"🔔 Yeni Sinyal Yakalandı: {alert_data['symbol']} - Dağıtılıyor...")
                
                # Webhook URL'si olan tüm VIP kullanıcıları bul
                async with db_pool.acquire() as conn:
                    users = await conn.fetch("SELECT webhook_url FROM api_users WHERE webhook_url IS NOT NULL")
                
                # Tüm URL'lere PUSH gönder (Paralel)
                if users:
                    tasks = []
                    for user in users:
                        url = user['webhook_url']
                        tasks.append(send_webhook(session, url, alert_data))
                    
                    await asyncio.gather(*tasks)
                    print(f"✅ Sinyal {len(users)} kurumsal noktaya iletildi.")

            except Exception as e:
                print(f"⚠️ Webhook Worker Hatası: {e}")

async def send_webhook(session, url, data):
    """ Dış sunucuya sinyali POST eder. """
    try:
        async with session.post(url, json=data, timeout=3) as response:
            if response.status in [200, 201, 202]:
                return True
    except:
        pass
    return False

if __name__ == "__main__":
    asyncio.run(webhook_push_worker())
