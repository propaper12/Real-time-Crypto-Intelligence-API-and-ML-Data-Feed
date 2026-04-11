from datetime import datetime


def format_whale_alert(data: dict) -> str:
    """Formats Titan-class order-book imbalance / whale wall detection."""
    symbol     = data.get("symbol", "UNKNOWN")
    buy_wall   = data.get("buy_wall_usd", 0)
    sell_wall  = data.get("sell_wall_usd", 0)
    imbalance  = data.get("imbalance_ratio", 0)
    cvd        = data.get("cvd", 0)
    price      = data.get("price", 0)
    ts         = data.get("timestamp", datetime.now().strftime("%H:%M:%S"))

    total = buy_wall + sell_wall + 1
    buy_pct  = (buy_wall / total * 100)
    sell_pct = (sell_wall / total * 100)

    if buy_wall > sell_wall * 2.5:
        signal = "🔥 GÜÇLÜ ALICI DUVARI — Mega Whale Inbound"
        emoji  = "🐳🟢"
    elif sell_wall > buy_wall * 2.5:
        signal = "🚨 GÜÇLÜ SATIŞ DUVARI — Sell Pressure Detected"
        emoji  = "🐳🔴"
    else:
        signal = "⚖️ DENGELİ ORDERBOOK — Accumulation Phase"
        emoji  = "🐳⚪"

    bar_buy  = "🟢" * int(buy_pct / 10)  + "⬜" * (10 - int(buy_pct / 10))
    bar_sell = "🔴" * int(sell_pct / 10) + "⬜" * (10 - int(sell_pct / 10))

    return (
        f"🐳 <b>RADARPRO WHALE ALERT — {symbol.upper()}</b> {emoji}\n"
        f"━━━━━━━━━━━━━━━━━━━━━\n"
        f"💰 <b>Fiyat:</b> <code>${price:,.2f}</code>\n"
        f"━━━━━━━━━━━━━━━━━━━━━\n"
        f"🟢 <b>Bids (Walls):</b> <code>${buy_wall:,.0f}</code> (%{buy_pct:.0f})\n"
        f"   {bar_buy}\n"
        f"🔴 <b>Asks (Walls):</b> <code>${sell_wall:,.0f}</code> (%{sell_pct:.0f})\n"
        f"   {bar_sell}\n"
        f"━━━━━━━━━━━━━━━━━━━━━\n"
        f"📊 <b>CVD Cluster:</b> <code>{cvd:,.0f}</code>\n"
        f"⚖️ <b>Imbalance:</b> <code>{imbalance:+.3f}</code>\n"
        f"━━━━━━━━━━━━━━━━━━━━━\n"
        f"🛡️ <code>{signal}</code>\n"
        f"⏰ <code>{ts}</code> | 📡 <i>TITAN ENGINE v3.5</i>"
    )


def format_funding_rate_alert(data: dict) -> str:
    """Alert when funding rate is unusually high or negative."""
    symbol       = data.get("symbol", "UNKNOWN")
    funding_rate = data.get("funding_rate", 0)
    price        = data.get("price", 0)
    ts           = datetime.now().strftime("%H:%M:%S")

    if funding_rate > 0.001:
        signal = "🔴 Yüksek pozitif fonlama — Longlar aşırı ısınmış!"
    elif funding_rate < -0.0005:
        signal = "🟢 Negatif fonlama — Shortlar aşırıya kaçtı, sıçrama riski!"
    else:
        signal = "⚪ Normal fonlama seviyesi."

    pct = funding_rate * 100

    return (
        f"💸 <b>FONLAMA ORANI UYARISI</b>\n"
        f"━━━━━━━━━━━━━━━━━━━━━\n"
        f"💎 <b>Sembol:</b> <code>{symbol}</code>\n"
        f"💲 <b>Fiyat:</b> <code>${price:,.4f}</code>\n"
        f"📊 <b>Fonlama Oranı:</b> <code>{pct:+.4f}%</code>\n"
        f"━━━━━━━━━━━━━━━━━━━━━\n"
        f"⚡ {signal}\n"
        f"⏰ <code>{ts}</code> | 📡 <i>@RadarPro_Intelligence_Bot</i>"
    )
