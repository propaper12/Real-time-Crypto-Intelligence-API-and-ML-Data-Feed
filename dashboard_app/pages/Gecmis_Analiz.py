import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from deltalake import DeltaTable
import os

# --- 0. SAYFA AYARLARI ---
st.set_page_config(page_title="Pro Terminal | Batch Analytics", layout="wide", page_icon="📈")

# --- 1. KURUMSAL CSS (Binance Style + Eğitim Kutuları) ---
st.markdown("""
<style>
    .stApp { background-color: #0b0e11; color: #eaecef; }
    .metric-card { background-color: #1e2329; padding: 20px; border-radius: 10px; border: 1px solid #2b3139; text-align: center; box-shadow: 0 4px 6px rgba(0,0,0,0.3); }
    .metric-value { font-size: 26px; font-weight: bold; color: #FCD535; }
    .metric-label { font-size: 13px; color: #848E9C; text-transform: uppercase; letter-spacing: 1px;}
    .trader-edu-box { background-color: #161a1e; padding: 15px 20px; border-radius: 8px; border-left: 4px solid #0ecb81; font-size: 14px; margin-top: -15px; margin-bottom: 25px; color: #b7bdc6; line-height: 1.6; }
    .trader-edu-box strong { color: #eaecef; }
    h1, h2, h3, h4 { color: #FCD535 !important; }
</style>
""", unsafe_allow_html=True)

# --- 2. S3 BAĞLANTI (LAKEHOUSE) ---
storage_options = {
    "AWS_ACCESS_KEY_ID": os.getenv("MINIO_ROOT_USER", "admin"),
    "AWS_SECRET_ACCESS_KEY": os.getenv("MINIO_ROOT_PASSWORD", "admin12345"),
    "AWS_ENDPOINT_URL": os.getenv("MINIO_ENDPOINT", "http://minio:9000"), 
    "AWS_REGION": "us-east-1",
    "AWS_S3_ALLOW_UNSAFE_RENAME": "true",
    "AWS_ALLOW_HTTP": "true"
}

