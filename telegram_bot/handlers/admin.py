"""
Admin panel handler — /admin command with inline keyboard.
All actions require the user's Telegram ID to be in ADMIN_IDS (env var).
"""
import logging

import aiohttp
import redis.asyncio as aioredis
from aiogram import Router, types, F
from aiogram.filters import Command

from config import ADMIN_IDS, REDIS_URL, VIP_CHANNEL_ID

logger = logging.getLogger(__name__)
router = Router()

INGESTION_BASE = "http://api_gateway:8000"


def _is_admin(user_id: int) -> bool:
    return user_id in ADMIN_IDS


def _admin_keyboard() -> types.InlineKeyboardMarkup:
    buttons = [
        [
            types.InlineKeyboardButton(text="👥 Kullanıcı Listesi", callback_data="admin:users"),
            types.InlineKeyboardButton(text="📊 Sistem Durumu",    callback_data="admin:status"),
        ],
        [
            types.InlineKeyboardButton(text="📢 Duyuru Yap",       callback_data="admin:broadcast_menu"),
            types.InlineKeyboardButton(text="⚙️ Tarayıcı Ayarları", callback_data="admin:scanner_settings"),
        ],
        [
            types.InlineKeyboardButton(text="🗑️ Kullanıcı Yasakla", callback_data="admin:ban_menu"),
            types.InlineKeyboardButton(text="⭐ Tier Güncelle",    callback_data="admin:tier_menu"),
        ],
        [
            types.InlineKeyboardButton(text="❌ Kapat",            callback_data="admin:close"),
        ],
    ]
    return types.InlineKeyboardMarkup(inline_keyboard=buttons)


# ─── /admin entry ────────────────────────────────────────────────────────────

@router.message(Command("admin"))
async def cmd_admin(message: types.Message):
    if not _is_admin(message.from_user.id):
        await message.answer("🚫 Bu komuta erişim yetkiniz yok.")
        return

    await message.answer(
        "🛸 <b>RadarPro Admin Paneli</b>\n\n"
        "Aşağıdan yapmak istediğiniz işlemi seçin:",
        parse_mode="HTML",
        reply_markup=_admin_keyboard()
    )


# ─── Callback dispatcher ─────────────────────────────────────────────────────

@router.callback_query(F.data.startswith("admin:"))
async def admin_callback(call: types.CallbackQuery):
    if not _is_admin(call.from_user.id):
        await call.answer("🚫 Yetkisiz erişim!", show_alert=True)
        return

    action = call.data.split(":", 1)[1]

    if action == "close":
        await call.message.delete()
        await call.answer()

    elif action == "status":
        await _admin_status(call)

    elif action == "users":
        await _admin_users(call)

    elif action == "broadcast_menu":
        await _admin_broadcast_prompt(call)

    elif action == "scanner_settings":
        await _admin_scanner_info(call)

    elif action == "ban_menu":
        await _admin_ban_prompt(call)

    elif action == "tier_menu":
        await _admin_tier_prompt(call)

    elif action == "back":
        await call.message.edit_text(
            "🛸 <b>RadarPro Admin Paneli</b>\n\nİşlem seçin:",
            parse_mode="HTML",
            reply_markup=_admin_keyboard()
        )
        await call.answer()

    else:
        await call.answer("Bilinmeyen işlem.")


# ─── Admin sub-actions ───────────────────────────────────────────────────────

