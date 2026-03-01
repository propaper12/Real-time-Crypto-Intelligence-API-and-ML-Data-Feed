# batch_processor.py
from pyspark.sql import SparkSession
from pyspark.sql import functions as F
import os
import sys
import re

# Sistem güvenliğini ve taşınabilirliğini sağlamak amacıyla hassas bilgileri 
# doğrudan kod içerisine yazmak yerine .env dosyası üzerinden dinamik olarak yönetiyorum.
MINIO_ENDPOINT = os.getenv("MINIO_ENDPOINT", "http://minio:9000")
ACCESS_KEY = os.getenv("MINIO_ROOT_USER")
SECRET_KEY = os.getenv("MINIO_ROOT_PASSWORD")

PG_HOST = os.getenv("POSTGRES_HOST", "postgres")
PG_DB = os.getenv("POSTGRES_DB", "market_db")
PG_USER = os.getenv("POSTGRES_USER")
PG_PASS = os.getenv("POSTGRES_PASSWORD")

# Veritabanı şemalarında ve analitik sorgularda karakter seti uyumsuzluklarını önlemek için 
# kapsamlı bir Türkçe karakter transformasyon haritası oluşturdum.
TR_CHARS = {'ı': 'i', 'ğ': 'g', 'ü': 'u', 'ş': 's', 'ö': 'o', 'ç': 'c', 
            'İ': 'I', 'Ğ': 'G', 'Ü': 'U', 'Ş': 'S', 'Ö': 'O', 'Ç': 'C'}

def clean_column_name(col_name):
    """
    Veri temizliği (Data Sanitization) katmanı: 
    Sütun isimlerini SQL standartlarına ve veritabanı isimlendirme konvansiyonlarına 
    uygun hale getiriyorum. Özel karakterleri temizleyerek şema hatalarını minimize ettim.
    """
    for tr, en in TR_CHARS.items():
        col_name = col_name.replace(tr, en)
    # Alfanümerik olmayan tüm karakterleri alt çizgi ile değiştirerek tutarlılık sağladım.
    clean = re.sub(r'[^a-zA-Z0-9]', '_', col_name.strip())
    return clean.lower()

def process_batch_file(filename):
    """
    Dinamik Batch İşleme motoru: 
    Manuel olarak yüklenen CSV dosyalarını işleyerek Lakehouse ve RDBMS katmanlarına dağıtır.
    """
    print(f"Dinamik Batch İşlemi Başlatıldı: {filename}")

    # Spark oturumunu, MinIO (S3A) protokolüyle tam uyumlu ve 
    # dosya bazlı işlemlere optimize olacak şekilde yapılandırdım.
    spark = SparkSession.builder \
        .appName("UniversalBatchProcessor") \
        .config("spark.hadoop.fs.s3a.endpoint", MINIO_ENDPOINT) \
        .config("spark.hadoop.fs.s3a.access.key", ACCESS_KEY) \
        .config("spark.hadoop.fs.s3a.secret.key", SECRET_KEY) \
        .config("spark.hadoop.fs.s3a.path.style.access", "true") \
        .config("spark.hadoop.fs.s3a.impl", "org.apache.hadoop.fs.s3a.S3AFileSystem") \
        .getOrCreate()

    input_path = f"s3a://market-data/raw_batch_uploads/{filename}"

    try:
        # 1. Veri Okuma: CSV formatındaki ham veriyi, şema çıkarımı (inferSchema) 
        # özelliğini kullanarak Spark DataFrame yapısına alıyorum.
        df = spark.read.option("header", "true").option("inferSchema", "true").csv(input_path)
        
        # 2. Şema Standardizasyonu: Tüm sütun isimlerini temizlik fonksiyonundan 
        # geçirerek veritabanı uyumlu hale getiriyorum.
        cleaned_columns = [clean_column_name(c) for c in df.columns]
        df_clean = df.toDF(*cleaned_columns)

        # 3. Dinamik Tablo Yönetimi: Dosya isminden yola çıkarak 
        # otomatik tablo isimlendirme kurguladım.
        clean_filename = clean_column_name(filename.split('.')[0])
        table_name = f"upload_{clean_filename}"

        print(f"Hedef Tablo Yapılandırılıyor: {table_name}")
        
        # 4. Polyglot Persistence Stratejisi: 
        # Veriyi hem analitik katman (MinIO) hem de operasyonel raporlama katmanı (PostgreSQL) için kaydediyorum.
        
        # MinIO Katmanı: Veriyi ileride yapılacak büyük veri analizleri için 
        # yüksek performanslı Parquet formatında yedekliyorum.
        minio_path = f"s3a://market-data/batch_processed/{table_name}"
        df_clean.write.format("parquet").mode("overwrite").save(minio_path)
        print(f"MinIO üzerine Parquet formatında yedekleme tamamlandı: {minio_path}")

        # PostgreSQL Katmanı: Metabase gibi iş zekası araçlarının anlık erişimi için 
        # veriyi JDBC üzerinden ilişkisel veritabanına aktarıyorum.
        jdbc_url = f"jdbc:postgresql://{PG_HOST}:5432/{PG_DB}"
        db_properties = {
            "user": PG_USER,
            "password": PG_PASS,
            "driver": "org.postgresql.Driver"
        }
        
        df_clean.write.jdbc(url=jdbc_url, table=table_name, mode="overwrite", properties=db_properties)
        
        print(f"PostgreSQL üzerine tablo yazımı başarılı: {table_name}")
        print("Batch işleme süreci başarıyla sonuçlandı.")

    except Exception as e:
        print(f"Batch işleme sırasında kritik hata: {e}")
        sys.exit(1)
    finally:
        # Kaynak yönetimi: İşlem bittiğinde Spark oturumunu kapatarak sistem kaynaklarını serbest bırakıyorum.
        spark.stop()

if __name__ == "__main__":
    if len(sys.argv) > 1:
        fname = sys.argv[1]
        process_batch_file(fname)
    else:
        print("Hata: Dosya adı parametre olarak sağlanmalıdır.")