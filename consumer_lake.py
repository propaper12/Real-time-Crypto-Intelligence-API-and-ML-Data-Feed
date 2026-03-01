import time
import os
import sys
from pyspark.sql import SparkSession
from pyspark.sql.functions import col, current_timestamp

# Bu modülü, Lakehouse mimarimizin ilk durağı olan Bronze (Raw) katmanını yönetmek üzere tasarladım.
# Temel stratejim, Kafka'dan gelen veriyi şemasına bakmaksızın en saf haliyle (raw) depolamaktır.

KAFKA_BOOTSTRAP_SERVERS = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "kafka:9092")
MINIO_ENDPOINT = os.getenv("MINIO_ENDPOINT", "http://minio:9000")
ACCESS_KEY = os.getenv("MINIO_ROOT_USER")
SECRET_KEY = os.getenv("MINIO_ROOT_PASSWORD")

print("Generic Raw Data Ingestion (Bronze Layer) sureci baslatiliyor...")

# Spark Session Yapılandırması:
# Veri gölü (Data Lake) entegrasyonu için gerekli olan Delta Lake ve AWS S3A kütüphanelerini 
# versiyon uyumluluklarını gözeterek oturuma dahil ettim.
spark = SparkSession.builder \
    .appName("GenericBronzeIngestion") \
    .config("spark.jars.packages", 
            "org.apache.spark:spark-sql-kafka-0-10_2.12:3.4.1,"
            "org.apache.kafka:kafka-clients:3.4.0,"
            "org.apache.hadoop:hadoop-aws:3.3.4,"
            "com.amazonaws:aws-java-sdk-bundle:1.12.500,"
            "io.delta:delta-core_2.12:2.4.0") \
    .config("spark.sql.extensions", "io.delta.sql.DeltaSparkSessionExtension") \
    .config("spark.sql.catalog.spark_catalog", "org.apache.spark.sql.delta.catalog.DeltaCatalog") \
    .config("spark.hadoop.fs.s3a.endpoint", MINIO_ENDPOINT) \
    .config("spark.hadoop.fs.s3a.access.key", ACCESS_KEY) \
    .config("spark.hadoop.fs.s3a.secret.key", SECRET_KEY) \
    .config("spark.hadoop.fs.s3a.path.style.access", "true") \
    .config("spark.hadoop.fs.s3a.impl", "org.apache.hadoop.fs.s3a.S3AFileSystem") \
    .config("spark.hadoop.fs.s3a.connection.ssl.enabled", "false") \
    .config("spark.sql.shuffle.partitions", "2") \
    .master("local[*]") \
    .getOrCreate()

spark.sparkContext.setLogLevel("ERROR")

try:
    # 1. Veri Kaynagina Baglanti (Kafka Ingestion)
    # Geriye dönük veri kaybını önlemek adına 'earliest' offset stratejisini belirledim.
    # 'maxOffsetsPerTrigger' parametresi ile anlık veri patlamalarında (spike) 
    # sistemin kaynak tüketimini kontrol altında tutmayı hedefledim.
    streamingDf = spark.readStream \
        .format("kafka") \
        .option("kafka.bootstrap.servers", KAFKA_BOOTSTRAP_SERVERS) \
        .option("subscribe", "market_data") \
        .option("startingOffsets", "earliest") \
        .option("failOnDataLoss", "false") \
        .option("maxOffsetsPerTrigger", 1000) \
        .load()

    # 2. 'Dumb Consumer' (Aptal Tuketici) Mimarisi:
    # Veri mühendisliğinde 'Schema-on-Read' prensibini desteklemek amacıyla 
    # gelen JSON verisini burada ayrıştırmıyorum. 
    # Bu tercih, sisteme IoT sensör verisi, sunucu logu veya borsa verisi gibi 
    # farklı yapılarda veri gelse dahi ingestion katmanının asla hata almadan 
    # çalışmaya devam etmesini saglar (Schema Agnostic).
    raw_df = streamingDf.select(
        col("key").cast("string").alias("kafka_key"),
        col("value").cast("string").alias("raw_payload"), 
        col("timestamp").alias("ingest_time")
    )

    # 3. Bronze Katmanina Kayit (Delta Lake Persistence)
    # Veriyi partition (bölümleme) yapmadan doğrudan Delta Lake formatında kaydediyorum.
    # Bölümleme işlemini Silver katmanına bırakmamın sebebi, Bronze katmanının 
    # olabildiğince hızlı ve 'stateless' kalmasını saglamaktır.
    # Checkpoint mekanizması ile olası kesintilerde veri tutarlılığını garanti altına aldım.
    query = raw_df.writeStream \
        .format("delta") \
        .outputMode("append") \
        .option("path", "s3a://market-data/raw_layer_delta") \
        .option("checkpointLocation", "s3a://market-data/checkpoints_delta_raw") \
        .trigger(processingTime='5 seconds') \
        .start()

    print("Lakehouse Raw (Bronze) katmani akisi aktif. Her turlu veri formati kabul ediliyor.")
    query.awaitTermination()

except Exception as e:
    print(f"Ingestion surecinde kritik hata: {e}")
    sys.exit(1)