async def _admin_status(call: types.CallbackQuery):
    await call.answer("📊 Sistem durumu yükleniyor...")

    status_lines = ["🖥️ <b>SİSTEM DURUMU (Admin)</b>", "━━━━━━━━━━━━━━━━━━━━━"]

    # Redis check
    try:
        redis = await aioredis.from_url(REDIS_URL, encoding="utf-8", decode_responses=True)
        await redis.ping()
        keys_count = len(await redis.keys("GOD_MODE_*"))
        alarm_count = len(await redis.keys("alarm:*"))
        await redis.aclose()
        status_lines.append(f"🟢 <b>Redis:</b> AKTİF")
        status_lines.append(f"   GOD_MODE Coinler: <code>{keys_count}</code>")
        status_lines.append(f"   Aktif Alarmlar: <code>{alarm_count}</code>")
    except Exception as e:
        status_lines.append(f"🔴 <b>Redis:</b> KAPALI ({e})")

    # API check
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(
                f"{INGESTION_BASE}/docs",
                timeout=aiohttp.ClientTimeout(total=3)
            ) as r:
                api_ok = r.status == 200
    except Exception:
        api_ok = False
    status_lines.append(f"{'🟢' if api_ok else '🔴'} <b>Ingestion API:</b> {'AKTİF' if api_ok else 'KAPALI'}")

    back_btn = types.InlineKeyboardMarkup(
        inline_keyboard=[[types.InlineKeyboardButton(text="◀️ Geri", callback_data="admin:back")]]
    )
    await call.message.edit_text(
        "\n".join(status_lines),
        parse_mode="HTML",
        reply_markup=back_btn
    )


async def _admin_users(call: types.CallbackQuery):
    await call.answer("👥 Kullanıcılar yükleniyor...")
    try:
        async with aiohttp.ClientSession() as session:
            # Use the /api/v1/auth/me endpoint — real user list needs a dedicated endpoint
            # For now show Redis tier cache stats
            pass

        redis = await aioredis.from_url(REDIS_URL, encoding="utf-8", decode_responses=True)
        tier_keys = await redis.keys("tg_tier:*")
        tiers = {}
        for k in tier_keys:
            tier = await redis.get(k)
            tiers[tier] = tiers.get(tier, 0) + 1
        await redis.aclose()

        lines = ["👥 <b>KULLANICI İSTATİSTİKLERİ</b>", "━━━━━━━━━━━━━━━━━━━━━"]
        for tier, count in sorted(tiers.items()):
            icon = {"VIP": "💎", "PREMIUM": "⭐", "FREE": "🆓"}.get(tier, "❓")
            lines.append(f"{icon} <b>{tier}:</b> {count} kullanıcı")
        if not tiers:
            lines.append("ℹ️ Henüz kayıtlı kullanıcı yoktur.")

    except Exception as e:
        lines = [f"❌ Kullanıcılar yüklenemedi: {e}"]

    back_btn = types.InlineKeyboardMarkup(
        inline_keyboard=[[types.InlineKeyboardButton(text="◀️ Geri", callback_data="admin:back")]]
    )
    await call.message.edit_text("\n".join(lines), parse_mode="HTML", reply_markup=back_btn)


async def _admin_broadcast_prompt(call: types.CallbackQuery):
    await call.message.edit_text(
        "📢 <b>Duyuru Yap</b>\n\n"
        "Tüm VIP kanalına mesaj göndermek için:\n\n"
        "<code>/broadcast Mesajınız buraya</code>\n\n"
        "komutu ile mesaj gönderebilirsiniz.",
        parse_mode="HTML",
        reply_markup=types.InlineKeyboardMarkup(
            inline_keyboard=[[types.InlineKeyboardButton(text="◀️ Geri", callback_data="admin:back")]]
        )
    )
    await call.answer()


async def _admin_scanner_info(call: types.CallbackQuery):
    await call.answer("⚙️ Tarayıcı bilgileri yükleniyor...")

    try:
        redis = await aioredis.from_url(REDIS_URL, encoding="utf-8", decode_responses=True)
        arb_keys = await redis.keys("GOD_MODE_*")
        await redis.aclose()
        keys_info = f"Aktif coin akışı: <code>{len(arb_keys)}</code>"
    except Exception:
        keys_info = "Redis bilgisi alınamadı."

    await call.message.edit_text(
        "⚙️ <b>ARBİTRAJ TARAYICI AYARLARI</b>\n\n"
        f"{keys_info}\n\n"
        "⚠️ Eşik ve tarama sıklığı için .env dosyasını düzenleyin:\n"
        "<code>ARBITRAGE_THRESHOLD_PCT</code> (şu an %0.15)\n"
        "<code>WHALE_WALL_USD</code> (şu an $5,000,000)",
        parse_mode="HTML",
        reply_markup=types.InlineKeyboardMarkup(
            inline_keyboard=[[types.InlineKeyboardButton(text="◀️ Geri", callback_data="admin:back")]]
        )
    )


