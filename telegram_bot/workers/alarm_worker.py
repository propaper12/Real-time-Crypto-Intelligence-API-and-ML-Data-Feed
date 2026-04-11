"""
Price alarm worker — periodically checks user-defined price alarms stored in Redis.
Key pattern: alarm:{user_id}:{symbol}:{target_price}:{direction}
direction: 'up' (notify when price >= target) | 'down' (notify when price <= target)
"""
import asyncio
import json
import logging

import redis.asyncio as aioredis

from config import REDIS_URL, FASTAPI_MARKET_URL
from formatters.generic import format_price_alarm_triggered

logger = logging.getLogger(__name__)

CHECK_INTERVAL_SECS = 30  # check alarms every 30 seconds


async def _fetch_current_price(session, symbol: str) -> float | None:
    """Pulls current price from Binance public ticker (no API key needed)."""
    import aiohttp
    url = f"https://api.binance.com/api/v3/ticker/price?symbol={symbol.upper()}"
    try:
        async with session.get(url, timeout=aiohttp.ClientTimeout(total=5)) as r:
            if r.status == 200:
                data = await r.json()
                return float(data["price"])
    except Exception:
        pass
    return None


async def alarm_checker_worker(bot):
    """
    Polls Redis every CHECK_INTERVAL_SECS seconds.
    For each alarm key, fetches live price and fires DM if condition is met.
    """
    import aiohttp
    backoff = 1

    while True:
        try:
            redis = await aioredis.from_url(REDIS_URL, encoding="utf-8", decode_responses=True)
            logger.info("✅ Alarm checker worker started.")
            backoff = 1

            async with aiohttp.ClientSession() as session:
                while True:
                    try:
                        keys = await redis.keys("alarm:*")
                        for key in keys:
                            try:
                                parts = key.split(":")
                                # Expected pattern: alarm:{user_id}:{symbol}:{target}:{direction}
                                if len(parts) != 5:
                                    continue
                                _, user_id, symbol, target_str, direction = parts
                                target = float(target_str)
                                current = await _fetch_current_price(session, symbol)
                                if current is None:
                                    continue

                                triggered = (
                                    (direction == "up"   and current >= target) or
                                    (direction == "down" and current <= target)
                                )
                                if triggered:
                                    text = format_price_alarm_triggered(symbol, target, current, direction)
                                    try:
                                        await bot.send_message(
                                            chat_id=int(user_id),
                                            text=text,
                                            parse_mode="HTML"
                                        )
                                        logger.info(f"🔔 Alarm fired: {key}")
                                    except Exception as send_err:
                                        logger.warning(f"Could not DM user {user_id}: {send_err}")
                                    # Remove fired alarm
                                    await redis.delete(key)

                            except Exception as e:
                                logger.warning(f"Alarm key error '{key}': {e}")

                    except Exception as e:
                        logger.warning(f"Alarm check cycle error: {e}")

                    await asyncio.sleep(CHECK_INTERVAL_SECS)

        except asyncio.CancelledError:
            logger.info("Alarm checker cancelled.")
            break
        except Exception as e:
            logger.error(f"Alarm checker connection error: {e}")
            await asyncio.sleep(backoff)
            backoff = min(backoff * 2, 60)
