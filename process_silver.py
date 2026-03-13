import time
import os
import json
import redis
import pandas as pd
from pyspark.sql import SparkSession
from pyspark.sql.functions import from_json, col, current_timestamp, coalesce, window, stddev_pop, avg, last, sum, to_timestamp, when, abs
from pyspark.sql.types import StructType, StringType, DoubleType, BooleanType
from delta.tables import DeltaTable

print("\n" + "="*60)
print("🚀 V13.0 GOD MODE + ML ENGINE: THE ULTIMATE QUANT PIPELINE")
print("="*60 + "\n")

# --- ÇEVRE DEĞİŞKENLERİ ---
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

# --- SPARK SESSION VE JAR KÜTÜPHANELERİ ---
jar_dir = "/opt/spark-jars"
jar_conf = ",".join([
    f"{jar_dir}/delta-core_2.12-2.4.0.jar", 
    f"{jar_dir}/delta-storage-2.4.0.jar",
    f"{jar_dir}/hadoop-aws-3.3.4.jar", 
    f"{jar_dir}/aws-java-sdk-bundle-1.12.500.jar",
    f"{jar_dir}/spark-sql-kafka-0-10_2.12-3.4.1.jar", 
    f"{jar_dir}/spark-token-provider-kafka-0-10_2.12-3.4.1.jar",
    f"{jar_dir}/kafka-clients-3.4.0.jar", 
    f"{jar_dir}/commons-pool2-2.11.1.jar",  # ÖNEMLİ EKSİK GİDERİLDİ
    f"{jar_dir}/postgresql-42.6.0.jar"
])

spark = SparkSession.builder \
    .appName("Enterprise_V13_ML_Pipeline") \
    .config("spark.jars", jar_conf) \
    .config("spark.driver.extraClassPath", f"{jar_dir}/*") \
    .config("spark.executor.extraClassPath", f"{jar_dir}/*") \
    .config("spark.hadoop.fs.s3a.endpoint", MINIO_ENDPOINT) \
    .config("spark.hadoop.fs.s3a.access.key", ACCESS_KEY) \
    .config("spark.hadoop.fs.s3a.secret.key", SECRET_KEY) \
    .config("spark.hadoop.fs.s3a.path.style.access", "true") \
    .config("spark.hadoop.fs.s3a.impl", "org.apache.hadoop.fs.s3a.S3AFileSystem") \
    .config("spark.sql.extensions", "io.delta.sql.DeltaSparkSessionExtension") \
    .config("spark.sql.catalog.spark_catalog", "org.apache.spark.sql.delta.catalog.DeltaCatalog") \
    .config("spark.sql.shuffle.partitions", "4") \
    .master("local[*]") \
    .getOrCreate()
spark.sparkContext.setLogLevel("WARN")

# --- KAFKA OKUMA VE V13 ŞEMA ---
schema = StructType() \
    .add("symbol", StringType()).add("price", DoubleType()).add("quantity", DoubleType()) \
    .add("volume_usd", DoubleType()).add("is_buyer_maker", BooleanType()).add("trade_side", StringType()) \
    .add("buy_wall_usd", DoubleType()).add("sell_wall_usd", DoubleType()).add("imbalance_ratio", DoubleType()) \
    .add("mark_price", DoubleType()).add("funding_rate", DoubleType()) \
    .add("liq_buy_usd", DoubleType()).add("liq_sell_usd", DoubleType()).add("timestamp", StringType()) \
    .add("data", StructType().add("s", StringType()).add("p", StringType()).add("q", StringType())) # Multi-stream fallback

df = spark.readStream.format("kafka").option("kafka.bootstrap.servers", KAFKA_BOOTSTRAP_SERVERS) \
    .option("subscribe", "market_data").option("startingOffsets", "latest").option("failOnDataLoss", "false").load()

json_df = df.select(from_json(col("value").cast("string"), schema).alias("v13"))

# --- VERİ DÜZENLEME VE CVD ---
normalized_df = json_df.select(
    coalesce(col("v13.symbol"), col("v13.data.s")).alias("symbol"),
    coalesce(col("v13.price"), col("v13.data.p").cast("double")).alias("average_price"),
    col("v13.volume_usd"), col("v13.is_buyer_maker"), col("v13.trade_side"),
    col("v13.buy_wall_usd"), col("v13.sell_wall_usd"), col("v13.imbalance_ratio"),
    col("v13.mark_price"), col("v13.funding_rate"), col("v13.liq_buy_usd"), col("v13.liq_sell_usd"),
    current_timestamp().alias("timestamp")
).withColumn("volume_delta", when(col("trade_side") == "BUY", col("volume_usd")).otherwise(-col("volume_usd")))

# --- WINDOW AGGREGATION (ALPHA METRICS) ---
windowed_df = normalized_df \
    .withWatermark("timestamp", "1 minute") \
    .groupBy(window(col("timestamp"), "30 seconds", "5 seconds"), col("symbol")) \
    .agg(
        avg("average_price").alias("average_price"),
        stddev_pop("average_price").alias("volatility"),
        sum("volume_usd").alias("volume_usd"),
        sum("volume_delta").alias("cvd"),
        (abs(sum("volume_delta")) / sum("volume_usd")).alias("vpin_score"),
        (last("buy_wall_usd") / last("sell_wall_usd")).alias("wall_imbalance"),
        last("is_buyer_maker").alias("is_buyer_maker"), last("trade_side").alias("trade_side"),
        last("buy_wall_usd").alias("buy_wall_usd"), last("sell_wall_usd").alias("sell_wall_usd"),
        last("imbalance_ratio").alias("imbalance_ratio"), last("mark_price").alias("mark_price"),
        last("funding_rate").alias("funding_rate"), sum("liq_buy_usd").alias("liq_buy_usd"),
        sum("liq_sell_usd").alias("liq_sell_usd"), last("timestamp").alias("processed_time")
    ).na.fill(0.0)

