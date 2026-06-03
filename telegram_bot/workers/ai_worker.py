"""
AI proactive worker — listens to 'ai_proactive_alerts' channel in Redis
and forwards AI market reports to the VIP channel.
"""
import asyncio
import json
import logging
import redis.asyncio as aioredis
from config import REDIS_URL, VIP_CHANNEL_ID

logger = logging.getLogger(__name__)

async def ai_update_worker(message_sender, target_chat_id=VIP_CHANNEL_ID):
    backoff = 1
    while True:
        try:
            redis = await aioredis.from_url(REDIS_URL, encoding="utf-8", decode_responses=True)
            pubsub = redis.pubsub()
            await pubsub.subscribe("ai_proactive_alerts")
            logger.info("✅ Subscribed to Redis channel: ai_proactive_alerts")
            backoff = 1

            async for message in pubsub.listen():
                if message["type"] != "message":
                    continue
                
                try:
                    data = json.loads(message["data"])
                    if data.get("type") == "AI_REPORT":
                        content = data.get("content", "")
                        ts = data.get("timestamp", "")
                        
                        header = f"🤖 <b>RADARPRO AI PİYASA ANALİZİ</b> ({ts})\n━━━━━━━━━━━━━━━━━━━━━\n"
                        footer = f"\n━━━━━━━━━━━━━━━━━━━━━\n📡 <i>@RadarPro_VIP_Analiz</i>"
                        
                        await message_sender.send_message(target_chat_id, header + content + footer)
                except Exception as e:
                    logger.error(f"AI worker data error: {e}")

        except asyncio.CancelledError:
            break
        except Exception as e:
            logger.error(f"AI worker error: {e}")
            await asyncio.sleep(backoff)
            backoff = min(backoff * 2, 60)
