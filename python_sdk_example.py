import requests
import json

# ==============================================================================
# 🚀 RADARPRO - DEVELOPER SDK EXAMPLE (PYTHON)
# ==============================================================================

API_BASE_URL = "http://localhost:8000/api/v1"
API_KEY = "YOUR_API_KEY_HERE"

headers = {
    "X-API-Key": API_KEY,
    "Content-Type": "application/json"
}

def register_webhook(my_url):
    """Sinyallerin otomatik PUSH edileceği URL'yi kaydeder."""
    payload = {"url": my_url}
    r = requests.post(f"{API_BASE_URL}/settings/webhook", json=payload, headers=headers)
    return r.json()

def get_safe_arbitrage():
    """Piyasadaki en karlı ve güvenli fırsatları listeler."""
    r = requests.get(f"{API_BASE_URL}/arbitrage/all/safe?min_score=80&min_spread=0.2", headers=headers)
    return r.json()

def validate_with_ai(symbol, buy_ex, sell_ex, spread):
    """Bir işlemi yapmadan önce Gemini AI'dan teknik onay alır."""
    payload = {
        "symbol": symbol,
        "buy_exchange": buy_ex,
        "sell_exchange": sell_ex,
        "spread_pct": spread
    }
    r = requests.post(f"{API_BASE_URL}/agent/validate", json=payload, headers=headers)
    return r.json()

# --- Örnek Senaryo ---
if __name__ == "__main__":
    print("📡 RadarPro Entegrasyonu Başlatılıyor...")
    
    # 1. Webhook Kaydı (Kendi botun için)
    # print(register_webhook("https://my-trading-bot.com/webhooks/radarpro"))

    # 2. Güvenli Fırsatları Getir
    opportunities = get_safe_arbitrage()
    if opportunities.get("status") == "success" and opportunities.get("count", 0) > 0:
        best_arb = opportunities["data"][0]
        print(f"🔥 Fırsat Yakalandı: {best_arb['symbol']} - %{best_arb['spread_pct']}")

        # 3. Yapay Zekadan Onay Al
        print("🤖 AI Karar Mekanizması Sorgulanıyor...")
        decision = validate_with_ai(
            best_arb['symbol'], 
            best_arb['buy_exchange'], 
            best_arb['sell_exchange'], 
            best_arb['spread_pct']
        )
        print(f"⚖️ AI Kararı: {json.dumps(decision, indent=2)}")
    else:
        print("⌛ Şu an kriterlere uygun güvenli fırsat bulunamadı.")
