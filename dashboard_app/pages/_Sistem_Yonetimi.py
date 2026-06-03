import streamlit as st
import sys
import os
import docker
import pandas as pd
import psutil 
import time
import psycopg2
import redis
from psycopg2.extras import RealDictCursor
from datetime import datetime

# --- MODÜL YOLU AYARLARI ---
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# --- VERİTABANI VE REDIS BAĞLANTILARI ---
def get_db_connection():
    try:
        return psycopg2.connect(
            host=os.getenv("POSTGRES_HOST", "postgres"),
            database=os.getenv("POSTGRES_DB", "market_db"),
            user=os.getenv("POSTGRES_USER", "admin_lakehouse"),
            password=os.getenv("POSTGRES_PASSWORD", "SuperSecret_DB_Password_2026"),
            connect_timeout=3
        )
    except:
        return None

def get_redis_connection():
    try:
        r = redis.Redis(host=os.getenv("REDIS_HOST", "redis"), port=6379, db=0, decode_responses=True)
        r.ping()
        return r
    except:
        return None

# --- SAYFA AYARLARI ---
st.set_page_config(page_title="Radar Global | Control Plane", layout="wide", page_icon="🎛️")

# --- ENTERPRISE DARK CSS ---
st.markdown("""
<style>
    .stApp { background-color: #0E1117; }
    [data-testid="stContainer"] {
        background-color: #161920;
        border: 1px solid #303339;
        border-radius: 8px;
        padding: 20px;
    }
    [data-testid="stMetricValue"] { color: #00ADB5 !important; font-weight: 800; }
    .stButton button {
        background-color: #1E2127;
        border: 1px solid #00ADB5;
        color: #00ADB5;
        font-weight: bold;
        width: 100%;
    }
    .stButton button:hover {
        background-color: #00ADB5;
        color: white;
    }
    code { background-color: #000 !important; color: #00FF41 !important; }
</style>
""", unsafe_allow_html=True)

# --- BAŞLIK ---
c1, c2 = st.columns([3, 1])
with c1:
    st.title("🎛️ Radar Global Enterprise Control Plane")
    st.caption("Infrastructure Management • User CRM • Real-Time Monitoring")
with c2:
    st.markdown(f"<div style='text-align: right; color: #00ADB5;'>SYSTEM TIME: {datetime.now().strftime('%H:%M:%S')}</div>", unsafe_allow_html=True)

st.markdown("---")

# --- BÖLÜM 1: HOST TELEMETRY ---
st.subheader("🖥️ Sunucu Kaynak Durumu")
k1, k2, k3 = st.columns(3)
cpu = psutil.cpu_percent()
mem = psutil.virtual_memory()
disk = psutil.disk_usage('/')

with k1:
    with st.container():
        st.metric("CPU Usage", f"%{cpu}")
        st.progress(cpu/100)
with k2:
    with st.container():
        st.metric("RAM Usage", f"{mem.used/(1024**3):.1f}GB / {mem.total/(1024**3):.1f}GB")
        st.progress(mem.percent/100)
with k3:
    with st.container():
        st.metric("Disk Storage", f"%{disk.percent} Full")
        st.progress(disk.percent/100)

# --- BÖLÜM 2: DOCKER SERVICE MESH ---
st.subheader("📦 Mikroservis Sağlık Matrisi")
try:
    client = docker.from_env()
    containers = client.containers.list(all=True)
    grid = st.columns(4)
    services = ["binance_producer", "kafka", "spark-silver", "api_gateway", "postgres", "redis_cache", "ml-trainer", "grafana"]
    
    for idx, s_name in enumerate(services):
        cont = next((c for c in containers if s_name in c.name), None)
        with grid[idx % 4]:
            with st.container():
                if cont and cont.status == "running":
                    st.markdown(f"🟢 **{s_name.upper()}**")
                    st.caption("Service is healthy")
                else:
                    st.markdown(f"🔴 **{s_name.upper()}**")
                    st.caption("Service offline/restarting")
except:
    st.error("Docker Socket Error")

st.markdown("---")

# --- BÖLÜM 3: ANA YÖNETİM SEKMELERİ ---
tabs = st.tabs(["👥 Kullanıcı Yönetimi (CRM)", "🛡️ Güvenlik & Ban Listesi", "⚙️ Sistem Bakımı", "📜 Canlı Loglar"])

