import time
import os
import json
import redis
import numpy as np
import pandas as pd
from pyspark.sql import SparkSession
from pyspark.sql.functions import from_json, col, current_timestamp, coalesce, window, stddev_pop, avg, last, sum, to_timestamp, when, abs
from pyspark.sql.types import StructType, StringType, DoubleType, BooleanType
from delta.tables import DeltaTable
import threading
import requests

print("\n" + "="*60)
print("🚀 V28 GOD MODE: AI + LIQUIDATION + FOOTPRINT + ANOMALY DETECTOR")
print("="*60 + "\n")

KAFKA_BOOTSTRAP_SERVERS = os.getenv('KAFKA_BOOTSTRAP_SERVERS', 'kafka:9092')
MINIO_ENDPOINT = os.getenv("MINIO_ENDPOINT", "http://minio:9000")
ACCESS_KEY = os.getenv("MINIO_ROOT_USER", "admin")
SECRET_KEY = os.getenv("MINIO_ROOT_PASSWORD", "admin12345")
MLFLOW_TRACKING_URI = os.getenv("MLFLOW_TRACKING_URI", "http://mlflow_server:5000")

PG_USER = os.getenv("POSTGRES_USER", "admin_lakehouse")
PG_PASS = os.getenv("POSTGRES_PASSWORD", "SuperSecret_DB_Password_2026")
PG_HOST = os.getenv("POSTGRES_HOST", "postgres")
PG_DB = os.getenv("POSTGRES_DB", "market_db")
PG_URL = f"jdbc:postgresql://{PG_HOST}:5432/{PG_DB}"
PG_PROPERTIES = {"user": PG_USER, "password": PG_PASS, "driver": "org.postgresql.Driver"}

try:
    redis_client = redis.Redis(host=os.getenv("REDIS_HOST", "redis"), port=6379, db=0)
except:
    redis_client = None

# ==============================================================================
# 🟣 MAX PAIN MOTORU
# ==============================================================================
max_pain_cache = {}
def perform_deribit_fetch():
    global max_pain_cache
    try:
        for coin in ["BTC", "ETH", "SOL"]:
            url = f"https://deribit.com/api/v2/public/get_book_summary_by_currency?currency={coin}&kind=option"
            resp = requests.get(url, timeout=10)
            data = resp.json().get('result', [])
            options = []
            strikes = set()
            for item in data:
                inst = item['instrument_name'].split('-')
                if len(inst) == 4:
                    strike = float(inst[2])
                    opt_type = inst[3]
                    oi = item.get('open_interest', 0)
                    if oi > 0:
                        options.append({'strike': strike, 'type': opt_type, 'oi': oi})
                        strikes.add(strike)
            if not strikes: continue
            min_pain = float('inf')
            max_pain_strike = 0
            for test_price in strikes:
                pain = 0
                for o in options:
                    if o['type'] == 'C' and test_price > o['strike']: pain += (test_price - o['strike']) * o['oi']
                    elif o['type'] == 'P' and test_price < o['strike']: pain += (o['strike'] - test_price) * o['oi']
                if pain < min_pain:
                    min_pain = pain
                    max_pain_strike = test_price
            max_pain_cache[f"{coin}USDT"] = max_pain_strike
    except Exception as e:
        pass

def fetch_deribit_max_pain():
    perform_deribit_fetch()
    while True:
        time.sleep(300)
        perform_deribit_fetch()

threading.Thread(target=fetch_deribit_max_pain, daemon=True).start()

jar_dir = "/opt/spark-jars"
jar_conf = ",".join([
    f"{jar_dir}/delta-core_2.12-2.4.0.jar", f"{jar_dir}/delta-storage-2.4.0.jar",
    f"{jar_dir}/hadoop-aws-3.3.4.jar", f"{jar_dir}/aws-java-sdk-bundle-1.12.500.jar",
    f"{jar_dir}/spark-sql-kafka-0-10_2.12-3.4.1.jar", f"{jar_dir}/spark-token-provider-kafka-0-10_2.12-3.4.1.jar",
    f"{jar_dir}/kafka-clients-3.4.0.jar", f"{jar_dir}/commons-pool2-2.11.1.jar", f"{jar_dir}/postgresql-42.6.0.jar"
])

