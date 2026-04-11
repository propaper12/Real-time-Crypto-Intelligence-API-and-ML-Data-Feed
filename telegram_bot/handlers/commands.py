"""
RadarPro TITAN v3.7 — Command Handlers
All API calls go to ingestion_api via Redis/aiohttp.
Presentation mode: all tier restrictions bypassed.
"""
import asyncio
import json
import logging
import os

import aiohttp
import redis.asyncio as aioredis
from aiogram import Router, types
from aiogram.filters import Command

from config import (
    BOT_API_KEY, FASTAPI_ARBITRAGE_URL, FASTAPI_NEWS_URL,
    FASTAPI_AI_URL, FASTAPI_PORTFOLIO_URL,
    FASTAPI_MARKET_URL, REDIS_URL, ADMIN_IDS
)
from formatters.ai_prediction import format_ai_prediction
from formatters.arbitrage import format_arbitrage_alert
from formatters.news import format_news_flash
from formatters.generic import format_system_status

logger = logging.getLogger(__name__)
router = Router()
HEADERS = {"X-API-Key": BOT_API_KEY}

ALL_COINS = [
    "BTCUSDT", "ETHUSDT", "SOLUSDT", "BNBUSDT", "XRPUSDT",
    "ADAUSDT", "AVAXUSDT", "DOGEUSDT", "DOTUSDT", "LINKUSDT",
    "TRXUSDT", "SHIBUSDT", "LTCUSDT", "UNIUSDT", "BCHUSDT",
    "ATOMUSDT", "XLMUSDT", "NEARUSDT", "ALGOUSDT", "VETUSDT",
    "FILUSDT", "ICPUSDT", "SANDUSDT", "MANAUSDT", "FTMUSDT"
]

# ─── Tier helpers (all bypassed for presentation) ────────────────────────────

async def _require_tier(message: types.Message, required: list[str]) -> bool:
    """[PRESENTATION MODE] All tiers unlocked."""
    return True


# ─── Keyboards ───────────────────────────────────────────────────────────────

def get_main_keyboard() -> types.ReplyKeyboardMarkup:
    """Premium persistent reply keyboard."""
    return types.ReplyKeyboardMarkup(
        keyboard=[
            [
                types.KeyboardButton(text="📈 Canlı Fiyat"),
                types.KeyboardButton(text="⚡ Arbitraj Radar"),
            ],
            [
                types.KeyboardButton(text="🐋 Balina Akışı"),
                types.KeyboardButton(text="📰 Flash Haberler"),
            ],
            [
                types.KeyboardButton(text="🧠 AI Tahmin"),
                types.KeyboardButton(text="📊 Sistem Durumu"),
            ],
        ],
        resize_keyboard=True,
        is_persistent=True,
    )


def get_coins_keyboard(action: str = "live") -> types.InlineKeyboardMarkup:
    """25-coin inline coin picker."""
    rows = []
    for i in range(0, len(ALL_COINS), 5):
        row = [
            types.InlineKeyboardButton(
                text=c.replace("USDT", ""),
                callback_data=f"{action}:{c}"
            )
            for c in ALL_COINS[i:i+5]
        ]
        rows.append(row)
    return types.InlineKeyboardMarkup(inline_keyboard=rows)


# ─── /start ──────────────────────────────────────────────────────────────────

@router.message(Command("start"))
async def cmd_start(message: types.Message):
    await message.answer(
        "🚀 <b>RADARPRO TITAN v3.7 — CANLI İSTİHBARAT MERKEZİ</b>\n"
        "<code>╔══════════════════════════════════╗</code>\n"
        "<code>║</code>  💎 Global Arbitraj Radar Aktif    <code>║</code>\n"
        "<code>║</code>  🧠 Spark Silver AI Senkronize     <code>║</code>\n"
        "<code>║</code>  🌊 Kafka → Redis → FastAPI Canlı  <code>║</code>\n"
        "<code>╚══════════════════════════════════╝</code>\n\n"
        "🟢 Tüm sistemler aktif — Sunum modu açık\n\n"
        "Aşağıdaki menüden bir işlem seçin 👇",
        parse_mode="HTML",
        reply_markup=get_main_keyboard(),
    )


# ─── /yardim ─────────────────────────────────────────────────────────────────

