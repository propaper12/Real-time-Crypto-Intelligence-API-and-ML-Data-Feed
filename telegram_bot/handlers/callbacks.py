from aiogram import Router, F, types
from aiogram.types import CallbackQuery
from .commands import cmd_radar_ai, cmd_menu
import json

router = Router()

@router.callback_query(F.data == "menu_main")
async def cb_main_menu(callback: CallbackQuery):
    await callback.message.edit_text("🖥️ <b>RadarPro Ana Menü</b>", parse_mode="HTML")
    from keyboards import get_main_menu_keyboard
    await callback.message.edit_reply_markup(reply_markup=get_main_menu_keyboard())

@router.callback_query(F.data == "menu_radarai")
async def cb_radar_ai(callback: CallbackQuery):
    # radarai komutunu manuel tetiklemiş gibi davran
    await cmd_radar_ai(callback.message)
    await callback.answer()

@router.callback_query(F.data == "menu_arbitrage")
async def cb_arbitrage(callback: CallbackQuery):
    from keyboards import get_arbitrage_keyboard
    await callback.message.edit_text("⚖️ <b>Arbitraj Merkezi</b>\n\nLütfen bir işlem seçin:", parse_mode="HTML", reply_markup=get_arbitrage_keyboard())

@router.callback_query(F.data == "arb_top5")
async def cb_arb_top5(callback: CallbackQuery):
    from config import REDIS_URL
    import redis.asyncio as aioredis
    
    redis = await aioredis.from_url(REDIS_URL, encoding="utf-8", decode_responses=True)
    keys = await redis.keys("ARB_STATE_*")
    opportunities = []
    for key in keys:
        raw = await redis.get(key)
        if raw: opportunities.append(json.loads(raw))
    await redis.aclose()

    if not opportunities:
        await callback.answer("⚠️ Şu an aktif fırsat bulunamadı.", show_alert=True)
        return

    opportunities.sort(key=lambda x: x.get("spread_pct", 0), reverse=True)
    top5 = opportunities[:5]
    
    text = "🔥 <b>EN KARLI 5 ARBİTRAJ FIRSATI</b>\n━━━━━━━━━━━━━━━━━━━━━\n"
    for o in top5:
        text += f"• <b>{o['symbol']}:</b> <code>%{o['spread_pct']:.2f}</code> ({o['buy_exchange']} ➔ {o['sell_exchange']})\n"
    
    text += "━━━━━━━━━━━━━━━━━━━━━\n📡 <i>Detaylı analiz için /arbitraj [coin] yazın.</i>"
    
    from keyboards import get_arbitrage_keyboard
    await callback.message.edit_text(text, parse_mode="HTML", reply_markup=get_arbitrage_keyboard())

@router.callback_query(F.data == "menu_market")
async def cb_market(callback: CallbackQuery):
    await callback.answer("📊 Piyasa durumu hazırlanıyor...", show_alert=False)
    # Gelecekte buraya genel piyasa verileri eklenebilir.
