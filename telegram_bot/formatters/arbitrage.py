from datetime import datetime


def format_arbitrage_alert(data: dict) -> str:
    """Premium multi-exchange arbitrage formatter matching terminal style."""
    symbol   = data.get("symbol", "UNKNOWN")
    spread   = data.get("spread_pct", 0)
    prices   = data.get("prices", {})
    min_ex   = data.get("min_exchange", data.get("buy_exchange", "N/A"))
    max_ex   = data.get("max_exchange", data.get("sell_exchange", "N/A"))
    ts       = data.get("timestamp", datetime.now().strftime("%H:%M:%S"))

    if spread >= 0.5:
        tier_icon = "🔥"
        tier_label = "YÜKSEK FIRSAT"
    else:
        tier_icon = "⚡"
        tier_label = "LİKİDİTE MAKASI"

    text = (
        f"⚖️ <b>GLOBAL ARBİTRAJ RADARI — {symbol}</b> {tier_icon}\n"
        f"━━━━━━━━━━━━━━━━━━━━━\n"
    )
    
    # Sort prices high to low
    sorted_p = sorted(prices.items(), key=lambda x: x[1], reverse=True)
    
    for ex, pr in sorted_p:
        if ex == min_ex:
            text += f"🟢 <b>{ex}:</b> <code>${pr:,.4f}</code> [BEST BUY]\n"
        elif ex == max_ex:
            text += f"🔴 <b>{ex}:</b> <code>${pr:,.4f}</code> [BEST SELL]\n"
        else:
            text += f"   • {ex}: <code>${pr:,.4f}</code>\n"

    text += (
        f"━━━━━━━━━━━━━━━━━━━━━\n"
        f"📊 <b>Market Spread:</b> <code>%{spread:.3f}</code> — {tier_label}\n"
        f"⏰ <b>Update (UTC):</b> <code>{ts}</code>\n"
        f"📡 <i>@RadarPro_Intelligence_Bot</i>"
    )
    return text
