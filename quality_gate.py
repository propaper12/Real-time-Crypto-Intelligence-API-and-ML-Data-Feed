import os
import sys
from pyspark.sql import SparkSession
from pyspark.sql.functions import col

# Bu modülü, veri ambarımızdaki Silver katmanının doğruluğunu ve tutarlılığını 
# denetlemek amacıyla bir 'Data Quality Gate' (Veri Kalite Kapısı) olarak tasarladım.
# Temel amacım, hatalı verilerin analitik süreçlere ve makine öğrenmesi modellerine 
# sızmasını önleyerek veri güvenilirliğini en üst seviyede tutmaktır.

# Ayarlar ve Bağlantı Yapılandırması:
# Sistem taşınabilirliğini ve güvenliğini sağlamak amacıyla altyapı bilgilerini 
# dinamik ortam değişkenlerinden çekiyorum.
MINIO_ENDPOINT = os.getenv("MINIO_ENDPOINT", "http://minio:9000")
ACCESS_KEY = os.getenv("MINIO_ROOT_USER")
SECRET_KEY = os.getenv("MINIO_ROOT_PASSWORD")
SILVER_PATH = "s3a://market-data/silver_layer_delta"

print("DATA QUALITY GATE (Offline Mod) Baslatiliyor...")

# Spark Session Yapılandırması:
# Delta Lake ve S3A protokollerini destekleyen gerekli JAR bağımlılıklarını 
# oturuma dahil ederek izole bir veri işleme ortamı kurguladım.
spark = SparkSession.builder \
    .appName("Quality_Guard") \
    .config("spark.jars", 
            "/opt/spark-jars/delta-core_2.12-2.4.0.jar,"
            "/opt/spark-jars/delta-storage-2.4.0.jar,"
            "/opt/spark-jars/hadoop-aws-3.3.4.jar,"
            "/opt/spark-jars/aws-java-sdk-bundle-1.12.500.jar") \
    .config("spark.driver.extraClassPath", "/opt/spark-jars/*") \
    .config("spark.executor.extraClassPath", "/opt/spark-jars/*") \
    .config("spark.sql.extensions", "io.delta.sql.DeltaSparkSessionExtension") \
    .config("spark.sql.catalog.spark_catalog", "org.apache.spark.sql.delta.catalog.DeltaCatalog") \
    .config("spark.hadoop.fs.s3a.endpoint", MINIO_ENDPOINT) \
    .config("spark.hadoop.fs.s3a.access.key", ACCESS_KEY) \
    .config("spark.hadoop.fs.s3a.secret.key", SECRET_KEY) \
    .config("spark.hadoop.fs.s3a.path.style.access", "true") \
    .config("spark.hadoop.fs.s3a.impl", "org.apache.hadoop.fs.s3a.S3AFileSystem") \
    .master("local[*]") \
    .getOrCreate()

spark.sparkContext.setLogLevel("ERROR")

try:
    # Veri Okuma ve Hata Yönetimi:
    # Cold start senaryolarında Silver katmanı henüz oluşmamış olabilir. 
    # Sistemin çökmesini önlemek için tablo varlık kontrolü ekledim.
    print(f"Veri Okunuyor: {SILVER_PATH}")
    
    try:
        df = spark.read.format("delta").load(SILVER_PATH)
    except Exception:
        print("UYARI: Silver katmaninda henüz veri yok veya tablo olusmamis.")
        sys.exit(0)
    
    total_rows = df.count()
    print(f"Toplam Analiz Edilen Satir: {total_rows}")

    if total_rows == 0:
        print("Tablo bos, kontrol adimi sonlandiriliyor.")
        sys.exit(0)

    # --- KRİTİK KURAL SETİ ---
    # Veri bütünlüğünü sağlamak adına üç temel kural tanımladım:
    
    # Kural 1: Finansal veri tutarlılığı için fiyatın sıfır veya negatif olması kabul edilemez.
    bad_prices = df.filter(col("average_price") <= 0).count()
    
    # Kural 2: Makine öğrenmesi öznitelikleri (features) için volatilite değerinin boş (Null) olmaması gerekir.
    null_volatility = df.filter(col("volatility").isNull()).count()
    
    # Kural 3: Zaman serisi analizlerinin doğruluğu için işleme zaman damgasının mevcudiyeti zorunludur.
    null_time = df.filter(col("processed_time").isNull()).count()

    # --- RAPORLAMA VE KARAR MEKANİZMASI ---
    # Bu raporlama yapısı, CI/CD süreçlerine veya otomatik izleme sistemlerine entegre edilebilir.
    print("\n" + "="*40)
    print("      KALITE KONTROL RAPORU      ")
    print("="*40)

    success = True

    if bad_prices > 0:
        print(f"HATA: Negatif/Sifir Fiyat Saptandi: {bad_prices} kayit")
        success = False
    else:
        print("Fiyat Kontrolü: BASARILI")

    if null_volatility > 0:
        print(f"UYARI: Eksik Volatilite Verisi: {null_volatility} kayit")
    else:
        print("Volatilite Kontrolü: BASARILI")
        
    if null_time > 0:
        print(f"HATA: Zaman Damgasi Hatasi: {null_time} kayit")
        success = False
    else:
        print("Zaman Damgasi Kontrolü: BASARILI")

    print("-" * 40)
    
    if success:
        print("SONUC: VERI KALITESI STANDARTLARA UYGUN (PASSED)")
    else:
        print("SONUC: VERIDE KRITIK HATALAR MEVCUT (FAILED)")

except Exception as e:
    print(f"Kritik Sistem Hatasi: {e}")

# Kaynak Yönetimi: İşlem bittiğinde Spark oturumunu güvenli bir şekilde kapatıyorum.
spark.stop()