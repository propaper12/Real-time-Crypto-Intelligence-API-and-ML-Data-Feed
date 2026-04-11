"""
ML model update worker — subscribes to Redis 'model_updates' pub/sub channel.
ml_watcher.py publishes 'RELOAD_MODELS' here after each successful training run.
"""
import asyncio
import json
import logging

import redis.asyncio as aioredis

from config import REDIS_URL, VIP_CHANNEL_ID
from formatters.ai_prediction import format_ml_model_update

logger = logging.getLogger(__name__)


async def ml_update_worker(message_sender):
    backoff = 1
    while True:
        try:
            redis = await aioredis.from_url(REDIS_URL, encoding="utf-8", decode_responses=True)
            pubsub = redis.pubsub()
            await pubsub.subscribe("model_updates")
            logger.info("✅ Subscribed to Redis channel: model_updates")
            backoff = 1

            async for message in pubsub.listen():
                if message["type"] != "message":
                    continue

                data_str = message["data"]
                logger.info(f"🤖 ML model update signal received: {data_str}")

                # Payload may be plain string 'RELOAD_MODELS' or JSON with metrics
                try:
                    payload = json.loads(data_str)
                except (json.JSONDecodeError, TypeError):
                    # Plain signal — build minimal payload
                    payload = {"model": "champion", "rmse": "N/A", "r2": "N/A"}

                text = format_ml_model_update(payload)
                await message_sender.send_message(VIP_CHANNEL_ID, text)

        except asyncio.CancelledError:
            logger.info("ML update worker cancelled.")
            break
        except Exception as e:
            logger.error(f"ML update worker error: {e}")
            await asyncio.sleep(backoff)
            backoff = min(backoff * 2, 60)