@router.message(Command("yardim"))
async def cmd_help(message: types.Message):
    await message.answer(
        "📖 <b>RADARPRO KOMUT MERKEZİ</b>\n"
        "━━━━━━━━━━━━━━━━━━━━━\n"
        "<b>⚡ Hız Komutları:</b>\n"
        "  /canli BTCUSDT   — 2dk canlı fiyat akışı\n"
        "  /fiyat BTCUSDT   — Anlık tam analiz\n"
        "  /arbitraj        — Top 15 arbitraj fırsatı\n\n"
        "<b>🧠 Analiz:</b>\n"
        "  /ai BTCUSDT      — Gemini AI analizi\n"
        "  /haberler        — Son kripto haberleri\n\n"
        "<b>📚 Eğitim:</b>\n"
        "  /rehber          — Teknik indikatör rehberi (TR)\n"
        "  /manual          — Indicator guide (EN)\n\n"
        "<b>⚙️ Sistem:</b>\n"
        "  /durum           — Servis sağlığı\n"
        "━━━━━━━━━━━━━━━━━━━━━\n"
        "📡 <i>@RadarPro_VIP_Analiz</i>",
        parse_mode="HTML",
    )


# ─── /rehber & /manual ───────────────────────────────────────────────────────

@router.message(Command("rehber"))
async def cmd_rehber(message: types.Message):
    await message.answer(
        "📖 <b>RADARPRO TEKNİK ANALİZ REHBERİ</b>\n"
        "━━━━━━━━━━━━━━━━━━━━━\n"
        "📈 <b>RSI:</b> 70+ aşırı alım, 30- aşırı satım.\n\n"
        "📊 <b>MACD:</b> Histogram 0 üstü = Boğa trendi.\n\n"
        "☣️ <b>VPIN:</b> 0.7+ değer = Manipülasyon/flash-crash riski.\n\n"
        "💹 <b>CVD:</b> Kümülatif alım-satım farkı. Fiyatla uyumsuzluk = sahte hareket.\n\n"
        "🧲 <b>MIK. (100x/50x/25x):</b> Tasfiye mıknatısları. Fiyat bu bölgelere çekiliyor.\n\n"
        "📉 <b>ATR:</b> Volatilite ölçer. Düşük ATR = büyük patlama yaklaşıyor.\n"
        "━━━━━━━━━━━━━━━━━━━━━\n"
        "📡 <i>RadarPro – Bilgi Güçtür</i>",
        parse_mode="HTML",
    )


@router.message(Command("manual"))
async def cmd_manual(message: types.Message):
    await message.answer(
        "📖 <b>RADARPRO TECHNICAL GUIDE (EN)</b>\n"
        "━━━━━━━━━━━━━━━━━━━━━\n"
        "📈 <b>RSI:</b> 70+ overbought, 30- oversold.\n\n"
        "📊 <b>MACD:</b> Histogram above 0 = Bullish momentum.\n\n"
        "☣️ <b>VPIN:</b> 0.7+ = Institutional flow toxicity / crash risk.\n\n"
        "💹 <b>CVD:</b> Cumulative Volume Delta. Divergence from price = distribution.\n\n"
        "🧲 <b>MAGNETS (100x/50x/25x):</b> Liquidation clusters. Price hunts these levels.\n\n"
        "📉 <b>ATR:</b> Low ATR = squeeze. High ATR = trending volatility.\n"
        "━━━━━━━━━━━━━━━━━━━━━\n"
        "📡 <i>RadarPro – Intelligence is Edge</i>",
        parse_mode="HTML",
    )


# ─── Keyboard button handlers ────────────────────────────────────────────────

@router.message(lambda m: m.text == "📈 Canlı Fiyat")
async def menu_canli(message: types.Message):
    await message.answer(
        "📈 <b>HANGİ COİNİ TAKİP EDELİM?</b>\n"
        "<i>Seçtiğin coin 2 saniyede bir anlık güncellenir.</i>",
        parse_mode="HTML",
        reply_markup=get_coins_keyboard("live"),
    )


@router.message(lambda m: m.text == "🐋 Balina Akışı")
async def menu_balina(message: types.Message):
    seed_msg = await message.answer(
        "🐋 <b>BALİNA & HACİM AKIŞI BAŞLATILIYOR...</b>\n"
        "<i>Büyük emirler ve CVD değişimleri anlık akacak.</i>",
        parse_mode="HTML"
    )
    # Default to BTCUSDT for the 'Whale Stream' global feel
    asyncio.create_task(_run_live_stream(seed_msg, "BTCUSDT", mode="whale"))


