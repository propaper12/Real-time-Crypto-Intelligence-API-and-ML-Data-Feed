"""
MessageSender — thread-safe async queue for rate-limited Telegram delivery.
Also handles the zero-friction Telegram auth webhook to ingestion_api.
"""
import asyncio
import logging

import aiohttp
from aiogram import Bot
from aiogram.exceptions import TelegramRetryAfter, TelegramAPIError

from config import FASTAPI_AUTH_URL, REDIS_URL

logger = logging.getLogger(__name__)


class MessageSender:
    """
    Single queue for all outgoing Telegram messages.
    Respects Telegram rate limits with exponential backoff.
    """

    def __init__(self, bot: Bot):
        self.bot = bot
        self.queue: asyncio.Queue = asyncio.Queue()
        self.worker_task: asyncio.Task | None = None

    async def start(self):
        self.worker_task = asyncio.create_task(self._worker())
        logger.info("MessageSender started.")

    async def stop(self):
        if self.worker_task:
            self.worker_task.cancel()
            logger.info("MessageSender stopped.")

    async def send_message(self, chat_id: str | int, text: str, reply_markup=None):
        await self.queue.put((chat_id, text, reply_markup))

    async def _worker(self):
        while True:
            chat_id, text, reply_markup = await self.queue.get()
            try:
                await self._safe_send(chat_id, text, reply_markup)
                # Keep well below Telegram group limit (20/min → 0.05s gap)
                await asyncio.sleep(0.05)
            except Exception as e:
                logger.error(f"MessageSender worker error: {e}")
            finally:
                self.queue.task_done()

    async def _safe_send(self, chat_id, text: str, reply_markup=None, retries: int = 5):
        backoff = 1
        for attempt in range(retries):
            try:
                await self.bot.send_message(
                    chat_id=chat_id,
                    text=text,
                    parse_mode="HTML",
                    reply_markup=reply_markup,
                    disable_web_page_preview=True,
                )
                return
            except TelegramRetryAfter as e:
                logger.warning(f"Rate limited. Waiting {e.retry_after}s…")
                await asyncio.sleep(e.retry_after)
            except TelegramAPIError as e:
                logger.error(f"TelegramAPIError [{attempt+1}/{retries}]: {e}")
                await asyncio.sleep(backoff)
                backoff *= 2
            except Exception as e:
                logger.error(f"Unexpected send error [{attempt+1}/{retries}]: {e}")
                await asyncio.sleep(backoff)
                backoff *= 2
        logger.error(f"Gave up sending to {chat_id} after {retries} attempts.")


async def notify_fastapi_auth(telegram_id: int, invite_link: str):
    """Sends auth data to ingestion_api so it can match telegram_id to invite_link."""
    async with aiohttp.ClientSession() as session:
        try:
            payload = {"telegram_id": telegram_id, "invite_link": invite_link}
            async with session.post(FASTAPI_AUTH_URL, json=payload, timeout=10) as r:
                if r.status in (200, 201):
                    logger.info(f"Auth sent for user {telegram_id}")
                else:
                    logger.error(f"Auth HTTP {r.status} for user {telegram_id}")
        except Exception as e:
            logger.error(f"FastAPI auth error: {e}")


async def cache_user_tier(telegram_id: int, tier: str):
    """Caches user tier in Redis so command handlers can look it up instantly."""
    import redis.asyncio as aioredis
    try:
        redis = await aioredis.from_url(REDIS_URL, encoding="utf-8", decode_responses=True)
        await redis.set(f"tg_tier:{telegram_id}", tier, ex=3600)  # refresh hourly
        await redis.aclose()
    except Exception as e:
        logger.warning(f"Could not cache tier for {telegram_id}: {e}")
