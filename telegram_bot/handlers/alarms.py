"""
Price alarm handlers: /alarm ekle, /alarm listele, /alarm sil
Alarms stored in Redis with key: alarm:{user_id}:{symbol}:{target}:{direction}
"""
import logging

import redis.asyncio as aioredis
from aiogram import Router, types
from aiogram.filters import Command

from config import REDIS_URL

logger = logging.getLogger(__name__)
router = Router()

MAX_ALARMS_PER_USER = 10


@router.message(Command("alarm"))
async def cmd_alarm(message: types.Message):
    """
    Usage:
      /alarm ekle BTCUSDT 80000 üst   → trigger when price >= 80000
      /alarm ekle ETHUSDT 3000 alt    → trigger when price <= 3000
      /alarm listele
      /alarm sil BTCUSDT 80000
    """
    parts = message.text.strip().split()

    if len(parts) < 2:
        await _show_alarm_help(message)
        return

    sub = parts[1].lower()

    if sub == "ekle":
        await _add_alarm(message, parts[2:])
    elif sub == "listele":
        await _list_alarms(message)
    elif sub == "sil":
        await _delete_alarm(message, parts[2:])
    else:
        await _show_alarm_help(message)


async def _show_alarm_help(message: types.Message):
    await message.answer(
        "🔔 <b>Fiyat Alarm Komutları</b>\n\n"
        "<code>/alarm ekle BTCUSDT 80000 üst</code>\n"
        "   → Fiyat 80,000$ üstüne çıkınca bildir\n\n"
        "<code>/alarm ekle ETHUSDT 3000 alt</code>\n"
        "   → Fiyat 3,000$ altına inince bildir\n\n"
        "<code>/alarm listele</code>\n"
        "   → Tüm aktif alarmlarınızı göster\n\n"
        "<code>/alarm sil BTCUSDT 80000</code>\n"
        "   → Belirli bir alarmı sil\n",
        parse_mode="HTML"
    )


async def _add_alarm(message: types.Message, args: list):
    if len(args) < 3:
        await message.answer(
            "⚠️ Eksik parametre!\n"
            "Örnek: <code>/alarm ekle BTCUSDT 80000 üst</code>",
            parse_mode="HTML"
        )
        return

    symbol    = args[0].upper()
    direction_raw = args[2].lower()

    try:
        target = float(args[1])
    except ValueError:
        await message.answer("❌ Geçersiz fiyat değeri.", parse_mode="HTML")
        return

    if direction_raw in ("üst", "ust", "üstü", "up", "yukari", "yukarı"):
        direction = "up"
        dir_label = "📈 üstüne çıkınca"
    elif direction_raw in ("alt", "down", "aşağı", "asagi"):
        direction = "down"
        dir_label = "📉 altına inince"
    else:
        await message.answer(
            "❌ Yön belirtin: <code>üst</code> veya <code>alt</code>",
            parse_mode="HTML"
        )
        return

    user_id = message.from_user.id

    try:
        redis = await aioredis.from_url(REDIS_URL, encoding="utf-8", decode_responses=True)

        # Count existing alarms
        existing = await redis.keys(f"alarm:{user_id}:*")
        if len(existing) >= MAX_ALARMS_PER_USER:
            await redis.aclose()
            await message.answer(
                f"⚠️ Maksimum alarm sınırına ({MAX_ALARMS_PER_USER}) ulaştınız.\n"
                "Önce bir alarmı silin.",
                parse_mode="HTML"
            )
            return

        key = f"alarm:{user_id}:{symbol}:{target}:{direction}"
        await redis.set(key, "1", ex=86400 * 30)  # 30 day TTL
        await redis.aclose()

        await message.answer(
            f"✅ <b>Alarm Kuruldu!</b>\n\n"
            f"💎 <b>Sembol:</b> <code>{symbol}</code>\n"
            f"🎯 <b>Hedef:</b> <code>${target:,.2f}</code> {dir_label}\n\n"
            f"Fiyat bu seviyeye ulaştığında <b>özel mesaj</b> alacaksınız.",
            parse_mode="HTML"
        )

    except Exception as e:
        logger.error(f"Add alarm error: {e}")
        await message.answer("❌ Alarm kaydedilemedi, lütfen tekrar deneyin.", parse_mode="HTML")


async def _list_alarms(message: types.Message):
    user_id = message.from_user.id
    try:
        redis = await aioredis.from_url(REDIS_URL, encoding="utf-8", decode_responses=True)
        keys = await redis.keys(f"alarm:{user_id}:*")
        await redis.aclose()

        if not keys:
            await message.answer(
                "🔔 Aktif fiyat alarminiz bulunmuyor.\n\n"
                "Eklemek için: <code>/alarm ekle BTCUSDT 80000 üst</code>",
                parse_mode="HTML"
            )
            return

        lines = ["🔔 <b>AKTİF FİYAT ALARMLARI</b>", "━━━━━━━━━━━━━━━━━━━━━"]
        for key in keys:
            parts = key.split(":")
            if len(parts) == 5:
                _, _, symbol, target, direction = parts
                dir_icon = "📈" if direction == "up" else "📉"
                dir_text = "üstüne geçince" if direction == "up" else "altına inince"
                lines.append(
                    f"{dir_icon} <b>{symbol}</b> — <code>${float(target):,.2f}</code> {dir_text}"
                )
        lines.append("━━━━━━━━━━━━━━━━━━━━━")
        lines.append(f"Toplam: {len(keys)}/{MAX_ALARMS_PER_USER} alarm")
        await message.answer("\n".join(lines), parse_mode="HTML")

    except Exception as e:
        logger.error(f"List alarms error: {e}")
        await message.answer("❌ Alarmlar listelenemedi.", parse_mode="HTML")


async def _delete_alarm(message: types.Message, args: list):
    if len(args) < 2:
        await message.answer(
            "⚠️ Kullanım: <code>/alarm sil BTCUSDT 80000</code>",
            parse_mode="HTML"
        )
        return

    symbol = args[0].upper()
    try:
        target = float(args[1])
    except ValueError:
        await message.answer("❌ Geçersiz fiyat değeri.", parse_mode="HTML")
        return

    user_id = message.from_user.id
    try:
        redis = await aioredis.from_url(REDIS_URL, encoding="utf-8", decode_responses=True)
        deleted = 0
        for direction in ("up", "down"):
            key = f"alarm:{user_id}:{symbol}:{target}:{direction}"
            deleted += await redis.delete(key)
        await redis.aclose()

        if deleted:
            await message.answer(
                f"✅ <b>{symbol}</b> ${target:,.2f} alarmı silindi.",
                parse_mode="HTML"
            )
        else:
            await message.answer(
                f"⚠️ <b>{symbol}</b> ${target:,.2f} için aktif alarm bulunamadı.",
                parse_mode="HTML"
            )

    except Exception as e:
        logger.error(f"Delete alarm error: {e}")
        await message.answer("❌ Alarm silinemedi.", parse_mode="HTML")