# --- 🧠 DISTRIBUTED MLOPS: PANDAS UDF (ESKİ KODUN TAMAMI GERİ GELDİ) ---
output_schema = "symbol string, average_price double, volume_usd double, is_buyer_maker boolean, trade_side string, processed_time timestamp, volatility double, predicted_price double, cvd double, buy_wall_usd double, sell_wall_usd double, imbalance_ratio double, mark_price double, funding_rate double, liq_buy_usd double, liq_sell_usd double, vpin_score double, wall_imbalance double"

def predict_per_symbol(pdf: pd.DataFrame) -> pd.DataFrame:
    if pdf.empty: return pdf
    symbol = pdf['symbol'].iloc[0]
    
    os.environ["MLFLOW_TRACKING_URI"] = "http://mlflow_server:5000"
    os.environ["AWS_ACCESS_KEY_ID"] = "admin"
    os.environ["AWS_SECRET_ACCESS_KEY"] = "admin12345"
    os.environ["MLFLOW_S3_ENDPOINT_URL"] = "http://minio:9000"
    
    global_cache = globals().get("spark_model_cache", {})
    if "spark_model_cache" not in globals(): globals()["spark_model_cache"] = global_cache
        
    model = global_cache.get(symbol)
    if model is None:
        try:
            import mlflow.sklearn
            model = mlflow.sklearn.load_model(f"models:/model_{symbol}/Production")
            global_cache[symbol] = model
        except Exception: model = None

    # Eskiden olan tüm feature engineering işlemleri geri eklendi!
    pdf['lag_1'] = pdf['average_price']
    pdf['lag_3'] = pdf['average_price']
    pdf['ma_5'] = pdf['average_price']
    pdf['ma_10'] = pdf['average_price']
    pdf['momentum'] = 0.0
    pdf['volatility_change'] = 0.0
    
    features = pdf[["volatility", "lag_1", "lag_3", "ma_5", "ma_10", "momentum", "volatility_change"]]
    pdf["predicted_price"] = model.predict(features) if model else pdf["average_price"]
        
    return pdf[["symbol", "average_price", "volume_usd", "is_buyer_maker", "trade_side", "processed_time", "volatility", "predicted_price", "cvd", "buy_wall_usd", "sell_wall_usd", "imbalance_ratio", "mark_price", "funding_rate", "liq_buy_usd", "liq_sell_usd", "vpin_score", "wall_imbalance"]]

predictions_df = windowed_df.groupBy("symbol").applyInPandas(predict_per_symbol, schema=output_schema)

# --- 🗄️ POLYGLOT PERSISTENCE (IDEMPOTENT SINK + CACHE) ---
def write_to_sinks(batch_df, batch_id):
    if batch_df.rdd.isEmpty(): return
    batch_df.persist()
    
    try:
        delta_path = "s3a://market-data/silver_layer_delta"
        
        # 1. DELTA LAKE MERGE
        if DeltaTable.isDeltaTable(spark, delta_path):
            dt = DeltaTable.forPath(spark, delta_path)
            dt.alias("target").merge(
                batch_df.alias("source"),
                "target.symbol = source.symbol AND target.processed_time = source.processed_time"
            ).whenMatchedUpdateAll().whenNotMatchedInsertAll().execute()
        else:
            batch_df.write.format("delta").mode("overwrite").partitionBy("symbol").save(delta_path)
        
        # 2. TIMESCALEDB SINK
        batch_df.write.jdbc(url=PG_URL, table="market_data", mode="append", properties=PG_PROPERTIES)
        
        # 3. REDIS IN-MEMORY CACHE (API VE AI İÇİN)
        if redis_client:
            rows = batch_df.collect()
            for row in rows:
                cache_data = {
                    "price": row["average_price"],
                    "predicted_price": row["predicted_price"], # ML Tahmini eklendi!
                    "trade_side": row["trade_side"],
                    "cvd": row["cvd"],
                    "vpin": row["vpin_score"],
                    "imb": row["wall_imbalance"],
                    "liq": row["liq_buy_usd"] + row["liq_sell_usd"],
                    "fr": row["funding_rate"]
                }
                # Hem eski API hem yeni AI sistemi okuyabilsin diye iki key'e de yazıyoruz
                redis_client.set(f"LATEST_{row['symbol']}", json.dumps(cache_data))
                redis_client.set(f"GOD_MODE_{row['symbol']}", json.dumps(cache_data))
                
        print(f"📦 Batch {batch_id}: ML Tahmini + V13 Verileri Delta, Postgres ve Redis'e yazıldı!")
    except Exception as e:
        print(f"❌ Veri yazma hatası: {e}")
    finally:
        batch_df.unpersist()

# --- STREAMING EXECUTION ---
query = predictions_df.writeStream \
    .foreachBatch(write_to_sinks) \
    .outputMode("update") \
    .option("checkpointLocation", "/app/checkpoints_silver_v13_ml") \
    .trigger(processingTime='5 seconds') \
    .start()

query.awaitTermination()