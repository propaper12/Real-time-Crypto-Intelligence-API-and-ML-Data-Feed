from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

def get_main_menu_keyboard():
    """RadarPro Premium Ana Menü Keyboard"""
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="⚖️ Canlı Arbitraj", callback_query_id="menu_arbitrage"),
            InlineKeyboardButton(text="🧠 RadarAI Analizi", callback_query_id="menu_radarai")
        ],
        [
            InlineKeyboardButton(text="🐋 Balina Takibi", callback_query_id="menu_whale"),
            InlineKeyboardButton(text="📊 Teknik Durum", callback_query_id="menu_market")
        ],
        [
            InlineKeyboardButton(text="⚙️ Ayarlar (Webhook)", callback_query_id="menu_settings"),
            InlineKeyboardButton(text="💎 VIP Üyelik", callback_query_id="menu_vip")
        ],
        [
            InlineKeyboardButton(text="🌐 RadarPro Terminal (Web)", url="https://radarpro-terminal.io")
        ]
    ])
    return keyboard

def get_arbitrage_keyboard():
    """Arbitraj alt menüsü"""
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔥 En Karlı 5 Fırsat", callback_query_id="arb_top5")],
        [InlineKeyboardButton(text="🔍 Sembol Sorgula", switch_inline_query_current_chat="/arbitraj ")],
        [InlineKeyboardButton(text="↩️ Geri Dön", callback_query_id="menu_main")]
    ])
    return keyboard