async def _admin_ban_prompt(call: types.CallbackQuery):
    await call.message.edit_text(
        "🗑️ <b>Kullanıcı Yasakla</b>\n\n"
        "Kullanıcıyı kanaldan atmak için:\n\n"
        "<code>/kick &lt;TELEGRAM_USER_ID&gt;</code>\n\n"
        "Örnek: <code>/kick 123456789</code>",
        parse_mode="HTML",
        reply_markup=types.InlineKeyboardMarkup(
            inline_keyboard=[[types.InlineKeyboardButton(text="◀️ Geri", callback_data="admin:back")]]
        )
    )
    await call.answer()


async def _admin_tier_prompt(call: types.CallbackQuery):
    await call.message.edit_text(
        "⭐ <b>Tier Güncelleme</b>\n\n"
        "Kullanıcı tier'ını güncellemek için:\n\n"
        "<code>/settier &lt;EMAIL&gt; &lt;TIER&gt;</code>\n\n"
        "Örnek: <code>/settier user@mail.com VIP</code>\n"
        "Geçerli tier'lar: <code>FREE</code>, <code>PREMIUM</code>, <code>VIP</code>",
        parse_mode="HTML",
        reply_markup=types.InlineKeyboardMarkup(
            inline_keyboard=[[types.InlineKeyboardButton(text="◀️ Geri", callback_data="admin:back")]]
        )
    )
    await call.answer()


# ─── /broadcast command ───────────────────────────────────────────────────────

@router.message(Command("broadcast"))
async def cmd_broadcast(message: types.Message):
    if not _is_admin(message.from_user.id):
        await message.answer("🚫 Yetkisiz erişim.")
        return

    parts = message.text.split(maxsplit=1)
    if len(parts) < 2:
        await message.answer("⚠️ Kullanım: <code>/broadcast Mesajınız</code>", parse_mode="HTML")
        return

    broadcast_text = (
        f"📢 <b>RADARPRO DUYURUSU</b>\n"
        f"━━━━━━━━━━━━━━━━━━━━━\n"
        f"{parts[1]}\n"
        f"━━━━━━━━━━━━━━━━━━━━━\n"
        f"📡 <i>@RadarPro_Intelligence_Bot</i>"
    )

    try:
        await message.bot.send_message(
            chat_id=VIP_CHANNEL_ID,
            text=broadcast_text,
            parse_mode="HTML"
        )
        await message.answer("✅ Duyuru VIP kanalına gönderildi.")
    except Exception as e:
        await message.answer(f"❌ Gönderim hatası: {e}")


# ─── /kick command ────────────────────────────────────────────────────────────

@router.message(Command("kick"))
async def cmd_kick(message: types.Message):
    if not _is_admin(message.from_user.id):
        await message.answer("🚫 Yetkisiz erişim.")
        return

    parts = message.text.split()
    if len(parts) < 2 or not parts[1].lstrip("-").isdigit():
        await message.answer("⚠️ Kullanım: <code>/kick 123456789</code>", parse_mode="HTML")
        return

    user_id = int(parts[1])
    try:
        redis = await aioredis.from_url(REDIS_URL, encoding="utf-8", decode_responses=True)
        import json
        await redis.lpush("kick_queue", json.dumps({"user_id": user_id}))
        await redis.aclose()
        await message.answer(f"✅ Kullanıcı {user_id} kick kuyruğuna eklendi.")
    except Exception as e:
        await message.answer(f"❌ Kick işlemi başarısız: {e}")


# ─── /setier command ──────────────────────────────────────────────────────────