# --- TAB 1: USER MANAGEMENT (CRM) ---
with tabs[0]:
    st.subheader("User Authorization & Tier Management")
    conn = get_db_connection()
    r = get_redis_connection()
    if conn:
        cur = conn.cursor(cursor_factory=RealDictCursor)
        cur.execute("SELECT id, username, email, tier, api_key FROM api_users")
        users = cur.fetchall()
        df = pd.DataFrame(users)
        
        st.dataframe(df, use_container_width=True)
        
        c_up1, c_up2 = st.columns(2)
        with c_up1:
            with st.container():
                st.markdown("### 👑 Yetki Yükselt/Düşür")
                target_user = st.selectbox("Kullanıcı Seç:", df['username'].tolist() if not df.empty else [])
                new_tier = st.selectbox("Yeni Seviye:", ["FREE", "VIP"])
                if st.button("YETKİYİ GÜNCELLE"):
                    cur.execute("SELECT api_key FROM api_users WHERE username = %s", (target_user,))
                    user_rec = cur.fetchone()
                    cur.execute("UPDATE api_users SET tier = %s WHERE username = %s", (new_tier, target_user))
                    conn.commit()
                    if user_rec and r:
                        try:
                            r.delete(f"auth:api_key:{user_rec['api_key']}")
                        except Exception as e:
                            st.warning(f"Redis cache temizlenemedi: {e}")
                    st.success(f"{target_user} artık {new_tier}!")
                    time.sleep(1)
                    st.rerun()
        
        with c_up2:
            with st.container():
                st.markdown("### 🗑️ Kullanıcıyı Sil")
                del_user = st.selectbox("Silinecek Hesap:", df['username'].tolist() if not df.empty else [])
                if st.button("HESABI KALICI SİL"):
                    cur.execute("SELECT api_key FROM api_users WHERE username = %s", (del_user,))
                    user_rec = cur.fetchone()
                    cur.execute("DELETE FROM api_users WHERE username = %s", (del_user,))
                    conn.commit()
                    if user_rec and r:
                        try:
                            r.delete(f"auth:api_key:{user_rec['api_key']}")
                        except Exception as e:
                            st.warning(f"Redis cache temizlenemedi: {e}")
                    st.error(f"{del_user} sistemden temizlendi.")
                    time.sleep(1)
                    st.rerun()
        conn.close()

# --- TAB 2: SECURITY & BAN LIST ---
with tabs[1]:
    st.subheader("Redis Distributed Ban Manager")
    r = get_redis_connection()
    if r:
        all_keys = r.keys("ban:*")
        if all_keys:
            st.warning(f"Sistemde {len(all_keys)} adet banlı kullanıcı/IP tespit edildi.")
            ban_data = []
            for k in all_keys:
                ban_data.append({"API_KEY": k.replace("ban:", ""), "Status": r.get(k)})
            
            st.table(pd.DataFrame(ban_data))
            
            unban_target = st.selectbox("Banı Kaldırılacak Key:", [d['API_KEY'] for d in ban_data])
            if st.button("🔓 SEÇİLİ KULLANICIYI AFFET (UNBAN)"):
                r.delete(f"ban:{unban_target}")
                st.success("Kullanıcı erişimi tekrar açıldı.")
                st.rerun()
        else:
            st.success("Temiz! Şu an banlı kullanıcı bulunmuyor.")
    else:
        st.error("Redis Connection Failed")

# --- TAB 3: MAINTENANCE (SPARK & DELTA) ---
with tabs[2]:
    st.subheader("Lakehouse Operations")
    col_m1, col_m2 = st.columns(2)
    with col_m1:
        with st.container():
            st.markdown("### 🧹 Delta Optimize")
            st.write("Veri parçacıklarını birleştirir, sorgu hızını artırır.")
            if st.button("SPARK OPTIMIZE BAŞLAT"):
                with st.status("Spark Job Running...") as s:
                    try:
                        res = client.containers.get("spark-silver").exec_run("python maintenance_job.py")
                        st.code(res.output.decode())
                        s.update(label="Başarıyla Tamamlandı", state="complete")
                    except: st.error("Spark Container Error")
    
    with col_m2:
        with st.container():
            st.markdown("### 🧪 Veri Kalite Testi")
            st.write("Null değerleri ve negatif fiyatları tarar.")
            if st.button("QUALITY GATE ÇALIŞTIR"):
                with st.status("Scanning Data...") as s:
                    try:
                        res = client.containers.get("spark-silver").exec_run("python quality_gate.py")
                        st.code(res.output.decode())
                        s.update(label="Tarama Bitti", state="complete")
                    except: st.error("Service Error")

# --- TAB 4: LIVE LOGS ---
with tabs[3]:
    st.subheader("Real-Time Container Logs")
    target_log = st.selectbox("Logu İzlenecek Servis:", [c.name for c in containers])
    if st.button("LOGLARI GETİR"):
        log_output = client.containers.get(target_log).logs(tail=200).decode("utf-8")
        st.code(log_output, language="bash")

st.markdown("---")
st.caption("© 2026 Radar Global Ops Center | Developed by Ömer Çakan")