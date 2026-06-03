from datetime import datetime


def format_arbitrage_alert(data: dict) -> str:
    """Premium multi-exchange arbitrage formatter with Trust Score & Risk Analysis."""
    symbol   = data.get("symbol", "UNKNOWN")
    spread   = data.get("spread_pct", 0)
    prices   = data.get("prices", {})
    buy_ex   = data.get("buy_exchange", "N/A")
    sell_ex  = data.get("sell_exchange", "N/A")
    score    = data.get("trust_score", 0)
    status   = data.get("trust_status", "TEHLİKELİ")
    risks    = data.get("risk_factors", [])
    ts       = data.get("timestamp", datetime.now().strftime("%H:%M:%S"))

    # Trust Score Icon Logic
    if score >= 80:
        score_icon = "🛡️"
        status_color = "GÜVENLİ"
    elif score >= 50:
        score_icon = "⚠️"
        status_color = "RİSKLİ"
    else:
        score_icon = "🚨"
        status_color = "TEHLİKELİ"

    text = (
        f"⚖️ <b>GLOBAL ARBİTRAJ RADARI — {symbol}</b>\n"
        f"━━━━━━━━━━━━━━━━━━━━━\n"
        f"{score_icon} <b>GÜVEN SKORU:</b> <code>{score}/100</code> ({status_color})\n"
    )

    if risks:
        risk_text = ", ".join(risks)
        text += f"❗ <b>UYARI:</b> <code>{risk_text}</code>\n"

    text += f"━━━━━━━━━━━━━━━━━━━━━\n"
    
    # Sort prices low to high for clarity
    sorted_p = sorted(prices.items(), key=lambda x: x[1])
    
    for ex, pr in sorted_p:
        if ex == buy_ex:
            text += f"🟢 <b>{ex}:</b> <code>${pr:,.4f}</code> [AL]\n"
        elif ex == sell_ex:
            text += f"🔴 <b>{ex}:</b> <code>${pr:,.4f}</code> [SAT]\n"
        else:
            text += f"   • {ex}: <code>${pr:,.4f}</code>\n"

    text += (
        f"━━━━━━━━━━━━━━━━━━━━━\n"
        f"📊 <b>Market Spread:</b> <code>%{spread:.3f}</code>\n"
        f"⏰ <b>Update (UTC):</b> <code>{ts}</code>\n"
        f"📡 <i>@RadarPro_Intelligence_Bot</i>"
    )
    return text