@router.message(Command("setier"))
async def cmd_setier(message: types.Message):
    if not _is_admin(message.from_user.id):
        await message.answer("🚫 Yetkisiz erişim.")
        return

    parts = message.text.split()
    if len(parts) < 3:
        await message.answer(
            "⚠️ Kullanım: <code>/setier user@mail.com VIP</code>",
            parse_mode="HTML"
        )
        return

    email    = parts[1]
    new_tier = parts[2].upper()

    if new_tier not in ("FREE", "PREMIUM", "VIP"):
        await message.answer("❌ Geçersiz tier. Kullanın: FREE, PREMIUM, VIP")
        return

    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{INGESTION_BASE}/api/v1/auth/admin_update_tier",
                json={"email": email, "new_tier": new_tier},
                timeout=aiohttp.ClientTimeout(total=10)
            ) as r:
                result = await r.json()

        if result.get("status") == "success":
            await message.answer(f"✅ <b>{email}</b> hesabı → <b>{new_tier}</b> yapıldı.", parse_mode="HTML")
        else:
            await message.answer(f"❌ Güncelleme başarısız: {result}")
    except Exception as e:
        await message.answer(f"❌ API hatası: {e}")

# ─── /grantvip command (Direct TG ID) ────────────────────────────────────────

@router.message(Command("grantvip"))
async def cmd_grantvip(message: types.Message):
    if not _is_admin(message.from_user.id):
        await message.answer("🚫 Yetkisiz erişim.")
        return

    parts = message.text.split()
    if len(parts) < 2 or not parts[1].isdigit():
        await message.answer("⚠️ Kullanım: <code>/grantvip &lt;TELEGRAM_ID&gt;</code>\nÖrnek: <code>/grantvip 123456789</code>", parse_mode="HTML")
        return

    target_id = int(parts[1])

    try:
        redis = await aioredis.from_url(REDIS_URL, encoding="utf-8", decode_responses=True)
        await redis.set(f"tg_tier:{target_id}", "VIP")
        await redis.aclose()
        await message.answer(f"✅ Başarılı! <code>{target_id}</code> ID'li kullanıcıya <b>💎 VIP</b> yetkisi verildi.", parse_mode="HTML")
    except Exception as e:
        await message.answer(f"❌ Redis hatası: {e}")

# ─── Radar Control Commands ──────────────────────────────────────────────────

@router.message(Command("start_radar"))
async def cmd_start_radar(message: types.Message):
    if not _is_admin(message.from_user.id): return
    try:
        redis = await aioredis.from_url(REDIS_URL, encoding="utf-8", decode_responses=True)
        await redis.delete("global_scanner_paused")
        await redis.aclose()
        await message.answer("🟢 <b>Radar Sinyalleri Başlatıldı!</b>\nArtık arbitraj ve balina sinyalleri akmaya başlayacak.", parse_mode="HTML")
    except Exception as e:
        await message.answer(f"❌ Hata: {e}")

@router.message(Command("stop_radar"))
async def cmd_stop_radar(message: types.Message):
    if not _is_admin(message.from_user.id): return
    try:
        redis = await aioredis.from_url(REDIS_URL, encoding="utf-8", decode_responses=True)
        await redis.set("global_scanner_paused", "1")
        await redis.aclose()
        await message.answer("🔴 <b>Radar Sinyalleri Durduruldu!</b>\nSiz tekrar açana kadar sinyal gelmeyecek.", parse_mode="HTML")
    except Exception as e:
        await message.answer(f"❌ Hata: {e}")

# ─── Data Export Command ─────────────────────────────────────────────────────

@router.message(Command("export_csv"))
async def cmd_export_csv(message: types.Message):
    if not _is_admin(message.from_user.id): return
    wait_msg = await message.answer("📥 Veritabanı hazırlanıyor, lütfen bekleyin...")
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(
                f"{INGESTION_BASE}/api/v1/admin/export_data",
                headers={"X-API-Key": os.getenv("BOT_API_KEY")},
                timeout=30
            ) as r:
                if r.status == 200:
                    content = await r.read()
                    file = types.BufferedInputFile(content, filename="market_data_export.csv")
                    await message.answer_document(file, caption="📊 Son piyasa verileri dışa aktarıldı.")
                else:
                    await message.answer(f"❌ Veri alınamadı: HTTP {r.status}")
        await wait_msg.delete()
    except Exception as e:
        await message.answer(f"❌ Export hatası: {e}")
