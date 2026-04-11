import json
from datetime import datetime

class TelegramFormatter:
    @staticmethod
    def format_arbitrage_alert(data: dict) -> str:
        """Formats arbitrage opportunity data into a premium HTML message."""
        symbol = data.get("symbol", "UNKNOWN")
        spread = data.get("spread_pct", 0)
        buy_ex = data.get("buy_exchange", "N/A")
        buy_pr = data.get("buy_price", 0)
        sell_ex = data.get("sell_exchange", "N/A")
        sell_pr = data.get("sell_price", 0)
        time = data.get("timestamp", datetime.now().strftime("%H:%M:%S"))

        # Premium UI Design with Emojis and Formatting
        msg = (
            f"🚀 <b>RADARPRO ARBİTRAJ SİNYALİ</b> 🚀\n"
            f"━━━━━━━━━━━━━━━━━━━━━\n"
            f"💎 <b>Sembol:</b> <code>{symbol}</code>\n"
            f"📈 <b>Net Kâr:</b> 💸 <code>%{spread}</code>\n"
            f"━━━━━━━━━━━━━━━━━━━━━\n"
            f"📥 <b>AL:</b> {buy_ex} — <code>${buy_pr:,.4f}</code>\n"
            f"📤 <b>SAT:</b> {sell_ex} — <code>${sell_pr:,.4f}</code>\n"
            f"━━━━━━━━━━━━━━━━━━━━━\n"
            f"⏰ <b>Zaman:</b> <code>{time}</code>\n"
            f"📡 <i>@RadarPro_Intelligence_Bot</i>"
        )
        return msg

    @staticmethod
    def format_generic_message(data: str) -> str:
        """Fallback formatter for non-JSON or generic messages."""
        return f"📢 <b>Sistem Bildirimi:</b>\n\n{data}"
