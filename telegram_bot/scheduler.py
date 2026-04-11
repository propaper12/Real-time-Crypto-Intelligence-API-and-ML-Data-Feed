"""
APScheduler-based daily summary scheduler.
Runs at DAILY_SUMMARY_HOUR:DAILY_SUMMARY_MINUTE UTC every day.
Collects 24h stats from Redis and sends to VIP channel.
"""
import asyncio
import json
import logging
from datetime import datetime

import redis.asyncio as aioredis
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger

from config import REDIS_URL, VIP_CHANNEL_ID, DAILY_SUMMARY_HOUR, DAILY_SUMMARY_MINUTE
from formatters.daily_summary import format_daily_summary

logger = logging.getLogger(__name__)


async def _build_daily_stats() -> dict:
    """Gathers 24h aggregated stats from Redis."""
    stats = {
        "date_str": datetime.now().strftime("%d %B %Y"),
        "best_arbitrage": {},
        "total_signals": 0,
        "whale_events": 0,
        "news_count": 0,
        "ml_update_count": 0,
        "champion_model": "N/A",
        "r2": "0.00",
        "top_symbol": "N/A",
    }

    try:
        redis = await aioredis.from_url(REDIS_URL, encoding="utf-8", decode_responses=True)

        # Best arbitrage of the day
        raw_best = await redis.get("daily:best_arbitrage")
        if raw_best:
            stats["best_arbitrage"] = json.loads(raw_best)

        # Signal counts (incremented by ingestion_api)
        total = await redis.get("daily:total_signals")
        stats["total_signals"] = int(total or 0)

        whale = await redis.get("daily:whale_events")
        stats["whale_events"] = int(whale or 0)

        news = await redis.get("daily:news_count")
        stats["news_count"] = int(news or 0)

        ml = await redis.get("daily:ml_updates")
        stats["ml_update_count"] = int(ml or 0)

        # Current champion model info
        champion_raw = await redis.get("mlflow:champion")
        if champion_raw:
            champion_data = json.loads(champion_raw)
            stats["champion_model"] = champion_data.get("model", "N/A")
            stats["r2"] = str(champion_data.get("r2", "0.00"))

        # Top symbol by GOD_MODE cache hits
        god_keys = await redis.keys("GOD_MODE_*")
        if god_keys:
            stats["top_symbol"] = god_keys[0].replace("GOD_MODE_", "")

        await redis.aclose()

    except Exception as e:
        logger.error(f"Daily stats collection error: {e}")

    return stats


async def _send_daily_summary(bot):
    """Called by scheduler — builds stats and sends to VIP channel."""
    logger.info("📋 Sending daily summary...")
    try:
        stats = await _build_daily_stats()
        text = format_daily_summary(stats)
        await bot.send_message(chat_id=VIP_CHANNEL_ID, text=text, parse_mode="HTML")
        logger.info("✅ Daily summary sent.")

        # Reset daily counters
        try:
            redis = await aioredis.from_url(REDIS_URL, encoding="utf-8", decode_responses=True)
            await redis.delete(
                "daily:total_signals",
                "daily:whale_events",
                "daily:news_count",
                "daily:ml_updates",
                "daily:best_arbitrage",
            )
            await redis.aclose()
        except Exception as e:
            logger.warning(f"Could not reset daily counters: {e}")

    except Exception as e:
        logger.error(f"Daily summary send error: {e}")


def setup_scheduler(bot) -> AsyncIOScheduler:
    """Creates and returns a configured AsyncScheduler."""
    scheduler = AsyncIOScheduler()
    scheduler.add_job(
        func=lambda: asyncio.create_task(_send_daily_summary(bot)),
        trigger=CronTrigger(hour=DAILY_SUMMARY_HOUR, minute=DAILY_SUMMARY_MINUTE),
        id="daily_summary",
        name="Daily RadarPro Summary",
        replace_existing=True,
    )
    logger.info(
        f"📅 Daily summary scheduled at {DAILY_SUMMARY_HOUR:02d}:{DAILY_SUMMARY_MINUTE:02d} UTC"
    )
    return scheduler
