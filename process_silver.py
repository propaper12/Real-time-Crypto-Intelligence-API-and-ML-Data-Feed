import time
import os
import requests
import pandas as pd
from pyspark.sql import SparkSession
from pyspark.sql.functions import from_json, col, current_timestamp, coalesce, window, stddev_pop, avg, last
from pyspark.sql.types import StructType, StringType, DoubleType

print("\n" + "="*50)
print("🚀 V6.0 GÜNCELLEME: MICROSERVICE INFERENCE (API) AKTİF")
print("="*50 + "\n")

time.sleep(3)

# --- ÇEVRE DEĞİŞKENLERİ ---
KAFKA_BOOTSTRAP_SERVERS = os.getenv('KAFKA_BOOTSTRAP_SERVERS', 'kafka:9092')
MINIO_ENDPOINT = os.getenv("MINIO_ENDPOINT", "http://minio:9000")
ACCESS_KEY = os.getenv("MINIO_ROOT_USER", "admin")
SECRET_KEY = os.getenv("MINIO_ROOT_PASSWORD", "admin12345")

# Yeni Inference API Adresimiz (Docker network üzerinden haberleşecek)
INFERENCE_API_URL = os.getenv("INFERENCE_API_URL", "http://inference_api:8001/predict")

# --- POSTGRESQL BAĞLANTISI ---
PG_USER = os.getenv("POSTGRES_USER", "admin_lakehouse")
PG_PASS = os.getenv("POSTGRES_PASSWORD", "SuperSecret_DB_Password_2026")
PG_HOST = os.getenv("POSTGRES_HOST", "postgres")
PG_DB = os.getenv("POSTGRES_DB", "market_db")

PG_URL = f"jdbc:postgresql://{PG_HOST}:5432/{PG_DB}"
PG_PROPERTIES = {"user": PG_USER, "password": PG_PASS, "driver": "org.postgresql.Driver"}

# --- JAR AYARLARI ---
jar_dir = "/opt/spark-jars"
jar_conf = ",".join([
    f"{jar_dir}/delta-core_2.12-2.4.0.jar",
    f"{jar_dir}/delta-storage-2.4.0.jar",
    f"{jar_dir}/hadoop-aws-3.3.4.jar",
    f"{jar_dir}/aws-java-sdk-bundle-1.12.500.jar",
    f"{jar_dir}/spark-sql-kafka-0-10_2.12-3.4.1.jar",
    f"{jar_dir}/spark-token-provider-kafka-0-10_2.12-3.4.1.jar",
    f"{jar_dir}/kafka-clients-3.4.0.jar",
    f"{jar_dir}/commons-pool2-2.11.1.jar",
    f"{jar_dir}/postgresql-42.6.0.jar"
])

# --- SPARK SESSION ---
spark = SparkSession.builder \
    .appName("SilverLayer_Microservice") \
    .config("spark.jars", jar_conf) \
    .config("spark.driver.extraClassPath", f"{jar_dir}/*") \
    .config("spark.executor.extraClassPath", f"{jar_dir}/*") \
    .config("spark.hadoop.fs.s3a.endpoint", MINIO_ENDPOINT) \
    .config("spark.hadoop.fs.s3a.access.key", ACCESS_KEY) \
    .config("spark.hadoop.fs.s3a.secret.key", SECRET_KEY) \
    .config("spark.hadoop.fs.s3a.path.style.access", "true") \
    .config("spark.hadoop.fs.s3a.impl", "org.apache.hadoop.fs.s3a.S3AFileSystem") \
    .config("spark.hadoop.fs.s3a.connection.ssl.enabled", "false") \
    .config("spark.sql.extensions", "io.delta.sql.DeltaSparkSessionExtension") \
    .config("spark.sql.catalog.spark_catalog", "org.apache.spark.sql.delta.catalog.DeltaCatalog") \
    .config("spark.sql.shuffle.partitions", "2") \
    .master("local[*]") \
    .getOrCreate()

spark.sparkContext.setLogLevel("ERROR")

