"""
News worker — polls Redis key 'LATEST_NEWS' every 5 minutes.
When the news list changes (hash comparison), broadcasts the update.
"""
import asyncio
import hashlib
import json
import logging

import redis.asyncio as aioredis

from config import REDIS_URL, VIP_CHANNEL_ID
from formatters.news import format_news_flash

logger = logging.getLogger(__name__)


async def news_pubsub_worker(message_sender):
    backoff = 1
    last_hash = ""

    while True:
        try:
            redis = await aioredis.from_url(REDIS_URL, encoding="utf-8", decode_responses=True)
            logger.info("✅ News worker started. Polling LATEST_NEWS every 5 min.")
            backoff = 1

            while True:
                try:
                    raw = await redis.get("LATEST_NEWS")
                    if raw:
                        current_hash = hashlib.md5(raw.encode()).hexdigest()
                        if current_hash != last_hash:
                            last_hash = current_hash
                            news_list = json.loads(raw)
                            text = format_news_flash(news_list)
                            await message_sender.send_message(VIP_CHANNEL_ID, text)
                            logger.info("📰 New news broadcast sent.")
                except Exception as e:
                    logger.warning(f"News poll error: {e}")

                await asyncio.sleep(300)  # poll every 5 minutes

        except asyncio.CancelledError:
            logger.info("News worker cancelled.")
            break
        except Exception as e:
            logger.error(f"News worker connection error: {e}")
            await asyncio.sleep(backoff)
            backoff = min(backoff * 2, 60)
