import asyncio
import json
import os
import aiohttp
import redis.asyncio as aioredis
from datetime import datetime

# ==============================================================================
# 📐 RADARPRO - TRIANGULAR ARBITRAGE ENGINE (INTRA-EXCHANGE)
# ==============================================================================

REDIS_URL = os.getenv("REDIS_URL", "redis://redis_cache:6379")
EXCHANGE = "Binance"

async def scan_triangular():
    print(f"📐 Triangular Engine Başlatıldı ({EXCHANGE})...")
    r = await aioredis.from_url(REDIS_URL, decode_responses=True)
    
    async with aiohttp.ClientSession() as session:
        while True:
            try:
                # Örnek Üçgen: USDT -> BTC -> ETH -> USDT
                # Gerçek sistemde bu binlerce kombinasyon olabilir
                async with session.get("https://api.binance.com/api/v3/ticker/bookTicker") as resp:
                    data = await resp.json()
                    tickers = {t['symbol']: t for t in data}
                    
                    # 1. USDT -> BTC (Buy)
                    btc_usdt = float(tickers['BTCUSDT']['askPrice'])
                    # 2. BTC -> ETH (Buy ETH with BTC)
                    eth_btc = float(tickers['ETHBTC']['askPrice'])
                    # 3. ETH -> USDT (Sell)
                    eth_usdt = float(tickers['ETHUSDT']['bidPrice'])
                    
                    # Başlangıç: 1000 USDT
                    start_amount = 1000
                    step1 = start_amount / btc_usdt
                    step2 = step1 / eth_btc
                    final_amount = step2 * eth_usdt
                    
                    profit_pct = ((final_amount - start_amount) / start_amount) * 100
                    
                    if profit_pct > 0.05: # %0.05 üzeri kâr (Komisyonlar dahil değil)
                        tri_data = {
                            "type": "TRIANGULAR",
                            "route": "USDT -> BTC -> ETH -> USDT",
                            "profit_pct": round(profit_pct, 4),
                            "timestamp": datetime.now().strftime("%H:%M:%S")
                        }
                        await r.set("TRI_ARB_STATE", json.dumps(tri_data), ex=5)
                        print(f"📐 Triangular Opportunity: %{profit_pct:.4f}")
                        
            except Exception as e:
                print(f"⚠️ Triangular Hatası: {e}")
            
            await asyncio.sleep(2)

if __name__ == "__main__":
    asyncio.run(scan_triangular())