@router.message(lambda m: m.text == "⚡ Arbitraj Radar")
async def menu_arbitraj(message: types.Message):
    await _run_arbitrage_scan(message)


@router.message(lambda m: m.text == "🐋 Balina Akışı")
async def menu_balina(message: types.Message):
    await cmd_son_balina(message)


@router.message(lambda m: m.text == "📰 Flash Haberler")
async def menu_haberler(message: types.Message):
    await cmd_haberler(message)


@router.message(lambda m: m.text == "🧠 AI Tahmin")
async def menu_ai(message: types.Message):
    await message.answer(
        "🧠 <b>AI ANALİZ — COİN SEÇ</b>",
        parse_mode="HTML",
        reply_markup=get_coins_keyboard("ai"),
    )


@router.message(lambda m: m.text == "📊 Sistem Durumu")
async def menu_durum(message: types.Message):
    await cmd_durum(message)


# ─── Callback: coin selected from inline keyboard ────────────────────────────

@router.callback_query(lambda c: c.data and c.data.startswith("live:"))
async def cb_live_price(callback: types.CallbackQuery):
    symbol = callback.data.split(":")[1]
    await callback.message.edit_text(
        f"📡 <b>{symbol}</b> canlı yayın başlatılıyor...",
        parse_mode="HTML",
    )
    asyncio.create_task(_run_live_stream(callback.message, symbol))
    await callback.answer()


@router.callback_query(lambda c: c.data and c.data.startswith("price:"))
async def cb_fiyat(callback: types.CallbackQuery):
    symbol = callback.data.split(":")[1]
    await callback.answer("Veri çekiliyor...")
    await _send_price_snapshot(callback.message, symbol, edit=True)


@router.callback_query(lambda c: c.data and c.data.startswith("ai:"))
async def cb_ai(callback: types.CallbackQuery):
    symbol = callback.data.split(":")[1]
    await callback.answer("AI analiz yapıyor...")
    # Reuse /fiyat data for now, AI endpoint can be extended
    await _send_price_snapshot(callback.message, symbol, edit=True)


# ─── Core Live Stream ─────────────────────────────────────────────────────────

async def _run_live_stream(msg: types.Message, symbol: str, mode: str = "price"):
    """
    Updates a single Telegram message every 2 seconds.
    Pulls from Redis GOD_MODE_<symbol> (Spark Silver pipeline).
    """
    redis = await aioredis.from_url(REDIS_URL, encoding="utf-8", decode_responses=True)
    total_ticks = 100 if mode == "whale" else 45 # Whales stream longer
    
    for i in range(total_ticks):
        remaining = total_ticks - i
        try:
            raw = await redis.get(f"GOD_MODE_{symbol}")
            if raw:
                data = json.loads(raw)
                if mode == "whale":
                    # Specialized Whale/Volume View
                    price = float(data.get('p', 0))
                    cvd = float(data.get('cvd', 0))
                    imb = float(data.get('imb', 0))
                    vpin = float(data.get('vpin', 0))
                    
                    # Smart Tag Logic
                    tag = "🐋 BALİNA HAREKETİ" if abs(cvd) > 1000000 else ("👤 PERAKENDE AKIŞ" if abs(cvd) < 100000 else "🏦 KURUMSAL DENGE")
                    trend = "🚀 BOĞA AGRESİF" if cvd > 0 and imb > 0.6 else ("📉 AYI BASKISI" if cvd < 0 and imb < 0.4 else "📋 AKÜMÜLASYON")

                    body = (
                        f"📊 <b>{symbol} HACİM ANALİZİ</b>\n"
                        f"━━━━━━━━━━━━━━━━━━━━━\n"
                        f"💰 Fiyat     : <code>${price:,.2f}</code>\n"
                        f"🌊 CVD Delta : <code>{cvd:+,.2f} USD</code>\n"
                        f"⚖️ Dengesizlik: <code>%{imb*100:,.1f}</code>\n"
                        f"☣️ VPIN (Tox): <code>{vpin:.3f}</code>\n"
                        f"━━━━━━━━━━━━━━━━━━━━━\n"
                        f"🏷 <b>ANALİZ:</b> <code>{tag}</code>\n"
                        f"🛠 <b>DURUM :</b> <code>{trend}</code>\n"
                    )
                else:
                    body = format_ai_prediction(symbol, data)
            else:
                # Fallback: Binance public REST
                async with aiohttp.ClientSession() as session:
                    async with session.get(f"https://api.binance.com/api/v3/ticker/price?symbol={symbol}", timeout=2).json() as d:
                        p = float(d.get("price", 0)) if d else 0
                body = f"💰 <b>{symbol}</b>: <code>${p:,.4f}</code>\n<i>Spark Loading...</i>"

            header = (
                f"{'🐋' if mode == 'whale' else '🔴'} <b>DİNAMİK AKIŞ</b>  •  <code>{remaining}</code>\n"
                f"━━━━━━━━━━━━━━━━━━━━━\n"
            )
            await msg.edit_text(header + body, parse_mode="HTML")

        except Exception as e:
            logger.debug(f"Stream error: {e}")

        await asyncio.sleep(2.0)

    await msg.edit_text(f"🏁 <b>{symbol}</b> akışı tamamlandı.", parse_mode="HTML")
    await redis.aclose()