spark = SparkSession.builder.appName("Enterprise_Silver_Pipeline").config("spark.jars", jar_conf).config("spark.driver.extraClassPath", f"{jar_dir}/*").config("spark.executor.extraClassPath", f"{jar_dir}/*").config("spark.hadoop.fs.s3a.endpoint", MINIO_ENDPOINT).config("spark.hadoop.fs.s3a.access.key", ACCESS_KEY).config("spark.hadoop.fs.s3a.secret.key", SECRET_KEY).config("spark.hadoop.fs.s3a.path.style.access", "true").config("spark.hadoop.fs.s3a.impl", "org.apache.hadoop.fs.s3a.S3AFileSystem").config("spark.sql.extensions", "io.delta.sql.DeltaSparkSessionExtension").config("spark.sql.catalog.spark_catalog", "org.apache.spark.sql.delta.catalog.DeltaCatalog").config("spark.sql.shuffle.partitions", "4").master("local[*]").getOrCreate()
spark.sparkContext.setLogLevel("WARN")

schema = StructType().add("symbol", StringType()).add("price", DoubleType()).add("quantity", DoubleType()).add("volume_usd", DoubleType()).add("is_buyer_maker", BooleanType()).add("trade_side", StringType()).add("buy_wall_usd", DoubleType()).add("sell_wall_usd", DoubleType()).add("imbalance_ratio", DoubleType()).add("mark_price", DoubleType()).add("funding_rate", DoubleType()).add("liq_buy_usd", DoubleType()).add("liq_sell_usd", DoubleType()).add("timestamp", StringType())

df = spark.readStream.format("kafka").option("kafka.bootstrap.servers", KAFKA_BOOTSTRAP_SERVERS).option("subscribe", "market_data").option("startingOffsets", "latest").option("failOnDataLoss", "false").load()
json_df = df.select(from_json(col("value").cast("string"), schema).alias("v13"))

normalized_df = json_df.select(
    col("v13.symbol"), col("v13.price").alias("average_price"), col("v13.volume_usd"), col("v13.is_buyer_maker"),
    col("v13.trade_side"), col("v13.buy_wall_usd"), col("v13.sell_wall_usd"), col("v13.imbalance_ratio"),
    col("v13.mark_price"), col("v13.funding_rate"), col("v13.liq_buy_usd"), col("v13.liq_sell_usd"),
    current_timestamp().alias("timestamp")
).withColumn("volume_delta", when(col("trade_side") == "BUY", col("volume_usd")).otherwise(-col("volume_usd")))

windowed_df = normalized_df.withWatermark("timestamp", "1 minute").groupBy(window(col("timestamp"), "10 seconds", "5 seconds"), col("symbol")).agg(
    avg("average_price").alias("average_price"), stddev_pop("average_price").alias("volatility"),
    sum("volume_usd").alias("volume_usd"), sum("volume_delta").alias("cvd"),
    (abs(sum("volume_delta")) / (sum("volume_usd") + 1)).alias("vpin_score"),
    (last("buy_wall_usd") / (last("sell_wall_usd") + 1)).alias("wall_imbalance"),
    last("is_buyer_maker").alias("is_buyer_maker"), last("trade_side").alias("trade_side"),
    last("buy_wall_usd").alias("buy_wall_usd"), last("sell_wall_usd").alias("sell_wall_usd"),
    last("imbalance_ratio").alias("imbalance_ratio"), last("mark_price").alias("mark_price"),
    last("funding_rate").alias("funding_rate"), sum("liq_buy_usd").alias("liq_buy_usd"),
    sum("liq_sell_usd").alias("liq_sell_usd"), last("timestamp").alias("processed_time")
).na.fill(0.0)

