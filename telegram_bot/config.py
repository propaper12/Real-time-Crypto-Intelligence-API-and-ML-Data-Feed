import os

# ─── Core Bot Settings ──────────────────────────────────────────────────────
BOT_TOKEN         = os.getenv("BOT_TOKEN", "YOUR_TELEGRAM_BOT_TOKEN")
VIP_CHANNEL_ID    = os.getenv("VIP_CHANNEL_ID", "-100123456789")
WHALE_CHANNEL_ID  = os.getenv("WHALE_CHANNEL_ID", "-100987654321")
REDIS_URL         = os.getenv("REDIS_URL", "redis://redis_cache:6379")

# ─── Internal API Endpoints ─────────────────────────────────────────────────
_BASE_URL              = os.getenv("INGESTION_API_URL", "http://api_gateway:8000")
FASTAPI_AUTH_URL       = f"{_BASE_URL}/api/v1/auth/telegram"
FASTAPI_ARBITRAGE_URL  = f"{_BASE_URL}/api/v1/arbitrage"
FASTAPI_MARKET_URL     = f"{_BASE_URL}/api/v1/market"
FASTAPI_NEWS_URL       = f"{_BASE_URL}/api/v1/news"
FASTAPI_AI_URL         = f"{_BASE_URL}/api/v1/ask_ai"
FASTAPI_PORTFOLIO_URL  = f"{_BASE_URL}/api/v1/portfolio/me"
FASTAPI_ME_URL         = f"{_BASE_URL}/api/v1/auth/me"

# ─── Admin Access ───────────────────────────────────────────────────────────
# Comma-separated Telegram user IDs that can use /admin commands
_admin_raw  = os.getenv("ADMIN_IDS", "")
ADMIN_IDS   = [int(x.strip()) for x in _admin_raw.split(",") if x.strip().isdigit()]

# ─── Feature Thresholds ─────────────────────────────────────────────────────
ARBITRAGE_THRESHOLD_PCT = float(os.getenv("ARBITRAGE_THRESHOLD_PCT", "0.15"))
WHALE_WALL_USD_THRESHOLD = float(os.getenv("WHALE_WALL_USD", "5_000_000"))
FUNDING_RATE_THRESHOLD   = float(os.getenv("FUNDING_RATE_THRESHOLD", "0.001"))  # 0.1%

# ─── Scheduler ──────────────────────────────────────────────────────────────
DAILY_SUMMARY_HOUR   = int(os.getenv("DAILY_SUMMARY_HOUR", "20"))    # 20:00 UTC
DAILY_SUMMARY_MINUTE = int(os.getenv("DAILY_SUMMARY_MINUTE", "0"))

# ─── Internal API key for bot→API calls ─────────────────────────────────────
BOT_API_KEY = os.getenv("BOT_API_KEY", "")   # Set a VIP api_key here so the bot can query endpoints