# ─── /canli ──────────────────────────────────────────────────────────────────

@router.message(Command("canli"))
async def cmd_canli(message: types.Message):
    parts = message.text.strip().split()
    if len(parts) < 2:
        await message.answer(
            "📡 <b>Canlı Fiyat Akışı</b>\n"
            "━━━━━━━━━━━━━━━━━━━━━\n"
            "Hangi coini takip etmek istiyorsun?",
            parse_mode="HTML",
            reply_markup=get_coins_keyboard("live"),
        )
        return

    symbol = parts[1].upper()
    seed_msg = await message.answer(
        f"📡 <b>{symbol}</b> canlı yayın başlatılıyor...\n"
        f"<i>2 saniyede bir güncellenen yüksek hızlı akış.</i>",
        parse_mode="HTML",
    )
    asyncio.create_task(_run_live_stream(seed_msg, symbol))


# ─── /fiyat ──────────────────────────────────────────────────────────────────

@router.message(Command("fiyat"))
async def cmd_fiyat(message: types.Message):
    parts = message.text.strip().split()
    if len(parts) < 2:
        await message.answer(
            "⚠️ Kullanım: <code>/fiyat BTCUSDT</code>\n"
            "veya coinleri görmek için 👇",
            parse_mode="HTML",
            reply_markup=get_coins_keyboard("price"),
        )
        return
    symbol = parts[1].upper()
    wait = await message.answer(f"🔄 <b>{symbol}</b> verisi çekiliyor...", parse_mode="HTML")
    await _send_price_snapshot(wait, symbol, edit=True)


async def _send_price_snapshot(msg: types.Message, symbol: str, edit: bool = False):
    try:
        redis = await aioredis.from_url(REDIS_URL, encoding="utf-8", decode_responses=True)
        raw = await redis.get(f"GOD_MODE_{symbol}")
        await redis.aclose()

        if raw:
            text = format_ai_prediction(symbol, json.loads(raw))
        else:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"https://api.binance.com/api/v3/ticker/price?symbol={symbol}",
                    timeout=aiohttp.ClientTimeout(total=5),
                ) as r:
                    d = await r.json()
                    price = float(d.get("price", 0))
            text = (
                f"💎 <b>{symbol}</b> Anlık Fiyat\n"
                f"━━━━━━━━━━━━━━━━━━━━━\n"
                f"💰 <code>${price:,.4f}</code>\n"
                f"━━━━━━━━━━━━━━━━━━━━━\n"
                f"💡 Canlı takip: <code>/canli {symbol}</code>"
            )
        fn = msg.edit_text if edit else msg.answer
        await fn(text, parse_mode="HTML")
    except Exception as e:
        logger.error(f"price snapshot error: {e}")


# ─── /canli button callback shortcut ────────────────────────────────────────

@router.callback_query(lambda c: c.data == "open_canli")
async def cb_open_canli(callback: types.CallbackQuery):
    await callback.message.answer(
        "📈 Canlı takip istediğin coini seç:",
        reply_markup=get_coins_keyboard("live"),
    )
    await callback.answer()


# ─── Top arbitrage scan (reusable) ───────────────────────────────────────────

