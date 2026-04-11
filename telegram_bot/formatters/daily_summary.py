from datetime import datetime


def format_daily_summary(stats: dict) -> str:
    """
    Builds a visually rich daily summary report.
    stats keys: best_arbitrage, total_signals, whale_events,
                news_count, champion_model, r2, top_symbol,
                ml_update_count, date_str
    """
    date_str       = stats.get("date_str", datetime.now().strftime("%d %B %Y"))
    best_arb       = stats.get("best_arbitrage", {})
    total_signals  = stats.get("total_signals", 0)
    whale_events   = stats.get("whale_events", 0)
    news_count     = stats.get("news_count", 0)
    champion       = stats.get("champion_model", "N/A")
    r2             = stats.get("r2", 0)
    top_symbol     = stats.get("top_symbol", "N/A")
    ml_updates     = stats.get("ml_update_count", 0)

    best_symbol  = best_arb.get("symbol", "N/A")
    best_spread  = best_arb.get("spread_pct", 0)
    best_buy     = best_arb.get("buy_exchange", "N/A")
    best_sell    = best_arb.get("sell_exchange", "N/A")

    try:
        r2_bar = "🟩" * min(10, int(float(r2) * 10)) + "⬜" * (10 - min(10, int(float(r2) * 10)))
    except Exception:
        r2_bar = "⬜" * 10

    return (
        f"📋 <b>RADARPRO GÜNLÜK ÖZET</b>\n"
        f"📅 <b>{date_str}</b>\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"🔥 <b>En İyi Arbitraj:</b>\n"
        f"   <code>{best_symbol}</code> — <b>%{best_spread:.3f}</b>\n"
        f"   {best_buy} → {best_sell}\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"📊 <b>Toplam Arbitraj Sinyali:</b> <code>{total_signals}</code>\n"
        f"🐋 <b>Balina Hareketi:</b>         <code>{whale_events}</code>\n"
        f"📰 <b>Haber Güncelleme:</b>        <code>{news_count}</code>\n"
        f"🤖 <b>ML Model Güncellemesi:</b>   <code>{ml_updates}</code>\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"🏆 <b>Şampiyon Model:</b> <code>{champion}</code>\n"
        f"📈 <b>Model Doğruluğu:</b> {r2_bar}\n"
        f"    <code>R² = {r2}</code>\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"⭐ <b>En Aktif Coin:</b> <code>{top_symbol}</code>\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"📡 <i>@RadarPro_Intelligence_Bot • Her gün 20:00 UTC'de</i>"
    )
