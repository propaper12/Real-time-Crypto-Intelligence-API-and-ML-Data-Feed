import psycopg2
import secrets
import os
import sys

def get_db_connection():
    try:
        # Docker içinden çalışacağı için host'u çevresel değişkenlerden alıyoruz
        return psycopg2.connect(
            host=os.getenv("POSTGRES_HOST", "postgres"),
            database=os.getenv("POSTGRES_DB", "market_db"),
            user=os.getenv("POSTGRES_USER", "admin_lakehouse"),
            password=os.getenv("POSTGRES_PASSWORD", "SuperSecret_DB_Password_2026")
        )
    except Exception as e:
        print(f"❌ Veritabanı hatası: {e}")
        return None

def setup_database():
    conn = get_db_connection()
    if not conn: return
    cur = conn.cursor()
    # Müşterileri ve şifrelerini tutacağımız tabloyu oluşturuyoruz
    cur.execute("""
        CREATE TABLE IF NOT EXISTS api_users (
            id SERIAL PRIMARY KEY,
            username VARCHAR(50) UNIQUE NOT NULL,
            email VARCHAR(255) UNIQUE NOT NULL,
            api_key VARCHAR(64) UNIQUE NOT NULL,
            tier VARCHAR(20) DEFAULT 'PRO',
            password_hash VARCHAR(255),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    """)
    conn.commit()
    cur.close()
    conn.close()
    print("✅ Güvenlik tablosu (api_users) veritabanında hazır.")

def create_user(username, tier="PRO"):
    conn = get_db_connection()
    if not conn: return
    
    # Kırılması imkansız 32 bytelık rastgele bir şifre üretiyoruz
    raw_key = secrets.token_urlsafe(32)
    api_key = f"sk_live_{raw_key}" # sk_live = Secret Key Live (Stripe ve OpenAI standardı)
    email = f"{username.lower()}@radarpro.io"
    
    try:
        cur = conn.cursor()
        cur.execute("INSERT INTO api_users (username, email, api_key, tier) VALUES (%s, %s, %s, %s)", 
                    (username, email, api_key, tier))
        conn.commit()
        print("\n🎉 YENİ MÜŞTERİ BAŞARIYLA OLUŞTURULDU!")
        print("-" * 50)
        print(f"👤 Müşteri Adı : {username}")
        print(f"💎 Paket Tipi  : {tier}")
        print(f"🔑 API ANAHTARI: {api_key}")
        print("-" * 50)
        print("Lütfen bu anahtarı müşteriye iletin. Kaybedilirse sistemden silip yenisini üretmeniz gerekir.\n")
    except psycopg2.errors.UniqueViolation:
        print(f"⚠️ Hata: '{username}' adında bir müşteri zaten var!")
    finally:
        cur.close()
        conn.close()

if __name__ == "__main__":
    setup_database()
    # Eğer terminalden isim girildiyse ona göre üret, girilmediyse varsayılan "Test_User" üret
    user_name = sys.argv[1] if len(sys.argv) > 1 else "Demo_Musteri"
    create_user(user_name)