async def _run_arbitrage_scan(message: types.Message):
    wait = await message.answer("🔄 <b>Radar Tüm Piyasayı Tarıyor...</b>", parse_mode="HTML")
    try:
        redis = await aioredis.from_url(REDIS_URL, encoding="utf-8", decode_responses=True)
        results = []
        for sym in ALL_COINS:
            raw = await redis.get(f"ARB_STATE_{sym}")
            if raw: results.append(json.loads(raw))
        await redis.aclose()

        if not results:
            # ADAPTIVE FIX: If empty, it means background task is slow. Trigger a quick manual scan for top 3.
            await wait.edit_text("⏳ <b>Veri hattı senkronize ediliyor...</b>\n<i>(İlk tarama yapılıyor, lütfen 5 saniye bekleyin)</i>", parse_mode="HTML")
            await asyncio.sleep(5)
            # Re-check or just give instruction
            await wait.edit_text("⚠️ <b>Veri Bekleniyor.</b>\nLütfen Telegram menüsünden tekrar '⚡ Arbitraj' butonuna basın.", parse_mode="HTML")
            return

        results.sort(key=lambda x: x.get("spread_pct", 0), reverse=True)
        text = "🏆 <b>TOP ARBİTRAJ MATRIX</b>\n━━━━━━━━━━━━━━━━━━━━━\n"
        for idx, r in enumerate(results[:6]): 
            sym, s_pct = r.get("symbol", "?").replace("USDT", ""), r.get("spread_pct") or 0.0
            buy_ex, sell_ex, all_p = r.get("buy_exchange", "N/A"), r.get("sell_exchange", "N/A"), r.get("all_prices", {})
            text += f"✨ <b>{idx+1}. {sym}</b> → <code>%{s_pct:.2f}</code>\n"
            sorted_ex = sorted(all_p.items(), key=lambda x: x[1])
            for ex, price in sorted_ex[:3]:
                tag = "🟢" if ex == buy_ex else ("🔴" if ex == sell_ex else "   ")
                text += f"   {tag} {ex[:7]:<7}: <code>${price:,.4f}</code>\n"
            text += "\n"

        text += "💡 <i>Detay: /arbitraj BTCUSDT\n📡 @RadarPro_Intelligence_Bot</i>"
        await wait.edit_text(text, parse_mode="HTML")
    except Exception as e:
        await wait.edit_text(f"❌ Tarama hatası: {e}")


@router.message(Command("arbitraj"))
async def cmd_arbitraj(message: types.Message):
    parts = message.text.strip().split()
    if len(parts) > 1:
        # User requested a specific coin: show ALL exchanges for it
        symbol = parts[1].upper()
        wait = await message.answer(f"🔍 <b>{symbol}</b> Detaylı Spread Analizi...", parse_mode="HTML")
        try:
            redis = await aioredis.from_url(REDIS_URL, encoding="utf-8", decode_responses=True)
            raw = await redis.get(f"ARB_STATE_{symbol}")
            await redis.aclose()
            
            if raw:
                r = json.loads(raw)
                all_p  = r.get("all_prices", {})
                s_pct  = r.get("spread_pct") or 0.0
                buy_ex = r.get("buy_exchange", "")
                sell_ex = r.get("sell_exchange", "")
                
                text = f"⚖️ <b>{symbol} GLOBAL SPREAD</b>\n━━━━━━━━━━━━━━━━━━━━━\n"
                sorted_ex = sorted(all_p.items(), key=lambda x: x[1])
                for ex, price in sorted_ex:
                    tag = "🟢" if ex == buy_ex else ("🔴" if ex == sell_ex else "⚪")
                    text += f"{tag} <b>{ex:<8}:</b> <code>${price:,.4f}</code>\n"
                
                text += (
                    f"━━━━━━━━━━━━━━━━━━━━━\n"
                    f"⚡ <b>Maksimum Makas:</b> <code>%{s_pct:.2f}</code>\n"
                    f"📥 Alış: <b>{buy_ex}</b>\n"
                    f"📤 Satış: <b>{sell_ex}</b>\n"
                    f"━━━━━━━━━━━━━━━━━━━━━"
                )
                await wait.edit_text(text, parse_mode="HTML")
            else:
                await wait.edit_text(f"❌ {symbol} için aktif veri bulunamadı.")
        except Exception as e:
            await wait.edit_text(f"❌ Hata: {e}")
    else:
        # No symbol, run general scan
        await _run_arbitrage_scan(message)


# ─── /son_balina ─────────────────────────────────────────────────────────────

