"""
Arbitrage alert worker — subscribes to Redis 'arbitrage_alerts' pub/sub channel
and forwards formatted messages to the VIP channel via the MessageSender queue.
"""
import asyncio
import json
import logging

import redis.asyncio as aioredis
from aiogram import types

from config import REDIS_URL, VIP_CHANNEL_ID
from formatters.arbitrage import format_arbitrage_alert
from formatters.generic import format_generic

logger = logging.getLogger(__name__)

def get_exchange_link(exchange: str, symbol: str) -> str:
    """Helper to generate spot trading links for major exchanges."""
    base = symbol.replace("USDT", "")
    links = {
        "Binance": f"https://www.binance.com/en/trade/{base}_USDT?type=spot",
        "OKX": f"https://www.okx.com/markets/spot-info/{base.lower()}-usdt",
        "Bybit": f"https://www.bybit.com/en-US/trade/spot/{base}/USDT",
        "KuCoin": f"https://www.kucoin.com/trade/{base}-USDT",
        "Gate.io": f"https://www.gate.io/trade/{base}_USDT",
        "MEXC": f"https://www.mexc.com/exchange/{base}_USDT",
    }
    return links.get(exchange, "https://coinmarketcap.com")

async def arbitrage_pubsub_worker(message_sender, target_chat_id=VIP_CHANNEL_ID):
    backoff = 1
    while True:
        try:
            redis = await aioredis.from_url(REDIS_URL, encoding="utf-8", decode_responses=True)
            pubsub = redis.pubsub()
            await pubsub.subscribe("arbitrage_alerts")
            logger.info("✅ Subscribed to Redis channel: arbitrage_alerts")
            backoff = 1

            async for message in pubsub.listen():
                if message["type"] != "message":
                    continue
                
                reply_markup = None
                try:
                    data = json.loads(message["data"])
                    if isinstance(data, dict) and data.get("type") == "ARBITRAGE":
                        text = format_arbitrage_alert(data)
                        
                        # CREATE ACTION BUTTONS
                        symbol  = data.get("symbol", "BTCUSDT")
                        buy_ex  = data.get("buy_exchange")
                        sell_ex = data.get("sell_exchange")
                        
                        buttons = [
                            [
                                types.InlineKeyboardButton(text=f"📥 {buy_ex}'de AL", url=get_exchange_link(buy_ex, symbol)),
                                types.InlineKeyboardButton(text=f"📤 {sell_ex}'de SAT", url=get_exchange_link(sell_ex, symbol)),
                            ]
                        ]
                        reply_markup = types.InlineKeyboardMarkup(inline_keyboard=buttons)
                    else:
                        text = format_generic(message["data"])
                except json.JSONDecodeError:
                    text = format_generic(message["data"])

                await message_sender.send_message(target_chat_id, text, reply_markup=reply_markup)

        except asyncio.CancelledError:
            logger.info("Arbitrage worker cancelled.")
            break
        except Exception as e:
            logger.error(f"Arbitrage worker error: {e}")
            await asyncio.sleep(backoff)
            backoff = min(backoff * 2, 60)
