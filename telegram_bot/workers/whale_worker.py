"""
Whale wall worker — subscribes to Redis 'whale_alerts' channel.
ingestion_api.py (or process_silver.py) should publish there when
buy_wall_usd or sell_wall_usd exceeds the configured threshold.
"""
import asyncio
import json
import logging

import redis.asyncio as aioredis

from config import REDIS_URL, VIP_CHANNEL_ID
from formatters.whale import format_whale_alert, format_funding_rate_alert

logger = logging.getLogger(__name__)


async def whale_pubsub_worker(message_sender, target_chat_id=VIP_CHANNEL_ID):
    backoff = 1
    while True:
        try:
            redis = await aioredis.from_url(REDIS_URL, encoding="utf-8", decode_responses=True)
            pubsub = redis.pubsub()
            await pubsub.subscribe("whale_alerts", "funding_alerts")
            logger.info("✅ Subscribed to Redis channels: whale_alerts, funding_alerts")
            backoff = 1

            async for message in pubsub.listen():
                if message["type"] != "message":
                    continue
                try:
                    data = json.loads(message["data"])
                    channel = message.get("channel", "")
                    if channel == "funding_alerts":
                        text = format_funding_rate_alert(data)
                        await message_sender.send_message(VIP_CHANNEL_ID, text)
                    else:
                        text = format_whale_alert(data)
                        await message_sender.send_message(WHALE_CHANNEL_ID, text)
                except Exception as e:
                    logger.warning(f"Whale/Funding message parse error: {e}")

        except asyncio.CancelledError:
            logger.info("Whale worker cancelled.")
            break
        except Exception as e:
            logger.error(f"Whale worker error: {e}")
            await asyncio.sleep(backoff)
            backoff = min(backoff * 2, 60)
