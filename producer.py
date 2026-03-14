import json
import time
import os
import websocket
import logging
from kafka import KafkaProducer
from datetime import datetime

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

KAFKA_SERVER = os.getenv('KAFKA_BOOTSTRAP_SERVERS', 'kafka:9092')
KAFKA_TOPIC = 'market_data'

market_state = {}

def get_kafka_producer():
    while True:
        try:
            producer = KafkaProducer(
                bootstrap_servers=KAFKA_SERVER,
                value_serializer=lambda x: json.dumps(x).encode('utf-8'),
                acks=1, retries=5, compression_type='gzip'
            )
            logger.info("🟢 Kafka bağlantısı başarılı!")
            return producer
        except Exception as e:
            logger.error(f"🔴 Kafka Hatası: {e}")
            time.sleep(5)

producer = get_kafka_producer()

def on_message(ws, message):
    try:
        raw = json.loads(message)
        if 'stream' not in raw: return
        
        stream_name = raw['stream']
        data = raw['data']
        
        if stream_name == '!forceOrder@arr':
            symbol = data['o']['s'].upper()
            side = data['o']['S']
            usd_val = float(data['o']['p']) * float(data['o']['q'])
            if symbol not in market_state: market_state[symbol] = {"buy_wall":0, "sell_wall":0, "mark_price":0, "funding_rate":0, "liq_buy":0, "liq_sell":0}
            if side == 'SELL': market_state[symbol]['liq_buy'] += usd_val
            else: market_state[symbol]['liq_sell'] += usd_val

        elif '@markPrice' in stream_name:
            symbol = data['s'].upper()
            if symbol not in market_state: market_state[symbol] = {"buy_wall":0, "sell_wall":0, "mark_price":0, "funding_rate":0, "liq_buy":0, "liq_sell":0}
            market_state[symbol]['mark_price'] = float(data['p'])
            market_state[symbol]['funding_rate'] = float(data.get('r', 0))

        elif '@depth20' in stream_name:
            symbol = stream_name.split('@')[0].upper()
            buy_wall = sum([float(p) * float(q) for p, q in data.get('b', [])])
            sell_wall = sum([float(p) * float(q) for p, q in data.get('a', [])])
            if symbol not in market_state: market_state[symbol] = {"buy_wall":0, "sell_wall":0, "mark_price":0, "funding_rate":0, "liq_buy":0, "liq_sell":0}
            market_state[symbol]['buy_wall'] = buy_wall
            market_state[symbol]['sell_wall'] = sell_wall

        elif '@aggTrade' in stream_name:
            symbol = data['s'].upper()
            price = float(data['p'])
            quantity = float(data['q'])
            is_buyer_maker = data['m']
            
            state = market_state.get(symbol, {"buy_wall":0, "sell_wall":0, "mark_price":0, "funding_rate":0, "liq_buy":0, "liq_sell":0})
            total_wall = state['buy_wall'] + state['sell_wall']
            imbalance = (state['buy_wall'] - state['sell_wall']) / total_wall if total_wall > 0 else 0
            
            processed_data = {
                'symbol': symbol, 'price': price, 'quantity': quantity,
                'volume_usd': price * quantity, 'is_buyer_maker': is_buyer_maker,
                'trade_side': 'SELL' if is_buyer_maker else 'BUY',
                'buy_wall_usd': state['buy_wall'], 'sell_wall_usd': state['sell_wall'],
                'imbalance_ratio': imbalance, 'mark_price': state['mark_price'],
                'funding_rate': state['funding_rate'], 'liq_buy_usd': state['liq_buy'],
                'liq_sell_usd': state['liq_sell'],
                'timestamp': datetime.fromtimestamp(data['T'] / 1000).isoformat(),
                'event_time': datetime.utcnow().isoformat(),
                'source': 'binance_futures'
            }
            producer.send(KAFKA_TOPIC, value=processed_data)
            
            if symbol in market_state:
                market_state[symbol]['liq_buy'] = 0
                market_state[symbol]['liq_sell'] = 0

    except Exception as e:
        pass

def on_error(ws, error): logger.error(f"WS Hatası: {error}")
def on_close(ws, c, m): time.sleep(2)
def on_open(ws): logger.info("🚀 Binance FUTURES 25-Coin Bağlantısı Aktif!")

if __name__ == "__main__":
    coins = ["btcusdt", "ethusdt", "solusdt", "bnbusdt", "xrpusdt", "adausdt", "avaxusdt", "dogeusdt", "dotusdt", "linkusdt", "trxusdt", "shibusdt", "ltcusdt", "uniusdt", "bchusdt", "atomusdt", "xlmusdt", "nearusdt", "algousdt", "vetusdt", "filusdt", "icpusdt", "sandusdt", "manausdt", "ftmusdt"]
    streams = ["!forceOrder@arr"]
    for coin in coins:
        streams.append(f"{coin}@aggTrade")
        streams.append(f"{coin}@depth20@100ms")
        streams.append(f"{coin}@markPrice@1s")
        
    socket_url = f"wss://fstream.binance.com/stream?streams={'/'.join(streams)}"
    while True:
        ws = websocket.WebSocketApp(socket_url, on_open=on_open, on_message=on_message, on_error=on_error, on_close=on_close)
        ws.run_forever(ping_interval=70, ping_timeout=10)