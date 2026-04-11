"""
Kick queue worker — reads 'kick_queue' Redis list and bans users from VIP channel.
"""
import asyncio
import json
import logging

import redis.asyncio as aioredis
from aiogram import Bot

from config import REDIS_URL, VIP_CHANNEL_ID

logger = logging.getLogger(__name__)


async def kick_queue_worker(bot: Bot):
    backoff = 1
    while True:
        try:
            redis = await aioredis.from_url(REDIS_URL, encoding="utf-8", decode_responses=True)
            logger.info("✅ Kick queue worker started.")
            backoff = 1

            while True:
                result = await redis.brpop("kick_queue", timeout=30)
                if result:
                    _, data = result
                    try:
                        job = json.loads(data)
                        user_id = job.get("user_id")
                        if user_id:
                            await bot.ban_chat_member(chat_id=VIP_CHANNEL_ID, user_id=user_id)
                            logger.info(f"⚖️ Kicked user {user_id} from {VIP_CHANNEL_ID}")
                    except json.JSONDecodeError as e:
                        logger.error(f"Kick job decode error '{data}': {e}")
                    except Exception as e:
                        logger.error(f"Kick job processing error: {e}")

        except asyncio.CancelledError:
            logger.info("Kick queue worker cancelled.")
            break
        except Exception as e:
            logger.error(f"Kick queue connection error: {e}")
            await asyncio.sleep(backoff)
            backoff = min(backoff * 2, 60)
