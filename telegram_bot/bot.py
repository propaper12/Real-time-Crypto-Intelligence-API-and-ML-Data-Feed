"""
RadarPro Telegram Bot — Main Orchestrator (v2)
Fully featured: interactive commands, 5 Redis workers, scheduler, admin panel.
"""
import asyncio
import logging

from aiogram import Bot, Dispatcher, types
from aiogram.filters.chat_member_updated import ChatMemberUpdatedFilter, JOIN_TRANSITION

from config import BOT_TOKEN
from services import MessageSender, notify_fastapi_auth, cache_user_tier
from handlers import commands_router, alarms_router, admin_router, callbacks_router

from workers import (
    arbitrage_pubsub_worker,
    news_pubsub_worker,
    ml_update_worker,
    whale_pubsub_worker,
    alarm_checker_worker,
    kick_queue_worker,
)
from scheduler import setup_scheduler

# ─── Logging ─────────────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(name)-25s | %(levelname)-8s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)

# ─── Bot & Dispatcher ────────────────────────────────────────────────────────
bot = Bot(token=BOT_TOKEN)
dp  = Dispatcher()

# ─── Middleware ─────────────────────────────────────────────────────────────
@dp.update.outer_middleware()
async def log_updates_middleware(handler, event, data):
    if event.message and event.message.text:
        logger.info(f"📩 Mesaj Alındı: '{event.message.text}' | User: {event.message.from_user.id}")
    return await handler(event, data)

# Register all routers
dp.include_router(commands_router)
dp.include_router(alarms_router)
dp.include_router(admin_router)
dp.include_router(callbacks_router)


# ─── New member join handler ─────────────────────────────────────────────────

@dp.chat_member(ChatMemberUpdatedFilter(member_status_changed=JOIN_TRANSITION))
async def on_user_join(event: types.ChatMemberUpdated):
    """
    Zero-Friction Auth: captures invite link used → notifies FastAPI.
    Also caches the user's tier via the API response.
    """
    user = event.new_chat_member.user
    invite_link = event.invite_link.invite_link if event.invite_link else None

    logger.info(f"👤 User {user.id} ({user.username}) joined. Link: {invite_link}")

    if invite_link:
        asyncio.create_task(notify_fastapi_auth(user.id, invite_link))
    else:
        logger.warning(f"User {user.id} joined without invite link (public access or admin added).")


async def set_bot_commands(bot: Bot):
    """Sets the bot command menu visible in Telegram's UI."""
    commands = [
        types.BotCommand(command="start",    description="🚀 RadarPro Titan başlatıcı"),
        types.BotCommand(command="canli",    description="📡 [SEMBOL] Canlı 2dk fiyat akışı"),
        types.BotCommand(command="fiyat",    description="💰 [SEMBOL] Anlık tam analiz"),
        types.BotCommand(command="arbitraj", description="⚡ Top 15 arbitraj fırsatı"),
        types.BotCommand(command="ai",       description="🧠 [SEMBOL SORU] Gemini AI analizi"),
        types.BotCommand(command="haberler", description="📰 Son kripto haberleri"),
        types.BotCommand(command="rehber",   description="📖 Teknik indikatör rehberi (TR)"),
        types.BotCommand(command="manual",   description="📖 Indicator guide (EN)"),
        types.BotCommand(command="durum",    description="⚙️ Sistem sağlık raporu"),
        types.BotCommand(command="yardim",   description="❓ Tüm komutları listele"),
    ]
    await bot.set_my_commands(commands)
    logger.info("✅ Bot komut menüsü güncellendi.")

# ─── Main ────────────────────────────────────────────────────────────────────

async def main():
    logger.info("🚀 RadarPro Telegram Bot v2 başlatılıyor...")
    
    # Set UI Commands menu
    try:
        await set_bot_commands(bot)
    except Exception as e:
        logger.error(f"❌ Komut menüsü ayarlanırken hata: {e}")
        if "Unauthorized" in str(e):
            logger.critical("🛑 KRİTİK HATA: BOT_TOKEN geçersiz! Lütfen .env dosyasını kontrol edin.")
            # We don't exit, but the bot won't work anyway. 
            # This prevents the rapid crash-restart loop.

    # Start message sender queue
    message_sender = MessageSender(bot)
    await message_sender.start()

    # Launch background workers as asyncio tasks
    # User requested to stop automatic spam for whales and arbitrage (Conversation 5).
    # They will use the inline buttons / koinler menu instead.
    from config import VIP_CHANNEL_ID
    tasks = [
        asyncio.create_task(arbitrage_pubsub_worker(message_sender, VIP_CHANNEL_ID),  name="arbitrage_worker"),
        asyncio.create_task(news_pubsub_worker(message_sender),                      name="news_worker"),
        asyncio.create_task(ml_update_worker(message_sender),                        name="ml_worker"),
        asyncio.create_task(whale_pubsub_worker(message_sender, VIP_CHANNEL_ID),     name="whale_worker"),
        asyncio.create_task(alarm_checker_worker(bot),                               name="alarm_worker"),
        asyncio.create_task(kick_queue_worker(bot),                                  name="kick_worker"),
    ]

    # Start APScheduler
    scheduler = setup_scheduler(bot)
    scheduler.start()
    logger.info("📅 Scheduler started.")

    logger.info(f"🔧 {len(tasks)} background worker(s) launched.")
    logger.info("📡 Starting Telegram polling…")

    try:
        await dp.start_polling(
            bot,
            allowed_updates=["chat_member", "message", "callback_query"],
        )
    finally:
        logger.info("🛑 Shutting down gracefully…")
        scheduler.shutdown(wait=False)
        await message_sender.stop()
        for task in tasks:
            task.cancel()
        await asyncio.gather(*tasks, return_exceptions=True)
        await bot.session.close()
        logger.info("✅ Bot exited cleanly.")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logger.info("Bot manually stopped.")
