import asyncio
import json
import websockets
import time
from datetime import datetime

# ==============================================================================
# ⚡ RADARPRO LIGHTNING-FAST HFT BOT (WEBSOCKET EDITION)
# ==============================================================================
# Bu bot REST API kullanmaz. Borsalarin WebSocket kanallarina canli baglanir.
# Gecikme suresi (Latency): ~10ms - 50ms

class LightningArb:
    def __init__(self, symbols=["btcusdt", "ethusdt", "solusdt"]):
        self.symbols = symbols
        self.prices = {s: {} for s in symbols}
        self.threshold = 0.12 # %0.12 uzeri her seye zipla
        
    async def binance_ws(self):
        """ Binance milisaniyelik fiyat akisi """
        uri = "wss://stream.binance.com:9443/ws/" + "/".join([f"{s}@ticker" for s in self.symbols])
        async with websockets.connect(uri) as ws:
            while True:
                data = json.loads(await ws.recv())
                symbol = data['s'].lower()
                self.prices[symbol]['Binance'] = float(data['c'])
                await self.check_arbitrage(symbol)

    async def okx_ws(self):
        """ OKX milisaniyelik fiyat akisi """
        uri = "wss://ws.okx.com:8443/ws/v5/public"
        async with websockets.connect(uri) as ws:
            # Subscribe
            sub_msg = {"op": "subscribe", "args": [{"channel": "tickers", "instId": f"{s.upper().replace('USDT','-USDT')}"} for s in self.symbols]}
            await ws.send(json.dumps(sub_msg))
            while True:
                data = json.loads(await ws.recv())
                if 'data' in data:
                    inst = data['data'][0]['instId'].lower().replace("-", "")
                    self.prices[inst]['OKX'] = float(data['data'][0]['last'])
                    await self.check_arbitrage(inst)

    async def check_arbitrage(self, symbol):
        p = self.prices[symbol]
        if len(p) < 2: return
        
        ex_names = list(p.keys())
        p1, p2 = p[ex_names[0]], p[ex_names[1]]
        
        diff = abs(p1 - p2)
        min_p = min(p1, p2)
        spread = (diff / min_p) * 100
        
        if spread > self.threshold:
            buy_ex = ex_names[0] if p1 < p2 else ex_names[1]
            sell_ex = ex_names[1] if p1 < p2 else ex_names[0]
            
            print(f"⚡ [HFT SIGNAL] {symbol.upper()} | %{spread:.3f} | {buy_ex} -> {sell_ex} | {datetime.now().strftime('%H:%M:%S.%f')[:-3]}")
            # --- ASENKRON GERCEK EMIR BURADA TETIKLENIR ---
            # asyncio.create_task(self.execute_real_trade(symbol, buy_ex, sell_ex))

    async def run(self):
        print(f"🚀 HFT WebSocket Engine Aktif: {', '.join(self.symbols)}")
        await asyncio.gather(
            self.binance_ws(),
            self.okx_ws()
        )

if __name__ == "__main__":
    bot = LightningArb()
    try:
        asyncio.run(bot.run())
    except KeyboardInterrupt:
        print("🛑 Durduruldu.")