# Şema
schema = StructType().add("symbol", StringType()).add("price", DoubleType()).add("quantity", DoubleType()).add("timestamp", StringType()).add("source", StringType()) \
    .add("data", StructType().add("s", StringType()).add("p", StringType()).add("q", StringType()))

print("📡 Kafka Dinleniyor...")
df = spark.readStream \
    .format("kafka") \
    .option("kafka.bootstrap.servers", KAFKA_BOOTSTRAP_SERVERS) \
    .option("subscribe", "market_data") \
    .option("startingOffsets", "latest") \
    .option("failOnDataLoss", "false") \
    .load()

json_df = df.select(from_json(col("value").cast("string"), schema).alias("parsed_data"))

normalized_df = json_df.select(
    coalesce(col("parsed_data.symbol"), col("parsed_data.data.s")).alias("symbol"),
    coalesce(col("parsed_data.price"), col("parsed_data.data.p").cast("double")).alias("average_price"),
    current_timestamp().alias("timestamp")
)

# Window Aggregation (Veriyi 30 saniyelik bloklarda özetle)
windowed_df = normalized_df \
    .withWatermark("timestamp", "1 minute") \
    .groupBy(window(col("timestamp"), "30 seconds", "5 seconds"), col("symbol")) \
    .agg(
        stddev_pop("average_price").alias("volatility"),
        avg("average_price").alias("average_price"),
        current_timestamp().alias("processed_time")
    ).na.fill(0, subset=["volatility"])

def process_batch_with_ai(batch_df, batch_id):
    if batch_df.rdd.isEmpty(): return
    
    # 🎯 SENIOR DOKUNUŞU (BUG FIX): Pandas 2.0 Datetime Crash Çözümü
    # Tarihi geçici olarak string'e çeviriyoruz ki Pandas'a geçerken patlamasın.
    safe_batch_df = batch_df.withColumn("processed_time", col("processed_time").cast("string"))
    pdf = safe_batch_df.toPandas()
    
    results = []

    for index, row in pdf.iterrows():
        symbol = row['symbol']
        current_price = float(row['average_price'])
        volatility = float(row['volatility']) if pd.notnull(row['volatility']) else 0.0
        
        payload = {
            "symbol": symbol,
            "volatility": volatility,
            "lag_1": current_price, 
            "lag_3": current_price, 
            "ma_5": current_price,  
            "ma_10": current_price, 
            "momentum": 0.0,
            "volatility_change": 0.0
        }
        
        try:
            resp = requests.post(INFERENCE_API_URL, json=payload, timeout=2)
            if resp.status_code == 200:
                pred_price = resp.json().get("predicted_price", current_price)
            else:
                pred_price = current_price 
        except Exception:
            pred_price = current_price
            
        results.append({
            "symbol": symbol,
            "volatility": volatility,
            "average_price": current_price,
            "processed_time": row['processed_time'], # Şu an String
            "predicted_price": float(pred_price)
        })

    if results:
        from pyspark.sql.functions import to_timestamp
        
        # Sonuçları DataFrame'e çevir
        res_df = spark.createDataFrame(results)
        
        # 🎯 BUG FIX DEVAMI: String'i tekrar Spark Timestamp formatına geri çeviriyoruz
        res_df = res_df.withColumn("processed_time", to_timestamp(col("processed_time")))
        
        # 1. Delta Lake'e yaz 
        res_df.write.format("delta").mode("append").partitionBy("symbol").save("s3a://market-data/silver_layer_delta")
        
        # 2. Postgres'e yaz 
        try:
            pg_df = res_df.select("symbol", "volatility", "average_price", "processed_time", "predicted_price")
            pg_df.write.jdbc(url=PG_URL, table="market_data", mode="append", properties=PG_PROPERTIES)
            print(f"✅ Batch {batch_id}: {len(results)} sembol API'den geçirildi ve kaydedildi.")
        except Exception as e:
            print(f"❌ DB Yazma Hatası: {e}")
            
query = windowed_df.writeStream \
    .foreachBatch(process_batch_with_ai) \
    .outputMode("update") \
    .option("checkpointLocation", "/app/checkpoints_silver_v6") \
    .trigger(processingTime='5 seconds') \
    .start()

query.awaitTermination()