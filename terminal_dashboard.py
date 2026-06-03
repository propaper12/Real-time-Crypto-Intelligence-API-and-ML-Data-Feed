import redis
import json
import os
import time
from datetime import datetime

# ==============================================================================
# 📟 RADARPRO TERMINAL DASHBOARD - CLI EDITION
# ==============================================================================

REDIS_HOST = "redis_cache"
REDIS_PORT = 6379

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def get_live_arbitrage():
    try:
        r = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, decode_responses=True)
        keys = r.keys("ARB_STATE_*")
        opportunities = []
        for key in keys:
            raw = r.get(key)
            if raw: opportunities.append(json.loads(raw))
        
        opportunities.sort(key=lambda x: x.get("spread_pct", 0), reverse=True)
        return opportunities[:10]
    except:
        return None

def show_dashboard():
    while True:
        clear_screen()
        print(f"============================================================")
        print(f"🚀 RADARPRO TITAN - CANLI TERMINAL PANELI | {datetime.now().strftime('%H:%M:%S')}")
        print(f"============================================================\n")
        
        arbs = get_live_arbitrage()
        if arbs:
            print(f"{'SEMBOL':<10} | {'SPREAD':<8} | {'ROTA':<20} | {'GUVEN':<6}")
            print("-" * 60)
            for o in arbs:
                rota = f"{o['buy_exchange']}->{o['sell_exchange']}"
                score = o.get('trust_score', '??')
                print(f"{o['symbol']:<10} | %{o['spread_pct']:<7.2f} | {rota:<20} | {score}/100")
        else:
            print("⌛ Veri bekleniyor veya Redis baglantisi yok...")

        print(f"\n============================================================")
        print(f"💡 Cikmak icin CTRL+C basin.")
        time.sleep(2)

if __name__ == "__main__":
    try:
        show_dashboard()
    except KeyboardInterrupt:
        print("\n👋 Terminal Panelinden cikiliyor...")
