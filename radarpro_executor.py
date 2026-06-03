import requests
import time
import json
import logging
from datetime import datetime

# ==============================================================================
# 🤖 RADARPRO STANDALONE TRADING BOT (EXECUTOR v1.0)
# ==============================================================================
# Bu uygulama RadarPro Titan API'sini kullanarak otonom ticaret yapar.
# Tamamen bagimsiz bir "Trading App" olarak tasarlanmistir.

API_URL = "http://localhost:8000/api/v1/arbitrage"
TRADING_THRESHOLD = 0.15  # %0.15 uzeri karlilikta islem ac
MIN_TRUST_SCORE = 80      # Sadece guvenilir sinyallere gir
TRADE_AMOUNT_USDT = 100   # Islem basina miktar

logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(levelname)s | %(message)s")
logger = logging.getLogger("RadarExecutor")

class RadarProExecutor:
    def __init__(self):
        self.is_running = True
        self.total_profit = 0

    def fetch_opportunities(self):
        try:
            # API'den DEV_MODE sayesinde sifresiz veri cekiyoruz
            response = requests.get(API_URL, timeout=2)
            if response.status_code == 200:
                return response.json().get("data", [])
        except Exception as e:
            logger.error(f"❌ API Baglanti Hatasi: {e}")
        return []

    def execute_trade(self, opportunity):
        symbol = opportunity['symbol']
        buy_ex = opportunity['buy_exchange']
        sell_ex = opportunity['sell_exchange']
        spread = opportunity['spread_pct']
        
        # --- BURASI GERCEK BORSA EMIRLERININ GIDECEGI YER ---
        # Ornek: binance_client.create_order(...)
        # Su an simülasyon modunda raporluyoruz.
        
        profit = (TRADE_AMOUNT_USDT * spread) / 100
        self.total_profit += profit
        
        print(f"\n🚀 [ISLEM ACILDI] {datetime.now().strftime('%H:%M:%S')}")
        print(f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        print(f"💰 Sembol: {symbol}")
        print(f"📥 Alis  : {buy_ex} | 📤 Satis: {sell_ex}")
        print(f"📈 Kar   : %{spread:.2f} (Tahmini: ${profit:.2f})")
        print(f"🛡️ Guven : {opportunity['trust_score']}/100")
        print(f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        print(f"💰 Toplam Biriken Kar: ${self.total_profit:.2f}\n")

    def run(self):
        print("🚀 Standalone Trading Bot Aktif. RadarPro Titan dinleniyor...")
        while self.is_running:
            opportunities = self.fetch_opportunities()
            
            for opp in opportunities:
                # Kriter Kontrolü
                if opp['spread_pct'] >= TRADING_THRESHOLD and opp['trust_score'] >= MIN_TRUST_SCORE:
                    # Islem daha once acilmis mi kontrolu (opsiyonel)
                    self.execute_trade(opp)
                    # Bir coin icin islem acildiginda 5 saniye bekle (Flood korumasi)
                    time.sleep(5)
            
            time.sleep(1) # Her saniye API'yi tara

if __name__ == "__main__":
    bot = RadarProExecutor()
    bot.run()
