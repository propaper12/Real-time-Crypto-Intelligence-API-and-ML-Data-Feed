import yfinance as yf
import pandas as pd
import os
from deltalake.writer import write_deltalake

# --- DOCKER İÇİ MINIO BAĞLANTISI ---
storage_options = {
    "AWS_ACCESS_KEY_ID": os.getenv("MINIO_ROOT_USER", "admin"),
    "AWS_SECRET_ACCESS_KEY": os.getenv("MINIO_ROOT_PASSWORD", "admin12345"),
    "AWS_ENDPOINT_URL": os.getenv("MINIO_ENDPOINT", "http://minio:9000"), # Docker Network DNS'i
    "AWS_REGION": "us-east-1",
    "AWS_S3_ALLOW_UNSAFE_RENAME": "true",
    "AWS_ALLOW_HTTP": "true"
}

COINS = ["BTC-USD", "ETH-USD", "SOL-USD", "XRP-USD", "AVAX-USD"]

def fetch_and_save_data(interval="1h", period="730d", target_path="s3://market-data/historical_hourly_delta"):
    print(f"\n🚀 BATCH ETL BAŞLATILDI: İnterval={interval}, Periyot={period}")
    all_data = []
    
    for coin in COINS:
        print(f"📡 {coin} çekiliyor...")
        try:
            ticker = yf.Ticker(coin)
            df = ticker.history(period=period, interval=interval)
            
            if df.empty: continue
                
            df = df.reset_index()
            date_col = 'Datetime' if 'Datetime' in df.columns else 'Date'
            
            df_clean = pd.DataFrame({
                'timestamp': pd.to_datetime(df[date_col], utc=True),
                'symbol': coin.replace('-USD', 'USDT'),
                'open': df['Open'].astype(float),
                'high': df['High'].astype(float),
                'low': df['Low'].astype(float),
                'close': df['Close'].astype(float),
                'volume': df['Volume'].astype(float)
            })
            
            # Partitioning için yıl sütunu
            df_clean['year'] = df_clean['timestamp'].dt.year
            all_data.append(df_clean)
            
        except Exception as e:
            print(f"❌ Hata: {e}")
            
    if all_data:
        final_df = pd.concat(all_data, ignore_index=True)
        print(f"✅ {len(final_df)} satır veri Delta Lake'e (MinIO) yazılıyor...")
        
        write_deltalake(
            target_path, 
            final_df, 
            mode="overwrite", 
            partition_by=["symbol", "year"], 
            storage_options=storage_options
        )
        print("🎉 ETL İşlemi Başarılı!")

if __name__ == "__main__":
    fetch_and_save_data(interval="1h", period="730d", target_path="s3://market-data/historical_hourly_delta")
    fetch_and_save_data(interval="1d", period="10y", target_path="s3://market-data/historical_daily_delta")