# --- 3. TEKNİK İNDİKATÖR MOTORU ---
def add_indicators(df):
    df = df.copy()
    # Getiri
    df['returns'] = df['close'].pct_change()
    
    # Hareketli Ortalamalar
    df['MA7'] = df['close'].rolling(window=7).mean()
    df['MA25'] = df['close'].rolling(window=25).mean()
    df['MA99'] = df['close'].rolling(window=99).mean()
    
    # RSI
    delta = df['close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
    df['RSI'] = 100 - (100 / (1 + (gain / loss)))
    
    # Bollinger Bantları
    df['BB_mid'] = df['close'].rolling(window=20).mean()
    df['BB_std'] = df['close'].rolling(window=20).std()
    df['BB_upper'] = df['BB_mid'] + (df['BB_std'] * 2)
    df['BB_lower'] = df['BB_mid'] - (df['BB_std'] * 2)
    
    # MACD
    exp1 = df['close'].ewm(span=12, adjust=False).mean()
    exp2 = df['close'].ewm(span=26, adjust=False).mean()
    df['MACD'] = exp1 - exp2
    df['Signal'] = df['MACD'].ewm(span=9, adjust=False).mean()
    df['MACD_Hist'] = df['MACD'] - df['Signal']
    
    return df

# --- 4. VERİ ÇEKME (CACHE) ---
@st.cache_data(ttl=3600, show_spinner=False)
def load_full_batch_data(interval):
    path = "s3://market-data/historical_daily_delta" if interval == "Günlük" else "s3://market-data/historical_hourly_delta"
    try:
        dt = DeltaTable(path, storage_options=storage_options)
        return dt.to_pandas()
    except Exception as e:
        return pd.DataFrame()

# --- 5. YAN PANEL (SIDEBAR) ---
with st.sidebar:
    st.header("⚙️ Veri Seti Ayarları")
    time_interval = st.radio("Zaman Periyodu", ["Günlük", "Saatlik"])
    all_data = load_full_batch_data(time_interval)
    
    if not all_data.empty:
        coin_list = sorted(all_data['symbol'].unique())
        selected_coin = st.selectbox("İncelenecek Varlık", coin_list)
        df_target = all_data[all_data['symbol'] == selected_coin].copy()
    else:
        st.error("MinIO bağlantısı veya Delta tablosu bulunamadı.")
        st.stop()
        
    st.divider()
    st.info("💡 **Batch Processing:** Grafikler, Lambda mimarisinin yığın veri katmanından (Data Lakehouse) beslenmektedir.")

# --- 6. VERİ HAZIRLIĞI ---
df_target = df_target.sort_values("timestamp")
df_target['timestamp'] = pd.to_datetime(df_target['timestamp'])
df_target = add_indicators(df_target).dropna()

# --- 7. ANA EKRAN VE METRİKLER ---
st.title(f"🔍 {selected_coin} Kantitatif Analiz Terminali")

c1, c2, c3, c4 = st.columns(4)
c1.markdown(f"<div class='metric-card'><div class='metric-label'>Kapanış Fiyatı</div><div class='metric-value'>${df_target['close'].iloc[-1]:,.2f}</div></div>", unsafe_allow_html=True)
c2.markdown(f"<div class='metric-card'><div class='metric-label'>RSI Momentum</div><div class='metric-value'>{df_target['RSI'].iloc[-1]:.2f}</div></div>", unsafe_allow_html=True)
c3.markdown(f"<div class='metric-card'><div class='metric-label'>Son Hacim</div><div class='metric-value'>${df_target['volume'].iloc[-1]/1e3:.1f}K</div></div>", unsafe_allow_html=True)
c4.markdown(f"<div class='metric-card'><div class='metric-label'>Uzun Vade Trend</div><div class='metric-value' style='color:{'#0ecb81' if df_target['close'].iloc[-1] > df_target['MA99'].iloc[-1] else '#f6465d'};'>{'BOĞA 🟢' if df_target['close'].iloc[-1] > df_target['MA99'].iloc[-1] else 'AYI 🔴'}</div></div>", unsafe_allow_html=True)

st.write("")

# ==========================================
# GRAFİK 1: FİYAT HAREKETİ VE TREND (ANA GRAFİK)
# ==========================================
st.subheader("📊 1. Fiyat Hareketi, Trend ve Volatilite Bantları")
fig_price = go.Figure()

# Mum Grafiği
fig_price.add_trace(go.Candlestick(x=df_target['timestamp'], open=df_target['open'], high=df_target['high'], low=df_target['low'], close=df_target['close'], name='OHLC', increasing_line_color='#0ecb81', decreasing_line_color='#f6465d'))
# Bollinger Bantları
fig_price.add_trace(go.Scatter(x=df_target['timestamp'], y=df_target['BB_upper'], line=dict(color='rgba(132, 142, 156, 0.4)'), name='BB Üst Direnç'))
fig_price.add_trace(go.Scatter(x=df_target['timestamp'], y=df_target['BB_lower'], line=dict(color='rgba(132, 142, 156, 0.4)'), fill='tonexty', fillcolor='rgba(132, 142, 156, 0.05)', name='BB Alt Destek'))
# Hareketli Ortalamalar
fig_price.add_trace(go.Scatter(x=df_target['timestamp'], y=df_target['MA7'], line=dict(color='#fcd535', width=1.5), name='MA7 (Hızlı Trend)'))
fig_price.add_trace(go.Scatter(x=df_target['timestamp'], y=df_target['MA99'], line=dict(color='#3498db', width=2), name='MA99 (Ana Trend)'))

fig_price.update_layout(template="plotly_dark", height=500, xaxis_rangeslider_visible=False, margin=dict(t=10, b=10))
st.plotly_chart(fig_price, use_container_width=True)

st.markdown("""
<div class='trader-edu-box'>
    <strong>📖 Terminal Okuması (Fiyat Aksiyonu):</strong> Bu grafik piyasanın kalbidir. <span style='color:#3498db;'>Mavi çizgi (MA99)</span> uzun vadeli trendin yönünü belirler; fiyat bu çizginin üzerindeyse piyasa pozitif (Boğa) eğilimlidir. Gri renkle gölgelendirilmiş alan <strong>Bollinger Bantlarıdır</strong>. Fiyatın üst banda çarpması aşırı fiyatlanmayı (direnç), alt banda çarpması ise ucuzlamayı (destek) işaret eder. Bantların daralması, yakında sert bir kırılım (volatilite patlaması) olacağının habercisidir.
</div>
""", unsafe_allow_html=True)

# ==========================================
# GRAFİK 2 & 3: HACİM VE MACD (YAN YANA)
# ==========================================
col_vol, col_macd = st.columns(2)

with col_vol:
    st.subheader("🌊 2. Likidite ve Hacim Profili")
    colors_vol = ['#f6465d' if r['open'] > r['close'] else '#0ecb81' for i, r in df_target.iterrows()]
    fig_vol = go.Figure()
    fig_vol.add_trace(go.Bar(x=df_target['timestamp'], y=df_target['volume'], marker_color=colors_vol, name='Hacim'))
    fig_vol.update_layout(template="plotly_dark", height=350, margin=dict(t=10, b=10))
    st.plotly_chart(fig_vol, use_container_width=True)
    
    st.markdown("""
    <div class='trader-edu-box'>
        <strong>📖 Terminal Okuması (Hacim):</strong> Hacim, fiyat hareketinin <em>'yakıtıdır'</em>. Yukarı yönlü bir fiyat kırılımı eğer yüksek hacimle (büyük yeşil çubuklar) desteklenmiyorsa, bu büyük ihtimalle bir "Boğa Tuzağıdır" (Fakeout) ve fiyat geri düşecektir. Düşük hacimli dönemler piyasanın kararsız olduğunu gösterir.
    </div>
    """, unsafe_allow_html=True)

with col_macd:
    st.subheader("⚡ 3. MACD Momentum İvmesi")
    fig_macd = go.Figure()
    fig_macd.add_trace(go.Bar(x=df_target['timestamp'], y=df_target['MACD_Hist'], marker_color=['#0ecb81' if val > 0 else '#f6465d' for val in df_target['MACD_Hist']], name='Histogram'))
    fig_macd.add_trace(go.Scatter(x=df_target['timestamp'], y=df_target['MACD'], line=dict(color='#00d2ff', width=2), name='MACD Çizgisi'))
    fig_macd.add_trace(go.Scatter(x=df_target['timestamp'], y=df_target['Signal'], line=dict(color='#ff9ff3', width=2), name='Sinyal Çizgisi'))
    fig_macd.update_layout(template="plotly_dark", height=350, margin=dict(t=10, b=10))
    st.plotly_chart(fig_macd, use_container_width=True)
    
    st.markdown("""
    <div class='trader-edu-box'>
        <strong>📖 Terminal Okuması (MACD):</strong> Trendin gücünü ve olası dönüş noktalarını yakalar. <span style='color:#00d2ff;'>Mavi çizginin</span> (MACD), <span style='color:#ff9ff3;'>Pembe çizgiyi</span> (Sinyal) yukarı yönlü kesmesi klasik bir <strong>AL (Buy)</strong> sinyalidir. Histogram çubuklarının sıfır çizgisinin üzerine çıkarak büyümesi, yükseliş momentumunun hızlandığını teyit eder.
    </div>
    """, unsafe_allow_html=True)

# ==========================================
# GRAFİK 4 & 5: RSI VE RİSK (DRAWDOWN) (YAN YANA)
# ==========================================
col_rsi, col_dd = st.columns(2)

with col_rsi:
    st.subheader("⚖️ 4. RSI (Aşırı Alım/Satım Dengesi)")
    fig_rsi = go.Figure()
    fig_rsi.add_trace(go.Scatter(x=df_target['timestamp'], y=df_target['RSI'], line=dict(color='#FCD535', width=2), name='RSI 14'))
    fig_rsi.add_hrect(y0=70, y1=100, fillcolor='#f6465d', opacity=0.1, line_width=0)
    fig_rsi.add_hrect(y0=0, y1=30, fillcolor='#0ecb81', opacity=0.1, line_width=0)
    fig_rsi.add_hline(y=70, line_dash="dash", line_color="#f6465d")
    fig_rsi.add_hline(y=30, line_dash="dash", line_color="#0ecb81")
    fig_rsi.update_layout(template="plotly_dark", height=300, yaxis=dict(range=[0, 100]), margin=dict(t=10, b=10))
    st.plotly_chart(fig_rsi, use_container_width=True)
    
    st.markdown("""
    <div class='trader-edu-box'>
        <strong>📖 Terminal Okuması (RSI):</strong> Fiyatın ne kadar şiştiğini veya ucuzladığını 0 ile 100 arasında ölçer. Kırmızı bölge (>70) piyasanın "Aşırı Alındığını" (Overbought) ve kâr satışlarının gelebileceğini; Yeşil bölge (<30) ise varlığın "Aşırı Satıldığını" (Oversold) ve dipten tepki alımlarının başlayabileceğini ifade eder.
    </div>
    """, unsafe_allow_html=True)

with col_dd:
    st.subheader("📉 5. Maksimum Kayıp (Pain Index)")
    rolling_max = df_target['close'].cummax()
    drawdown = (df_target['close'] - rolling_max) / rolling_max
    fig_dd = go.Figure()
    fig_dd.add_trace(go.Scatter(x=df_target['timestamp'], y=drawdown*100, fill='tozeroy', line=dict(color='#f6465d'), name='Drawdown %'))
    fig_dd.update_layout(template="plotly_dark", height=300, margin=dict(t=10, b=10), yaxis_title="% Kayıp")
    st.plotly_chart(fig_dd, use_container_width=True)
    
    st.markdown("""
    <div class='trader-edu-box'>
        <strong>📖 Terminal Okuması (Drawdown):</strong> Bir portföy yöneticisinin en çok baktığı risk metriğidir (Acı Endeksi). Varlığın ulaştığı en yüksek tarihi zirveden (ATH) o anki fiyata kadar yüzde kaç değer kaybettiğini gösterir. Derin kırmızı çukurlar, ayı piyasası krizlerini ve toparlanma sürelerini işaret eder.
    </div>
    """, unsafe_allow_html=True)

# ==========================================
# GRAFİK 6 & 7: QUANTS (MEVSİMSELLİK VE KORELASYON)
# ==========================================
st.divider()
col_hm, col_corr = st.columns(2)

with col_hm:
    st.subheader("📅 6. Mevsimsellik Isı Haritası")
    df_target['weekday'] = df_target['timestamp'].dt.day_name()
    df_target['month'] = df_target['timestamp'].dt.month_name()
    days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    months = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December']
    
    pivot = df_target.pivot_table(index='month', columns='weekday', values='returns', aggfunc='mean') * 100
    pivot = pivot.reindex(index=months, columns=days)
    
    fig_hm = px.imshow(pivot, color_continuous_scale='RdYlGn', text_auto=".2f", labels=dict(color="Ort Getiri %"))
    fig_hm.update_layout(template="plotly_dark", height=450, margin=dict(t=10, b=10))
    st.plotly_chart(fig_hm, use_container_width=True)
    
    st.markdown("""
    <div class='trader-edu-box'>
        <strong>📖 Terminal Okuması (Mevsimsellik):</strong> Niceliksel (Quant) analiz yaklaşımıdır. Kırmızı hücreler tarihsel olarak para kaybedilen, koyu yeşil hücreler ise kâr edilen dönemleri gösterir. Örneğin; "Salı günleri genelde yükseliş mi oluyor?" gibi takvimsel algoritmik stratejiler (Day-of-the-Week effect) bu tabloya bakılarak kurulur.
    </div>
    """, unsafe_allow_html=True)

with col_corr:
    st.subheader("🔗 7. Ekosistem Korelasyon Matrisi")
    corr_raw = all_data.pivot(index='timestamp', columns='symbol', values='close').pct_change()
    fig_corr = px.imshow(corr_raw.corr(), color_continuous_scale='Viridis', text_auto=".2f")
    fig_corr.update_layout(template="plotly_dark", height=450, margin=dict(t=10, b=10))
    st.plotly_chart(fig_corr, use_container_width=True)
    
    st.markdown("""
    <div class='trader-edu-box'>
        <strong>📖 Terminal Okuması (Korelasyon):</strong> Varlıkların birbirine olan bağımlılığını (1.00 ile -1.00 arası) ölçer. 1.00 değeri iki coinin birebir aynı hareket ettiğini, negatif değerler ise ters yöne gittiklerini gösterir. Tüm coinler birbirine 0.90 oranında bağlıysa (koyu sarı), sepet yapmanın riski düşürmediği (sistemik risk olduğu) anlaşılır.
    </div>
    """, unsafe_allow_html=True)

# ==========================================
# 8. HAM VERİ GÖRÜNÜMÜ
# ==========================================
st.divider()
with st.expander("📝 Data Engineering - Lakehouse Ham Veri Kayıtlarını Görüntüle"):
    st.dataframe(df_target.sort_values("timestamp", ascending=False).head(100), use_container_width=True)
