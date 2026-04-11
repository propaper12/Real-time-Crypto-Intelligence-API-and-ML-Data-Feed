from datetime import datetime


def format_ai_prediction(symbol: str, data: dict) -> str:
    """Formats a Titan-Class Institutional Signal for Telegram."""
    price       = data.get("p", data.get("price", "N/A"))
    cvd         = data.get("cvd", 0)
    vpin        = data.get("vpin", data.get("vpin_score", 0))
    predicted   = data.get("predicted_price", None)
    funding     = data.get("funding_rate", 0)
    buy_wall    = data.get("buy_wall_usd", 0)
    sell_wall   = data.get("sell_wall_usd", 0)
    imbalance   = data.get("imbalance_ratio", 0)
    
    # Liquidations
    liq_u25 = data.get("liq_up_25x", 0)
    liq_d25 = data.get("liq_dn_25x", 0)
    liq_u50 = data.get("liq_up_50x", 0)
    liq_d50 = data.get("liq_dn_50x", 0)
    
    # Proxy 100x for the demo if not in data
    try:
        p_val = float(price)
        liq_u100 = p_val * 1.008
        liq_d100 = p_val * 0.992
    except:
        liq_u100 = liq_d100 = 0

    ts = datetime.now().strftime("%H:%M:%S")

    # Sentiment Meter
    bull_pct = min(max(50 + (imbalance * 50), 5), 95)
    sent_bar = "🟢" * int(bull_pct/10) + "🔴" * (10 - int(bull_pct/10))

    # Pred Line
    pred_val = f"${float(predicted):,.2f}" if predicted else "CALIBRATING..."

    return (
        f"🚀 <b>RADARPRO TITAN INSTITUTIONAL SIGNAL</b>\n"
        f"<code>╔════════════════════════════════════╗</code>\n"
        f"  💎 <b>ASSET:</b> <code>{symbol.upper()} / USDT</code>\n"
        f"  💰 <b>PRICE:</b> <code>${price}</code>\n"
        f"  📊 <b>CHAMPION AI TARGET:</b> <code>{pred_val}</code>\n"
        f"<code>╚════════════════════════════════════╝</code>\n\n"
        f"🧲 <b>LIQUIDITY MAGNETS (SHARP)</b>\n"
        f"💖 <b>100x S:</b> <code>${liq_u100:,.0f}</code> | <b>100x L:</b> <code>${liq_d100:,.0f}</code>\n"
        f"🔴 <b>50x S:</b>  <code>${liq_u50:,.0f}</code> | <b>50x L:</b>  <code>${liq_d50:,.0f}</code>\n"
        f"🔥 <b>25x S:</b>  <code>${liq_u25:,.0f}</code> | <b>25x L:</b>  <code>${liq_d25:,.0f}</code>\n"
        f"━━━━━━━━━━━━━━━━━━━━━\n"
        f"⚖️ <b>SENTIMENT:</b> %{bull_pct:.0f} BULLISH\n"
        f"   <code>{sent_bar}</code>\n"
        f"━━━━━━━━━━━━━━━━━━━━━\n"
        f"⚙️ <b>SPARK SILVER HF METRICS</b>\n"
        f"• VPIN (Toxicity): <code>{vpin:.4f}</code>\n"
        f"• NET CVD DELTA:  <code>{cvd:,.0f}</code>\n"
        f"• FUNDING RATE:   <code>{funding:+.4f}%</code>\n"
        f"━━━━━━━━━━━━━━━━━━━━━\n"
        f"📡 <b>@RadarPro_VIP_Analiz</b> | ⏰ <code>{ts}</code>"
    )


def format_ml_model_update(data: dict) -> str:
    """Notifies channel when a new champion ML model is deployed."""
    model   = data.get("model", "Bilinmiyor")
    rmse    = data.get("rmse", "N/A")
    r2      = data.get("r2", "N/A")
    ts      = datetime.now().strftime("%d.%m.%Y %H:%M")

    try:
        r2_bar = "🟩" * min(10, int(float(r2) * 10)) + "⬜" * (10 - min(10, int(float(r2) * 10)))
    except Exception:
        r2_bar = "⬜⬜⬜⬜⬜⬜⬜⬜⬜⬜"

    return (
        f"🤖 <b>YENİ ML MODELİ AKTİF!</b>\n"
        f"━━━━━━━━━━━━━━━━━━━━━\n"
        f"🏆 <b>Şampiyon Model:</b> <code>{model.upper()}</code>\n"
        f"📉 <b>RMSE Hata Payı:</b> <code>{rmse}</code>\n"
        f"📊 <b>R² Başarısı:</b> {r2_bar}\n"
        f"    <code>{r2} / 1.000</code>\n"
        f"━━━━━━━━━━━━━━━━━━━━━\n"
        f"✅ Sistem yeni tahminlerle çalışıyor.\n"
        f"⏰ <code>{ts}</code> | 📡 <i>@RadarPro_Intelligence_Bot</i>"
    )
