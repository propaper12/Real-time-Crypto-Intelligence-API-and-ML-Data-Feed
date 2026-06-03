import asyncio
import json
import os
import google.generativeai as genai
import redis.asyncio as aioredis
from datetime import datetime

# ==============================================================================
# 🧠 RADARPRO AI AGENT - PROACTIVE MARKET ANALYST
# ==============================================================================

REDIS_URL = os.getenv("REDIS_URL", "redis://redis:6379")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
ANALYZE_INTERVAL = 60 # Her 1 dakikada bir analiz yap

if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)
    ai_model = genai.GenerativeModel('gemini-1.5-flash')
else:
    ai_model = None

async def get_top_arbitrage(redis):
    keys = await redis.keys("ARB_STATE_*")
    opportunities = []
    for key in keys:
        raw = await redis.get(key)
        if raw: opportunities.append(json.loads(raw))
    
    # En karlı 5 fırsatı al
    opportunities.sort(key=lambda x: x.get("spread_pct", 0), reverse=True)
    return opportunities[:5]

async def ai_proactive_loop():
    if not ai_model:
        print("⚠️ Gemini API Key bulunamadı. AI Agent devre dışı.")
        return

    print("🧠 RadarAI Proaktif Analiz Başlatıldı...")
    redis = await aioredis.from_url(REDIS_URL, decode_responses=True)
    
    while True:
        try:
            # 1. Veri Topla
            top_arbs = await get_top_arbitrage(redis)
            news_raw = await redis.get("LATEST_NEWS")
            news = json.loads(news_raw) if news_raw else []
            
            if not top_arbs:
                await asyncio.sleep(10)
                continue

            # 2. Prompt Hazırla
            prompt = f"""
            SİSTEM: RadarPro Baş Analist AI
            GÖREV: Piyasa Özeti ve Fırsat Değerlendirmesi
            
            EN KARLI ARBİTRAJ FIRSATLARI:
            {json.dumps(top_arbs)}
            
            SON HABERLER:
            {json.dumps([n['title'] for n in news[:3]])}
            
            YÖNERGE:
            - Piyasanın genel durumunu 1 cümleyle özetle.
            - Listelenen arbitraj fırsatlarından en 'GÜVENLİ' ve 'KARLI' olan 1 tanesini seç ve nedenini açıkla.
            - Teknik bir 'Trader Tavsiyesi' ekle.
            - Yanıtın profesyonel, kısa ve Türkçe olsun.
            - Markdown (Bold/Emoji) kullan.
            """

            # 3. Gemini Analizi
            response = await ai_model.generate_content_async(prompt)
            ai_report = response.text.strip()

            # 4. Yayınla (Redis Pub/Sub ve Cache)
            
            payload = {
                "type": "AI_REPORT",
                "content": ai_report,
                "timestamp": datetime.now().strftime("%H:%M")
            }
            await redis.publish("ai_proactive_alerts", json.dumps(payload))
            await redis.set("ai_last_report", json.dumps(payload)) # Bot komutu için cache
            print(f"✅ AI Raporu Yayınlandı: {payload['timestamp']}")

        except Exception as e:
            print(f"⚠️ RadarAI Hatası: {e}")
        
        await asyncio.sleep(ANALYZE_INTERVAL)

if __name__ == "__main__":
    asyncio.run(ai_proactive_loop())
