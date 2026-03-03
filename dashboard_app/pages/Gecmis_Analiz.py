import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from deltalake import DeltaTable
import os

# Sayfa Ayarları
st.set_page_config(page_title="Geçmiş Veri (Batch) Analizi", layout="wide", page_icon="🕰️")

# CSS ile Binance tarzı karanlık mod tasarımı
st.markdown("""
<style>
    .stApp { background-color: #0b0e11; color: #eaecef; }
    .metric-card { background-color: #1e2329; padding: 15px; border-radius: 8px; border: 1px solid #2b3139; text-align: center; }
    .metric-value { font-size: 24px; font-weight: bold; color: #FCD535; }
    .metric-label { font-size: 14px; color: #848E9C; }
</style>
""", unsafe_allow_html=True)

st.title("🕰️ Uzun Vadeli (Batch) Trend Analizi")
st.markdown("Bu modül, Lambda mimarisinin **Batch Processing** bacağıdır. Veriler Kafka'dan değil, doğrudan MinIO Delta Lake üzerinden (S3) sorgulanır.")

# S3 Bağlantı Ayarları
storage_options = {
    "AWS_ACCESS_KEY_ID": os.getenv("MINIO_ROOT_USER", "admin"),
    "AWS_SECRET_ACCESS_KEY": os.getenv("MINIO_ROOT_PASSWORD", "admin12345"),
    "AWS_ENDPOINT_URL": os.getenv("MINIO_ENDPOINT", "http://minio:9000"), 
    "AWS_REGION": "us-east-1",
    "AWS_S3_ALLOW_UNSAFE_RENAME": "true",
    "AWS_ALLOW_HTTP": "true"
}

# --- CACHE İLE OPTİMİZE EDİLMİŞ VERİ OKUMA ---
@st.cache_data(ttl=3600, show_spinner=False)
def load_historical_data(symbol, interval):
    path = "s3://market-data/historical_daily_delta" if interval == "Günlük (10 Yıl)" else "s3://market-data/historical_hourly_delta"
    
    try:
        dt = DeltaTable(path, storage_options=storage_options)
        # Sadece seçilen coini okuyoruz (Predicate Pushdown - Performans için kritik)
        df = dt.to_pandas(partitions=[("symbol", "=", symbol)])
        
        if not df.empty:
            df = df.sort_values("timestamp")
            # Tarihleri okunabilir yap
            df['timestamp'] = pd.to_datetime(df['timestamp'])
        return df
    except Exception as e:
        return pd.DataFrame()

# --- YAN PANEL (FİLTRELER) ---
with st.sidebar:
    st.header("⚙️ Analiz Ayarları")
    
    # Sisteme eklediğimiz coinler
    coin_list = ["BTCUSDT", "ETHUSDT", "SOLUSDT", "XRPUSDT", "AVAXUSDT"]
    selected_coin = st.selectbox("Varlık Seçimi", coin_list)
    
    time_interval = st.radio("Zaman Dilimi", ["Günlük (10 Yıl)", "Saatlik (Son 2 Yıl)"])
    
    st.divider()
    st.info("💡 **Mimari Not:** Bu veriler PostgreSQL'i yormadan, Parquet/Delta formatında saniyeler içinde AWS S3 (MinIO) mimarisinden RAM'e çekilmektedir.")

# --- VERİ YÜKLEME ---
with st.spinner("Data Lake (S3) üzerinden veriler getiriliyor..."):
    df = load_historical_data(selected_coin, time_interval)

if df.empty:
    st.warning(f"{selected_coin} için {time_interval} verisi bulunamadı. Lütfen önce Batch ETL scriptini çalıştırın.")
else:
    # --- METRİK HESAPLAMALARI ---
    current_price = df['close'].iloc[-1]
    ath = df['high'].max() # All Time High
    atl = df['low'].min()  # All Time Low
    ath_drop = ((current_price - ath) / ath) * 100
    
    # Ekrandaki Metrik Kartları
    c1, c2, c3, c4 = st.columns(4)
    c1.markdown(f"<div class='metric-card'><div class='metric-label'>Kapanış Fiyatı</div><div class='metric-value'>${current_price:,.2f}</div></div>", unsafe_allow_html=True)
    c2.markdown(f"<div class='metric-card'><div class='metric-label'>Zirve (ATH)</div><div class='metric-value'>${ath:,.2f}</div></div>", unsafe_allow_html=True)
    c3.markdown(f"<div class='metric-card'><div class='metric-label'>Zirveden Uzaklık</div><div class='metric-value' style='color:#f6465d;'>{ath_drop:.2f}%</div></div>", unsafe_allow_html=True)
    c4.markdown(f"<div class='metric-card'><div class='metric-label'>Toplam Veri (Satır)</div><div class='metric-value' style='color:#0ecb81;'>{len(df):,}</div></div>", unsafe_allow_html=True)
    
    st.write("") # Boşluk
    
    # --- PROFESYONEL FİNANSAL GRAFİK (MUM + HACİM) ---
    fig = make_subplots(rows=2, cols=1, shared_xaxes=True, 
                        vertical_spacing=0.03, subplot_titles=(f'{selected_coin} Fiyat Hareketi', 'İşlem Hacmi'),
                        row_width=[0.2, 0.7])

    # 1. Candlestick (Mum Grafiği)
    fig.add_trace(go.Candlestick(
        x=df['timestamp'], open=df['open'], high=df['high'], low=df['low'], close=df['close'],
        name='Fiyat', increasing_line_color='#0ecb81', decreasing_line_color='#f6465d'
    ), row=1, col=1)

    # Basit Hareketli Ortalamalar (SMA)
    if len(df) > 50:
        df['SMA50'] = df['close'].rolling(window=50).mean()
        fig.add_trace(go.Scatter(x=df['timestamp'], y=df['SMA50'], line=dict(color='#FCD535', width=1.5), name='SMA 50'), row=1, col=1)

    # 2. Hacim (Bar Grafiği)
    colors = ['#0ecb81' if row['close'] >= row['open'] else '#f6465d' for index, row in df.iterrows()]
    fig.add_trace(go.Bar(x=df['timestamp'], y=df['volume'], marker_color=colors, name='Hacim'), row=2, col=1)

    # Grafik Ayarları
    fig.update_layout(
        template="plotly_dark", height=700, margin=dict(l=0, r=0, t=30, b=0),
        plot_bgcolor='#0b0e11', paper_bgcolor='#0b0e11', showlegend=True,
        xaxis_rangeslider_visible=False # Alt kısımdaki gereksiz kaydırma çubuğunu kapat
    )
    fig.update_yaxes(title_text="Fiyat ($)", row=1, col=1)
    fig.update_yaxes(title_text="Hacim", row=2, col=1)

    st.plotly_chart(fig, use_container_width=True)
    
    # Veri Tablosu Görüntüleyici
    with st.expander("Tablo Olarak Görüntüle (Ham Veri)"):
        st.dataframe(df.sort_values("timestamp", ascending=False).head(100), use_container_width=True)