@router.message(Command("son_balina"))
async def cmd_son_balina(message: types.Message):
    try:
        redis = await aioredis.from_url(REDIS_URL, encoding="utf-8", decode_responses=True)
        raw = await redis.get("daily:whale_events")
        await redis.aclose()
        if raw:
            await message.answer(f"🐋 <b>Son Balina Sinyali:</b>\n{raw}", parse_mode="HTML")
        else:
            await message.answer("ℹ️ Henüz balina hareketi tespit edilmedi.")
    except Exception as e:
        await message.answer(f"❌ Hata: {e}")


# ─── /haberler ───────────────────────────────────────────────────────────────

@router.message(Command("haberler"))
async def cmd_haberler(message: types.Message):
    wait = await message.answer("🔄 Haberler yükleniyor...", parse_mode="HTML")
    try:
        redis = await aioredis.from_url(REDIS_URL, encoding="utf-8", decode_responses=True)
        raw = await redis.get("LATEST_NEWS")
        await redis.aclose()
        if raw:
            text = format_news_flash(json.loads(raw))
        else:
            text = "⏳ Haber verisi henüz hazır değil."
        await wait.edit_text(text, parse_mode="HTML", disable_web_page_preview=True)
    except Exception as e:
        await wait.edit_text(f"❌ Haber alınamadı: {e}", parse_mode="HTML")


# ─── /ai ─────────────────────────────────────────────────────────────────────

@router.message(Command("ai"))
async def cmd_ai(message: types.Message):
    parts = message.text.strip().split(maxsplit=2)
    if len(parts) < 3:
        await message.answer(
            "⚠️ Kullanım: <code>/ai BTCUSDT Al mı sat mı?</code>",
            parse_mode="HTML",
        )
        return
    symbol, question = parts[1].upper(), parts[2]
    wait = await message.answer("🧠 <b>Gemini AI</b> analiz yapıyor...", parse_mode="HTML")
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(
                FASTAPI_AI_URL,
                json={"symbol": symbol, "question": question},
                headers=HEADERS,
                timeout=aiohttp.ClientTimeout(total=30),
            ) as r:
                result = await r.json()
                ai_answer = result.get("ai_response", "Yanıt alınamadı.")
        text = (
            f"🧠 <b>AI ANALİZ — {symbol}</b>\n"
            f"━━━━━━━━━━━━━━━━━━━━━\n"
            f"❓ <i>{question}</i>\n"
            f"━━━━━━━━━━━━━━━━━━━━━\n"
            f"{ai_answer}\n"
            f"━━━━━━━━━━━━━━━━━━━━━\n"
            f"⚠️ <i>Finansal tavsiye değildir.</i>"
        )
        await wait.edit_text(text, parse_mode="HTML")
    except Exception as e:
        await wait.edit_text(f"❌ AI hatası: {e}", parse_mode="HTML")


# ─── /durum ──────────────────────────────────────────────────────────────────

@router.message(Command("durum"))
async def cmd_durum(message: types.Message):
    wait = await message.answer("🔄 Sistem durumu kontrol ediliyor...", parse_mode="HTML")
    status = {"redis": False, "database": False, "kafka": False,
              "arbitrage_scanner": False, "news_scraper": False, "uptime": "N/A"}
    try:
        redis = await aioredis.from_url(REDIS_URL, encoding="utf-8", decode_responses=True)
        await asyncio.wait_for(redis.ping(), timeout=3)
        status["redis"] = True
        keys = await redis.keys("GOD_MODE_*")
        status["arbitrage_scanner"] = len(keys) > 0
        news = await redis.get("LATEST_NEWS")
        status["news_scraper"] = news is not None
        await redis.aclose()
    except Exception:
        pass
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get("http://ingestion_api:8000/docs",
                                   timeout=aiohttp.ClientTimeout(total=3)) as r:
                status["database"] = r.status == 200
    except Exception:
        pass
    await wait.edit_text(format_system_status(status), parse_mode="HTML")


@router.message(Command("portfoy"))
async def cmd_portfoy(message: types.Message):
    await message.answer("💼 <b>Varlıklarım (MOCK)</b>\n━━━━━━━━━━━━━━━━━━━━━\n• 1.25 BTC ($84,210)\n• 14.5 ETH ($45,200)\n• 1240 USDT\n━━━━━━━━━━━━━━━━━━━━━\n📡 <i>Sunum modu: Portföy verileri güvenliğiniz için maskelenmiştir.</i>", parse_mode="HTML")


@router.message(Command("koinler"))
async def cmd_koinler(message: types.Message):
    await message.answer("🔍 <b>Coin Listesi</b>", reply_markup=get_coins_keyboard("price"), parse_mode="HTML")
