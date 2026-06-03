import asyncio
import os
import json
import aiohttp
import redis.asyncio as aioredis
from datetime import datetime

# ==============================================================================
# 📱 RADARPRO - TELEGRAM COMMAND & CONTROL CENTER
# ==============================================================================

TELEGRAM_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
REDIS_URL = os.getenv("REDIS_URL", "redis://redis_cache:6379")

async def send_telegram_msg(session, message):
    if not TELEGRAM_TOKEN or not TELEGRAM_CHAT_ID: return
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {"chat_id": TELEGRAM_CHAT_ID, "text": message, "parse_mode": "HTML"}
    try:
        async with session.post(url, json=payload) as resp:
            return await resp.json()
    except: pass

async def telegram_worker():
    print("📱 Telegram Worker Başlatıldı...")
    r = await aioredis.from_url(REDIS_URL, decode_responses=True)
    async with aiohttp.ClientSession() as session:
        last_alert_time = {} # Aynı coin için sürekli mesaj atmayalım
        
        while True:
            try:
                # Redis'ten tüm arbitraj durumlarını tara
                keys = await r.keys("ARB_STATE_*")
                for key in keys:
                    raw = await r.get(key)
                    if not raw: continue
                    data = json.loads(raw)
                    symbol = data['symbol']
                    spread = data['spread_pct']
                    
                    # KRİTİK EŞİK: %0.50 ve üzeri ise bildirim at
                    if spread >= 0.50:
                        now = datetime.now()
                        if symbol not in last_alert_time or (now - last_alert_time[symbol]).seconds > 300: # 5 dk limit
                            msg = (
                                f"🚨 <b>TITAN ARBITRAGE ALERT</b> 🚨\n\n"
                                f"<b>Symbol:</b> {symbol}\n"
                                f"<b>Spread:</b> %{spread}\n"
                                f"<b>Route:</b> {data['buy_exchange']} ➔ {data['sell_exchange']}\n"
                                f"<b>Trust Score:</b> {data['trust_score']}\n"
                                f"<b>Time:</b> {data['timestamp']}\n\n"
                                f"⚡ <i>RadarPro Titan v6.0</i>"
                            )
                            await send_telegram_msg(session, msg)
                            last_alert_time[symbol] = now
            except Exception as e:
                print(f"⚠️ Telegram Hatası: {e}")
            
            await asyncio.sleep(10) # 10 saniyede bir kontrol et

if __name__ == "__main__":
    asyncio.run(telegram_worker())
