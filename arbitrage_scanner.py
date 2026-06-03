import asyncio
import json
import os
import aiohttp
import redis.asyncio as aioredis
from datetime import datetime
import time

# ==============================================================================
# ⚡ RADARPRO - ENTERPRISE ARBITRAGE SCANNER (10 EXCHANGES)
# ==============================================================================

REDIS_URL = os.getenv("REDIS_URL", "redis://redis_cache:6379")
# .env'den coinleri oku, yoksa varsayılanları tara
SCAN_COINS_RAW = os.getenv("SCAN_COINS", "BTC,ETH,SOL,AVAX,XRP,LINK,ADA,DOT,MATIC,LTC,BCH,UNI,XLM,ETC,ATOM,ALGO,NEAR,HBAR,VET,ICP,FIL,LDO,ARB,OP,APT")
SCAN_COINS = [f"{c.strip()}USDT" for c in SCAN_COINS_RAW.split(",")]

SCAN_DELAY = float(os.getenv("SCAN_DELAY", "1.0")) # 1.0 - 2.0 idealdir

timeout = aiohttp.ClientTimeout(total=2.5, connect=1.0)

async def fetch_price(session, exchange, url, extract_func):
    try:
        async with session.get(url, timeout=timeout) as resp:
            if resp.status == 200:
                data = await resp.json()
                price = extract_func(data)
                return exchange, price
    except: pass
    return exchange, None

async def fetch_depth(session, exchange, symbol):
    """ Borsadan emir defteri derinliğini (top 5) çeker """
    base = symbol.replace("USDT", "")
    urls = {
        "Binance": f"https://api.binance.com/api/v3/depth?symbol={symbol}&limit=5",
        "OKX": f"https://www.okx.com/api/v5/market/books?instId={base}-USDT&sz=5"
    }
    if exchange not in urls: return 1000 
    try:
        async with session.get(urls[exchange], timeout=1.5) as resp:
            if resp.status == 200:
                data = await resp.json()
                if exchange == "Binance": return sum([float(it[1]) * float(it[0]) for it in data['bids']])
                if exchange == "OKX": return sum([float(it[1]) * float(it[0]) for it in data['data'][0]['bids']])
    except: pass
    return 500 

async def scan_coin(session, symbol, redis):
    base = symbol.replace("USDT", "")
    # Fiyat çekme işlemleri (Mevcut yapı)
    tasks = [
        fetch_price(session, "Binance", f"https://api.binance.com/api/v3/ticker/price?symbol={symbol}", lambda d: float(d['price'])),
        fetch_price(session, "OKX", f"https://www.okx.com/api/v5/market/ticker?instId={base}-USDT", lambda d: float(d['data'][0]['last'])),
        fetch_price(session, "Bybit", f"https://api.bybit.com/v5/market/tickers?category=spot&symbol={symbol}", lambda d: float(d['result']['list'][0]['lastPrice'])),
        fetch_price(session, "KuCoin", f"https://api.kucoin.com/api/v1/market/orderbook/level1?symbol={base}-USDT", lambda d: float(d['data']['price'])),
        fetch_price(session, "MEXC", f"https://api.mexc.com/api/v3/ticker/price?symbol={symbol}", lambda d: float(d['price'])),
        fetch_price(session, "Gateio", f"https://api.gateio.ws/api/v4/spot/tickers?currency_pair={base}_USDT", lambda d: float(d[0]['last'])),
        fetch_price(session, "Bitget", f"https://api.bitget.com/api/v2/spot/market/tickers?symbol={symbol}", lambda d: float(d['data'][0]['lastPr'])),
        fetch_price(session, "HTX", f"https://api.huobi.pro/market/detail/merged?symbol={base.lower()}usdt", lambda d: float(d['tick']['ask'][0])),
        fetch_price(session, "Phemex", f"https://api.phemex.com/v1/md/ticker/24hr?symbol=s{symbol}", lambda d: float(d['result']['lastEp'] / 10**8)),
        fetch_price(session, "Bitmart", f"https://api-cloud.bitmart.com/spot/v1/ticker?symbol={base}_USDT", lambda d: float(d['data']['tickers'][0]['last_price'])),
    ]
    
    results = await asyncio.gather(*tasks)
    prices = {ex: p for ex, p in results if p is not None}
    if len(prices) < 2: return

    mi, ma = min(prices, key=prices.get), max(prices, key=prices.get)
    spread_pct = ((prices[ma] - prices[mi]) / prices[mi]) * 100
    
    # 🔍 DERİNLİK KONTROLÜ (Likidite Filtresi)
    # Sadece en karlı borsa çifti için derinlik kontrolü yapıyoruz (Hız için)
    liquidity_usd = await fetch_depth(session, mi, symbol)
    
    trust_score = min(100, (len(prices) * 10))
    if liquidity_usd < 100: trust_score -= 30 # Çok düşük likidite
    if spread_pct > 3.0: trust_score -= 40 # Şüpheli yüksek makas (genelde cüzdan kapalıdır)

    arb_data = {
        "symbol": symbol, "prices": prices,
        "buy_exchange": mi, "sell_exchange": ma,
        "spread_pct": round(spread_pct, 4),
        "trust_score": trust_score,
        "liquidity_usd": round(liquidity_usd, 2),
        "timestamp": datetime.now().strftime("%H:%M:%S")
    }
    await redis.set(f"ARB_STATE_{symbol}", json.dumps(arb_data), ex=10)

async def main():
    print(f"🚀 RadarPro Enterprise Engine Baslatiliyor ({len(SCAN_COINS)} Coin | 10 Borsa)")
    r = await aioredis.from_url(REDIS_URL, decode_responses=True)
    async with aiohttp.ClientSession() as session:
        while True:
            t0 = time.perf_counter()
            tasks = [scan_coin(session, s, r) for s in SCAN_COINS]
            await asyncio.gather(*tasks)
            print(f"⚡ Global Tarama Tamamlandi: {(time.perf_counter()-t0):.2f}s | Aktif Coin: {len(SCAN_COINS)}")
            await asyncio.sleep(SCAN_DELAY)

if __name__ == "__main__":
    asyncio.run(main())
