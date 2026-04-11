import json
import logging
import redis.asyncio as aioredis
from config import REDIS_URL, VIP_CHANNEL_ID
from aiogram import Bot
from formatter import TelegramFormatter

logger = logging.getLogger(__name__)

async def redis_pubsub_worker(message_sender):
    """Listens to arbitrage_alerts channel in Redis and forwards messages to the VIP channel"""
    backoff = 1
    while True:
        try:
            redis = await aioredis.from_url(REDIS_URL, encoding="utf-8", decode_responses=True)
            pubsub = redis.pubsub()
            await pubsub.subscribe("arbitrage_alerts")
            logger.info("Subscribed to Redis channel: arbitrage_alerts")
            backoff = 1 # Reset backoff on successful connection
            
            async for message in pubsub.listen():
                if message['type'] == 'message':
                    data_str = message['data']
                    try:
                        data = json.loads(data_str)
                        if isinstance(data, dict) and data.get("type") == "ARBITRAGE":
                            formatted_msg = TelegramFormatter.format_arbitrage_alert(data)
                        else:
                            formatted_msg = TelegramFormatter.format_generic_message(data_str)
                    except json.JSONDecodeError:
                        formatted_msg = TelegramFormatter.format_generic_message(data_str)
                    
                    await message_sender.send_message(VIP_CHANNEL_ID, formatted_msg)
            
        except asyncio.CancelledError:
            logger.info("Redis PubSub worker cancelled")
            break
        except Exception as e:
            logger.error(f"Redis PubSub connection error: {e}")
            await asyncio.sleep(backoff)
            backoff = min(backoff * 2, 60) # Max 60 seconds exponential backoff

async def redis_kick_queue_worker(bot: Bot):
    """Listens to a kick_queue in Redis (List structure) to ban users from the channel"""
    backoff = 1
    while True:
        try:
            redis = await aioredis.from_url(REDIS_URL, encoding="utf-8", decode_responses=True)
            logger.info("Listening to Redis kick_queue")
            backoff = 1
            
            while True:
                # BRPOP blocks until an item is appended to 'kick_queue', timeout 0 means block indefinitely
                result = await redis.brpop("kick_queue", timeout=0)
                if result:
                    _, data = result
                    try:
                        job = json.loads(data)
                        user_id = job.get("user_id")
                        if user_id:
                            # Ban the user from the channel
                            await bot.ban_chat_member(chat_id=VIP_CHANNEL_ID, user_id=user_id)
                            logger.info(f"Successfully kicked/banned user {user_id} from {VIP_CHANNEL_ID}")
                    except json.JSONDecodeError as e:
                        logger.error(f"Failed to decode kick job '{data}': {e}")
                    except Exception as e:
                        logger.error(f"Failed to process kick job '{data}': {e}")
                        
        except asyncio.CancelledError:
            logger.info("Redis kick queue worker cancelled")
            break
        except Exception as e:
            logger.error(f"Redis Kick Queue connection error: {e}")
            await asyncio.sleep(backoff)
            backoff = min(backoff * 2, 60)