# 🛡️ YENİ ŞEMA: ANOMALİ SÜTUNLARI EKLENDİ
output_schema = "symbol string, average_price double, volume_usd double, is_buyer_maker boolean, trade_side string, processed_time timestamp, volatility double, predicted_price double, cvd double, buy_wall_usd double, sell_wall_usd double, imbalance_ratio double, mark_price double, funding_rate double, liq_buy_usd double, liq_sell_usd double, vpin_score double, wall_imbalance double, liq_up_10x double, liq_dn_10x double, liq_up_25x double, liq_dn_25x double, liq_up_50x double, liq_dn_50x double, liq_up_100x double, liq_dn_100x double, anomaly_wash_trading boolean, anomaly_spoofing boolean, anomaly_score double"

def predict_per_symbol(pdf: pd.DataFrame) -> pd.DataFrame:
    if pdf.empty: return pdf
    symbol = pdf['symbol'].iloc[0]
    os.environ["MLFLOW_TRACKING_URI"] = "http://mlflow_server:5000"
    
    # 🤖 1. MAKİNE ÖĞRENMESİ (FİYAT TAHMİNİ)
    global_cache = globals().get("spark_model_cache", {})
    if "spark_model_cache" not in globals(): globals()["spark_model_cache"] = global_cache
        
    model = global_cache.get(symbol)
    if model is None:
        try:
            import mlflow.sklearn
            model = mlflow.sklearn.load_model(f"models:/model_{symbol}/Production")
            global_cache[symbol] = model
        except: model = None

    pdf['lag_1'] = pdf['average_price']; pdf['lag_3'] = pdf['average_price']
    pdf['ma_5'] = pdf['average_price']; pdf['ma_10'] = pdf['average_price']
    pdf['momentum'] = 0.0; pdf['volatility_change'] = 0.0
    
    features = pdf[["volatility", "lag_1", "lag_3", "ma_5", "ma_10", "momentum", "volatility_change"]]
    pdf["predicted_price"] = model.predict(features) if model else pdf["average_price"]

    # 🧲 2. LİKİDASYON MIKNATISLARI
    pdf["liq_up_10x"] = pdf["average_price"] * 1.10; pdf["liq_dn_10x"] = pdf["average_price"] * 0.90
    pdf["liq_up_25x"] = pdf["average_price"] * 1.04; pdf["liq_dn_25x"] = pdf["average_price"] * 0.96
    pdf["liq_up_50x"] = pdf["average_price"] * 1.02; pdf["liq_dn_50x"] = pdf["average_price"] * 0.98
    pdf["liq_up_100x"] = pdf["average_price"] * 1.01; pdf["liq_dn_100x"] = pdf["average_price"] * 0.99
    
    # 🛡️ 3. Z-SCORE ANOMALİ DEDEKTÖRÜ (YENİ)
    global_anomaly = globals().get("spark_anomaly_cache", {})
    if "spark_anomaly_cache" not in globals(): globals()["spark_anomaly_cache"] = global_anomaly
    
    history = global_anomaly.get(symbol, {'volumes': [], 'imbalances': []})
    current_vol = float(pdf['volume_usd'].iloc[0])
    current_imb = float(pdf['wall_imbalance'].iloc[0])
    
    history['volumes'].append(current_vol)
    history['imbalances'].append(current_imb)
    
    if len(history['volumes']) > 30: # 30 pencere (yaklaşık son 2.5 dakika) hafızada tutulur
        history['volumes'].pop(0)
        history['imbalances'].pop(0)
        
    global_anomaly[symbol] = history
    
    if len(history['volumes']) > 5:
        vol_mean = np.mean(history['volumes']); vol_std = np.std(history['volumes']) + 1e-5
        vol_z = (current_vol - vol_mean) / vol_std
        
        imb_mean = np.mean(history['imbalances']); imb_std = np.std(history['imbalances']) + 1e-5
        imb_z = (current_imb - imb_mean) / imb_std
        
        # Hacim ortalamanın 3 Standart Sapma üzerindeyse: WASH TRADING
        pdf['anomaly_wash_trading'] = bool(vol_z > 3.0) 
        # Emir defteri aniden şişti ama hacim düşükse: SPOOFING (Sahte Duvar)
        pdf['anomaly_spoofing'] = bool(abs(imb_z) > 3.0 and current_vol < vol_mean * 0.5) 
        pdf['anomaly_score'] = float(max(abs(vol_z), abs(imb_z)))
    else:
        pdf['anomaly_wash_trading'] = False; pdf['anomaly_spoofing'] = False; pdf['anomaly_score'] = 0.0
        
    return pdf[["symbol", "average_price", "volume_usd", "is_buyer_maker", "trade_side", "processed_time", "volatility", "predicted_price", "cvd", "buy_wall_usd", "sell_wall_usd", "imbalance_ratio", "mark_price", "funding_rate", "liq_buy_usd", "liq_sell_usd", "vpin_score", "wall_imbalance", "liq_up_10x", "liq_dn_10x", "liq_up_25x", "liq_dn_25x", "liq_up_50x", "liq_dn_50x", "liq_up_100x", "liq_dn_100x", "anomaly_wash_trading", "anomaly_spoofing", "anomaly_score"]]

