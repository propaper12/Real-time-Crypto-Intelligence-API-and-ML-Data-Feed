from datetime import datetime


def format_generic(text: str) -> str:
    return f"📢 <b>Sistem Bildirimi:</b>\n\n{text}"


def format_system_status(status: dict) -> str:
    """Formats live system health check for /durum command."""
    redis_ok  = status.get("redis", False)
    db_ok     = status.get("database", False)
    kafka_ok  = status.get("kafka", False)
    arb_ok    = status.get("arbitrage_scanner", False)
    news_ok   = status.get("news_scraper", False)
    uptime    = status.get("uptime", "N/A")
    ts        = datetime.now().strftime("%d.%m.%Y %H:%M:%S")

    def dot(val): return "🟢" if val else "🔴"

    return (
        f"🖥️ <b>SİSTEM SAĞLIK RAPORU</b>\n"
        f"━━━━━━━━━━━━━━━━━━━━━\n"
        f"{dot(redis_ok)}  <b>Redis Cache:</b>        {'AKTİF' if redis_ok else 'KAPALI'}\n"
        f"{dot(db_ok)}  <b>PostgreSQL DB:</b>     {'AKTİF' if db_ok else 'KAPALI'}\n"
        f"{dot(kafka_ok)}  <b>Kafka Broker:</b>     {'AKTİF' if kafka_ok else 'KAPALI'}\n"
        f"{dot(arb_ok)}  <b>Arbitraj Tarayıcı:</b> {'ÇALIŞIYOR' if arb_ok else 'DURDU'}\n"
        f"{dot(news_ok)}  <b>Haber Botu:</b>        {'ÇALIŞIYOR' if news_ok else 'DURDU'}\n"
        f"━━━━━━━━━━━━━━━━━━━━━\n"
        f"⏱️ <b>Uptime:</b> <code>{uptime}</code>\n"
        f"⏰ <code>{ts}</code> | 📡 <i>@RadarPro_Intelligence_Bot</i>"
    )


def format_price_alarm_triggered(symbol: str, target: float, current: float, direction: str) -> str:
    direction_icon = "📈" if direction == "up" else "📉"
    return (
        f"🔔 <b>FİYAT ALARMI TETİKLENDİ!</b> {direction_icon}\n"
        f"━━━━━━━━━━━━━━━━━━━━━\n"
        f"💎 <b>Sembol:</b> <code>{symbol.upper()}</code>\n"
        f"🎯 <b>Hedef Fiyat:</b> <code>${target:,.4f}</code>\n"
        f"💲 <b>Anlık Fiyat:</b> <code>${current:,.4f}</code>\n"
        f"━━━━━━━━━━━━━━━━━━━━━\n"
        f"✅ Alarm tamamlandı ve silindi.\n"
        f"📡 <i>@RadarPro_Intelligence_Bot</i>"
    )