predictions_df = windowed_df.groupBy("symbol").applyInPandas(predict_per_symbol, schema=output_schema)

def write_to_sinks(batch_df, batch_id):
    if batch_df.rdd.isEmpty(): return
    batch_df.persist()
    try:
        # Delta Lake Kaydı
        delta_path = "s3a://market-data/silver_layer_delta"
        if DeltaTable.isDeltaTable(spark, delta_path):
            dt = DeltaTable.forPath(spark, delta_path)
            dt.alias("target").merge(batch_df.alias("source"), "target.symbol = source.symbol AND target.processed_time = source.processed_time").whenMatchedUpdateAll().whenNotMatchedInsertAll().execute()
        else:
            batch_df.write.format("delta").mode("overwrite").partitionBy("symbol").save(delta_path)
        
        # Postgres Şemasını Bozmamak İçin Ekstra Sütunlar DB Öncesi Düşürülüyor
        db_df = batch_df.drop("liq_up_10x", "liq_dn_10x", "liq_up_25x", "liq_dn_25x", "liq_up_50x", "liq_dn_50x", "liq_up_100x", "liq_dn_100x", "anomaly_wash_trading", "anomaly_spoofing", "anomaly_score")
        db_df.write.jdbc(url=PG_URL, table="market_data", mode="append", properties=PG_PROPERTIES)
        
        if redis_client:
            for row in batch_df.collect():
                cache_data = {
                    "p": row["average_price"], "predicted_price": row["predicted_price"], "trade_side": row["trade_side"],
                    "cvd": row["cvd"], "volatility": row["volatility"], "vpin": row["vpin_score"],
                    "imb": row["imbalance_ratio"], "wall_imbalance": row["wall_imbalance"],
                    "buy_wall_usd": row["buy_wall_usd"], "sell_wall_usd": row["sell_wall_usd"],
                    "liq_buy": row["liq_buy_usd"], "liq_sell": row["liq_sell_usd"], "fr": row["funding_rate"],
                    "liq_up_25x": row["liq_up_25x"], "liq_dn_25x": row["liq_dn_25x"],
                    "liq_up_50x": row["liq_up_50x"], "liq_dn_50x": row["liq_dn_50x"],
                    "max_pain": max_pain_cache.get(row['symbol'], None),
                    # 🛡️ ANOMALİ VERİSİ REDIS ÜZERİNDEN ARAYÜZE GİDİYOR
                    "anomaly_wash": row["anomaly_wash_trading"],
                    "anomaly_spoof": row["anomaly_spoofing"],
                    "anomaly_zscore": row["anomaly_score"]
                }
                redis_client.set(f"GOD_MODE_{row['symbol']}", json.dumps(cache_data))
                
    except Exception as e: print(f"❌ Hata: {e}")
    finally: batch_df.unpersist()

query = predictions_df.writeStream.foreachBatch(write_to_sinks).outputMode("update").option("checkpointLocation", "/app/checkpoints_silver_v21").trigger(processingTime='5 seconds').start()
query.awaitTermination()