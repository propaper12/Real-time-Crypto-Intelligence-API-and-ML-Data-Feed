import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import time
import json
import os
from datetime import datetime
from kafka import KafkaConsumer
from sqlalchemy import create_engine

# ==========================================
# 0. SAYFA KONFİGÜRASYONU
# ==========================================
st.set_page_config(page_title="RadarPro | VIP Quant Terminal", layout="wide", page_icon="🐺")

# ==========================================
# 1. BAĞLANTI VE ALTYAPI AYARLARI
# ==========================================
PG_USER = "admin_lakehouse"
PG_PASS = "SuperSecret_DB_Password_2026"
PG_HOST = "postgres"
PG_DB = "market_db"
DB_URL = f"postgresql://{PG_USER}:{PG_PASS}@{PG_HOST}:5432/{PG_DB}"
KAFKA_SERVER = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "kafka:9092")

# ==========================================
# 2. KURUMSAL UI/UX TASARIMI (CSS)
# ==========================================
st.markdown("""
<style>
    .stApp { background-color: #060709; color: #d1d4dc; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; }
    .block-container { padding-top: 2rem; max-width: 98%; }
    [data-testid="stMetricValue"] { font-size: 24px; font-weight: 900; color: #ffffff !important; font-family: 'Courier New', Courier, monospace;}
    [data-testid="stMetricLabel"] { color: #848E9C !important; font-weight: bold; text-transform: uppercase; font-size: 11px;}
    div[data-testid="metric-container"] { background-color: #0a0c10; padding: 15px; border-radius: 8px; border: 1px solid #1a1e24; box-shadow: 0 4px 10px rgba(0,0,0,0.3);}
    .analysis-box { background-color: #0a0c10; padding: 15px; border-radius: 8px; border-left: 4px solid #00d2ff; font-size: 14px; color: #d1d4dc; margin-top: 10px; margin-bottom: 20px; border: 1px solid #1a1e24;}
    .info-box { background-color: #0d1117; padding: 12px; border-radius: 6px; font-size: 12px; color: #848E9C; border-left: 3px solid #FCD535; margin-bottom: 15px; line-height: 1.5; border-top: 1px solid #1a1e24; border-right: 1px solid #1a1e24; border-bottom: 1px solid #1a1e24;}
    .highlight-up { color: #00ff95; font-weight: bold; }
    .highlight-down { color: #ff3b5c; font-weight: bold; }
    .live-indicator { color: #00ff95; font-weight: 900; animation: blinker 1.5s linear infinite; font-size: 14px; margin-right: 10px; letter-spacing: 1px;}
    .live-clock { color: #848E9C; font-size: 16px; font-weight: bold; font-family: 'Courier New', Courier, monospace; background-color: #0a0c10; padding: 6px 16px; border-radius: 6px; border: 1px solid #1a1e24;}
    @keyframes blinker { 50% { opacity: 0.3; } }
    h3 { color: #FCD535 !important; font-size: 18px !important; text-transform: uppercase; letter-spacing: 1px; font-weight: 900 !important; margin-bottom: 15px !important;}
    h5 { color: #d1d4dc !important; font-size: 14px !important; text-transform: uppercase; letter-spacing: 1px; font-weight: bold !important;}
</style>
""", unsafe_allow_html=True)

# ==========================================
# 3. VERİ İŞLEME VE İNDİKATÖR FONKSİYONLARI
# ==========================================
def calculate_technical_indicators(df):
    df = df.copy()
    df['SMA_20'] = df['average_price'].rolling(window=20).mean()
    df['Std_Dev'] = df['average_price'].rolling(window=20).std()
    df['Bollinger_Upper'] = df['SMA_20'] + (df['Std_Dev'] * 2)
    df['Bollinger_Lower'] = df['SMA_20'] - (df['Std_Dev'] * 2)
    
    delta = df['average_price'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
    df['RSI'] = 100 - (100 / (1 + (gain / loss)))
    
    df['EMA12'] = df['average_price'].ewm(span=12, adjust=False).mean()
    df['EMA26'] = df['average_price'].ewm(span=26, adjust=False).mean()
    df['MACD'] = df['EMA12'] - df['EMA26']
    df['Signal_Line'] = df['MACD'].ewm(span=9, adjust=False).mean()
    return df.fillna(0)

def process_data_to_ohlc(df, interval='5s'):
    df['processed_time'] = pd.to_datetime(df['processed_time'])
    df.set_index('processed_time', inplace=True)
    ohlc = df['average_price'].resample(interval).ohlc()
    
    base_cols = ['predicted_price', 'Bollinger_Upper', 'Bollinger_Lower', 'MACD', 'Signal_Line', 'RSI', 'volatility', 'SMA_20']
    premium_last_cols = [c for c in ['trade_side', 'is_buyer_maker', 'cvd', 'buy_wall_usd', 'sell_wall_usd', 'vpin_score', 'imbalance_ratio', 'mark_price', 'funding_rate'] if c in df.columns]
    premium_sum_cols = [c for c in ['liq_buy_usd', 'liq_sell_usd', 'volume_usd'] if c in df.columns]
    
    indicators_last = df[base_cols + premium_last_cols].resample(interval).last()
    indicators_sum = df[premium_sum_cols].resample(interval).sum()
        
    return pd.concat([ohlc, indicators_last, indicators_sum], axis=1).dropna().reset_index()

# ==========================================
# 4. KAFKA VE DB BAĞLANTILARI
# ==========================================
@st.cache_data(ttl=5, show_spinner=False)
def get_data_from_db():
    try:
        engine = create_engine(DB_URL)
        df = pd.read_sql("SELECT * FROM market_data ORDER BY processed_time DESC LIMIT 1500", engine)
        if not df.empty:
            df = df.sort_values('processed_time')
            df = df.groupby('symbol').apply(calculate_technical_indicators).reset_index(drop=True)
        return df
    except: return pd.DataFrame()

if 'kafka_consumer' not in st.session_state:
    try:
        st.session_state['kafka_consumer'] = KafkaConsumer(
            'market_data', bootstrap_servers=KAFKA_SERVER, auto_offset_reset='latest',
            enable_auto_commit=False, value_deserializer=lambda x: json.loads(x.decode('utf-8')),
            consumer_timeout_ms=50
        )
    except: st.session_state['kafka_consumer'] = None

def get_live_price(symbol):
    live_p = None
    if st.session_state['kafka_consumer']:
        try:
            msg_pack = st.session_state['kafka_consumer'].poll(timeout_ms=50)
            for tp, messages in msg_pack.items():
                for msg in messages:
                    if msg.value.get('symbol') == symbol: live_p = float(msg.value.get('price'))
        except: pass
    return live_p

# ==========================================
# 5. UI STATE YÖNETİMİ
# ==========================================
if 'selected_coin' not in st.session_state: st.session_state['selected_coin'] = None
if 'refresh_counter' not in st.session_state: st.session_state['refresh_counter'] = 5

# ==========================================
# 6. YAN PANEL (SIDEBAR)
# ==========================================
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/9676/9676527.png", width=60)
    st.header("⚙️ RadarPro Ayarları")
    interval_choice = st.select_slider("Zaman Çözünürlüğü", options=['1s', '5s', '15s', '30s', '1m'], value='5s')
    y_axis_mode = st.radio("Grafik Ölçeği", ["Odaklanmış (Zoom)", "Tam Ölçek"])
    chart_type = st.radio("Ana Grafik", ["Candlestick (Mum)", "Line (Çizgi)"])
    st.divider()
    st.write("🔄 Dashboard Yenileme:")
    progress_bar = st.progress(st.session_state['refresh_counter'] / 5.0)
    st.caption(f"Kalan: {st.session_state['refresh_counter']} saniye")

# ==========================================
# 7. ANA EKRAN DÜZENİ
# ==========================================
df_raw = get_data_from_db()

if not df_raw.empty:
    available_symbols = sorted(df_raw['symbol'].unique())
    if st.session_state['selected_coin'] not in available_symbols:
        st.session_state['selected_coin'] = available_symbols[0]
    
    c_head1, c_head2 = st.columns([1, 1])
    with c_head1:
        selected_sym = st.selectbox("🪙 İZLENEN VARLIK (MARKET SELECTION)", available_symbols, index=available_symbols.index(st.session_state['selected_coin']))
        st.session_state['selected_coin'] = selected_sym
    with c_head2:
        current_time_str = datetime.now().strftime("%d %b %Y - %H:%M:%S")
        st.markdown(f"<div style='text-align: right; margin-top: 30px;'><span class='live-indicator'>● RADAR LIVE</span> <span class='live-clock'>🕒 {current_time_str}</span></div>", unsafe_allow_html=True)

    df_filtered = df_raw[df_raw['symbol'] == selected_sym]
    
    if not df_filtered.empty:
        df_ohlc = process_data_to_ohlc(df_filtered.copy(), interval=interval_choice)
        last_raw = df_filtered.iloc[-1]
        last_ohlc = df_ohlc.iloc[-1] if not df_ohlc.empty else last_raw
        
        live_price = get_live_price(selected_sym)
        display_price = live_price if live_price else last_raw['average_price']
        
        # ────────── ÜST KPI METRİKLERİ (SATIR 1) ──────────
        st.write("") 
        k1, k2, k3, k4 = st.columns(4)
        k1.metric("💰 Anlık Fiyat", f"{display_price:,.4f} $", help="Binance Vadeli İşlemlerden milisaniyelik gecikmeyle alınan son gerçekleşen işlem fiyatı.")
        
        pred_diff = last_raw['predicted_price'] - display_price
        k2.metric("🤖 AI Model Hedefi", f"{last_raw['predicted_price']:,.4f} $", f"{pred_diff:+.4f} $", help="Makine öğrenmesi algoritmamızın hareketli ortalamalar ve geçmiş verilere dayanarak öngördüğü yön.")
        
        display_cvd = last_raw.get('cvd', 0)
        cvd_color = "normal" if display_cvd > 0 else "inverse"
        k3.metric("🐋 Net CVD (Akıllı Para)", f"${display_cvd:,.0f}", delta="Alıcı Üstünlüğü" if display_cvd > 0 else "Satıcı Üstünlüğü", delta_color=cvd_color, help="Kümülatif Hacim Deltası. Piyasaya giren net parayı gösterir. Pozitif değerler balinaların alım yaptığını, negatif değerler mal boşalttığını gösterir.")

        vpin = last_raw.get('vpin_score', 0)
        vpin_status = "🚨 ZEHİRLİ YÜKSEK!" if vpin > 0.75 else "Nötr"
        k4.metric("☣️ VPIN (Akış Zehirlenmesi)", f"{vpin:.2f}", vpin_status, delta_color="inverse" if vpin > 0.75 else "normal", help="Volume-Synchronized Probability of Informed Trading. 0-1 arası değer alır. 0.75 üzerine çıkması, piyasada içeriden bilgi alan büyük oyuncuların agresifleştiğini (toksik akış) gösterir. Yüksek risk belirtisidir.")

        # ────────── ALT KPI METRİKLERİ (SATIR 2) ──────────
        st.write("")
        p1, p2, p3, p4 = st.columns(4)
        
        liq_total = last_raw.get('liq_buy_usd', 0) + last_raw.get('liq_sell_usd', 0)
        p1.metric("⚡ Likidasyon (Son Mum)", f"${liq_total:,.0f}", help="Borsada zorunlu tasfiye edilen (Margin Call yiyen) pozisyonların dolar cinsinden toplam büyüklüğü.")

        buy_wall = last_raw.get('buy_wall_usd', 0)
        sell_wall = last_raw.get('sell_wall_usd', 0)
        dom_status = "BULLISH (Alıcı Ağır)" if buy_wall > sell_wall else "BEARISH (Satıcı Ağır)"
        p2.metric("🏦 Order Book Baskısı", dom_status, help="Emir defterindeki limit alım (Bid) ve limit satım (Ask) duvarlarının toplam hacim kıyaslamasıdır.")

        fr = last_raw.get('funding_rate', 0) * 100
        p3.metric("🌊 Funding Rate (Vadeli)", f"% {fr:.4f}", help="Vadeli işlemlerde açık olan pozisyonların ödediği fonlama oranıdır. Çok yüksek pozitif olması piyasanın aşırı 'Long' yönlü şiştiğini gösterir.")
        
        rsi_val = last_raw.get('RSI', 50)
        rsi_state = "Aşırı Alım" if rsi_val > 70 else "Aşırı Satım" if rsi_val < 30 else "Normal"
        p4.metric("📊 Güç Endeksi (RSI)", f"{rsi_val:.1f}", rsi_state, delta_color="off", help="0 ile 100 arasında değer alır. 70 üstü fiyatın çok şiştiğini (düzeltme gelebilir), 30 altı çok ucuzladığını (tepki gelebilir) gösterir.")

        st.divider()

        # ==========================================
        # 8. ANA FİYAT GRAFİĞİ VE AI TAHMİNİ
        # ==========================================
        st.markdown(f"<h3>📈 Dinamik Fiyat Aksiyonu ve AI Projeksiyonu ({interval_choice})</h3>", unsafe_allow_html=True)
        if not df_ohlc.empty:
            fig = go.Figure()
            if chart_type == "Candlestick (Mum)":
                fig.add_trace(go.Candlestick(x=df_ohlc['processed_time'], open=df_ohlc['open'], high=df_ohlc['high'], low=df_ohlc['low'], close=df_ohlc['close'], name='Mum', increasing_line_color='#00ff95', decreasing_line_color='#ff3b5c'))
            else:
                fig.add_trace(go.Scatter(x=df_ohlc['processed_time'], y=df_ohlc['close'], name='Fiyat', line=dict(color='#00ff95', width=3)))
            
            fig.add_trace(go.Scatter(x=df_ohlc['processed_time'], y=df_ohlc['Bollinger_Upper'], line=dict(color='rgba(0,210,255,0.3)', width=1), showlegend=False, hoverinfo='skip'))
            fig.add_trace(go.Scatter(x=df_ohlc['processed_time'], y=df_ohlc['Bollinger_Lower'], fill='tonexty', fillcolor='rgba(0,210,255,0.05)', line=dict(color='rgba(0,210,255,0.3)', width=1), name='Bollinger Bandı'))
            fig.add_trace(go.Scatter(x=df_ohlc['processed_time'], y=df_ohlc['predicted_price'], name='AI Hedefi', line=dict(dash='dot', color='#FCD535', width=2)))

            if y_axis_mode == "Odaklanmış (Zoom)":
                fig.update_yaxes(range=[df_ohlc['low'].min() * 0.999, df_ohlc['high'].max() * 1.001])
            
            fig.update_layout(template="plotly_dark", height=450, margin=dict(l=0,r=0,t=10,b=0), plot_bgcolor='#060709', paper_bgcolor='#060709', xaxis_rangeslider_visible=False, legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1))
            st.plotly_chart(fig, use_container_width=True)
            
            # ANA GRAFİK BİLGİ KUTUSU
            st.markdown("""
            <div class='info-box'>
                <b>ℹ️ Grafiği Nasıl Okumalıyım?</b><br>
                Mavi gölgeli alan <b>Bollinger Bantlarını</b> temsil eder. Fiyat üst banda çarptığında piyasanın pahalılaştığı (Satış baskısı), alt banda çarptığında ucuzladığı (Alış baskısı) varsayılır. 
                Sarı kesik çizgiler ise <b>Makine Öğrenmesi AI</b> modelimizin yakın gelecek için tahmin ettiği hedef fiyatı çizer.
            </div>
            """, unsafe_allow_html=True)

        st.divider()

        # ==========================================
        # 9. GOD MODE GÖRSELLEŞTİRMELERİ (YENİ)
        # ==========================================
        st.markdown("<h3>🎯 WALL STREET ANALİTİKLERİ (God Mode)</h3>", unsafe_allow_html=True)
        col_liq, col_ob = st.columns(2)
        
        # ⚡ 1. LİKİDASYON ISI HARİTASI
        with col_liq:
            st.markdown("<h5>⚡ Likidasyon Avı (Tasfiyeler)</h5>", unsafe_allow_html=True)
            if 'liq_buy_usd' in df_ohlc.columns and 'liq_sell_usd' in df_ohlc.columns:
                fig_liq = go.Figure()
                fig_liq.add_trace(go.Bar(x=df_ohlc['processed_time'], y=df_ohlc['liq_buy_usd'], name='Short Patladı (Fiyat Artar)', marker_color='#00ff95'))
                fig_liq.add_trace(go.Bar(x=df_ohlc['processed_time'], y=-df_ohlc['liq_sell_usd'], name='Long Patladı (Fiyat Düşer)', marker_color='#ff3b5c'))
                fig_liq.update_layout(barmode='relative', template="plotly_dark", height=250, margin=dict(l=0,r=0,t=0,b=0), plot_bgcolor='#060709', paper_bgcolor='#060709', showlegend=False)
                st.plotly_chart(fig_liq, use_container_width=True)
                
                st.markdown("""
                <div class='info-box'>
                    <b>ℹ️ Likidasyon Haritası Nedir?</b><br>
                    Yukarı bakan yeşil barlar, yükselişe inanmayıp "Short" açanların battığı anları gösterir. Aşağı sarkan kırmızı barlar ise "Long" açanların battığını gösterir. Yoğun likidasyonlar genellikle trendin döneceğinin habercisidir.
                </div>
                """, unsafe_allow_html=True)
            else:
                st.info("Likidasyon verisi bekleniyor...")

        # 🏦 2. EMİR DEFTERİ DUVARLARI
        with col_ob:
            st.markdown("<h5>🏦 Order Book DOM (Alım/Satım Duvarları)</h5>", unsafe_allow_html=True)
            if 'buy_wall_usd' in df_ohlc.columns and 'sell_wall_usd' in df_ohlc.columns:
                fig_ob = go.Figure()
                fig_ob.add_trace(go.Scatter(x=df_ohlc['processed_time'], y=df_ohlc['buy_wall_usd'], fill='tozeroy', name='Bids (Alım Duvarı)', line=dict(color='#00ff95', width=1), fillcolor='rgba(0,255,149,0.2)'))
                fig_ob.add_trace(go.Scatter(x=df_ohlc['processed_time'], y=df_ohlc['sell_wall_usd'], fill='tozeroy', name='Asks (Satış Duvarı)', line=dict(color='#ff3b5c', width=1), fillcolor='rgba(255,59,92,0.2)'))
                fig_ob.update_layout(template="plotly_dark", height=250, margin=dict(l=0,r=0,t=0,b=0), plot_bgcolor='#060709', paper_bgcolor='#060709', showlegend=False)
                st.plotly_chart(fig_ob, use_container_width=True)
                
                st.markdown("""
                <div class='info-box'>
                    <b>ℹ️ DOM (Depth of Market) Duvarları:</b><br>
                    Yeşil alan, tahtadaki bekleyen alış (destek) emirlerinin gücünü, Kırmızı alan ise satış (direnç) emirlerinin gücünü gösterir. Kırmızı alan yeşili eziyorsa, yukarı yönlü hareketler zorlaşır. (Spoofing/Sahte emirler de buradan tespit edilir).
                </div>
                """, unsafe_allow_html=True)
            else:
                st.info("Emir defteri verisi bekleniyor...")

        st.write("")
        col_vpin, col_cvd = st.columns(2)

        # ☣️ 3. VPIN ZEHİRLENME SKORU
        with col_vpin:
            st.markdown("<h5>☣️ VPIN (Akış Zehirlenmesi)</h5>", unsafe_allow_html=True)
            if 'vpin_score' in df_ohlc.columns:
                fig_vpin = go.Figure()
                fig_vpin.add_trace(go.Scatter(x=df_ohlc['processed_time'], y=df_ohlc['vpin_score'], name='VPIN Skoru', line=dict(color='#9c27b0', width=2), fill='tozeroy', fillcolor='rgba(156,39,176,0.1)'))
                fig_vpin.add_hline(y=0.75, line_dash="dash", line_color="#ff3b5c", annotation_text="Kritik Zehirlenme Seviyesi", annotation_position="top left")
                fig_vpin.update_layout(template="plotly_dark", height=200, margin=dict(l=0,r=0,t=0,b=0), plot_bgcolor='#060709', paper_bgcolor='#060709', yaxis=dict(range=[0, 1]))
                st.plotly_chart(fig_vpin, use_container_width=True)
                
                st.markdown("""
                <div class='info-box'>
                    <b>ℹ️ VPIN Nasıl Yorumlanır?</b><br>
                    Sıradan traderların göremediği Wall Street düzeyinde bir risk metriğidir. Çizgi <b>0.75</b> seviyesini aştığında, piyasaya aşırı derecede agresif veya "içeriden bilgi alan" bir hacim girdiğini gösterir. Bu anlarda yüksek volatilite (sert mumlar) yaşanması kaçınılmazdır.
                </div>
                """, unsafe_allow_html=True)

        # 🐋 4. CVD (SMART MONEY)
        with col_cvd:
            st.markdown("<h5>🐋 Net CVD (Akıllı Para Akışı)</h5>", unsafe_allow_html=True)
            if 'cvd' in df_ohlc.columns:
                fig_cvd = go.Figure()
                cvd_colors = ['#00ff95' if val > 0 else '#ff3b5c' for val in df_ohlc['cvd']]
                fig_cvd.add_trace(go.Bar(x=df_ohlc['processed_time'], y=df_ohlc['cvd'], marker_color=cvd_colors))
                fig_cvd.update_layout(template="plotly_dark", height=200, margin=dict(l=0,r=0,t=0,b=0), plot_bgcolor='#060709', paper_bgcolor='#060709')
                st.plotly_chart(fig_cvd, use_container_width=True)
                
                st.markdown("""
                <div class='info-box'>
                    <b>ℹ️ Kümülatif Delta Hacmi (CVD):</b><br>
                    Gerçekleşen net para giriş çıkışıdır. Fiyat yukarı giderken buradaki barlar kırmızıya (negatif) dönüyorsa, balinalar yükselişi fırsat bilip gizlice mal satıyor demektir. Fiyat düşerken barlar yeşilse, dipten mal toplanıyor demektir.
                </div>
                """, unsafe_allow_html=True)

        st.divider()

        # ==========================================
        # 10. KLASİK ALT GRAFİKLER (MACD & RSI)
        # ==========================================
        if not df_ohlc.empty:
            col_left, col_right = st.columns(2)
            with col_left:
                st.markdown("<h5>📉 Momentum (MACD)</h5>", unsafe_allow_html=True)
                fig_macd = go.Figure()
                macd_hist = df_ohlc['MACD'] - df_ohlc['Signal_Line']
                fig_macd.add_trace(go.Bar(x=df_ohlc['processed_time'], y=macd_hist, marker_color=['#00ff95' if x > 0 else '#ff3b5c' for x in macd_hist]))
                fig_macd.add_trace(go.Scatter(x=df_ohlc['processed_time'], y=df_ohlc['MACD'], line=dict(color='#2962FF', width=1.5)))
                fig_macd.update_layout(template="plotly_dark", height=180, margin=dict(l=0,r=0,t=0,b=0), plot_bgcolor='#060709', paper_bgcolor='#060709', showlegend=False)
                st.plotly_chart(fig_macd, use_container_width=True)
                st.markdown("<div class='info-box'><b>ℹ️ MACD Trendi:</b> Kısa vadeli hareketli ortalamanın, uzun vadeli ortalamadan farkını ölçer. Barların yeşile dönmesi yukarı ivmenin güçlendiğini gösterir.</div>", unsafe_allow_html=True)

            with col_right:
                st.markdown("<h5>📈 Güç Endeksi (RSI)</h5>", unsafe_allow_html=True)
                fig_rsi = go.Figure()
                fig_rsi.add_hrect(y0=70, y1=100, fillcolor='#ff3b5c', opacity=0.1, line_width=0)
                fig_rsi.add_hrect(y0=0, y1=30, fillcolor='#00ff95', opacity=0.1, line_width=0)
                fig_rsi.add_trace(go.Scatter(x=df_ohlc['processed_time'], y=df_ohlc['RSI'], line=dict(color='#FCD535', width=2)))
                fig_rsi.update_layout(template="plotly_dark", height=180, margin=dict(l=0,r=0,t=0,b=0), plot_bgcolor='#060709', paper_bgcolor='#060709', yaxis=dict(range=[0, 100]))
                st.plotly_chart(fig_rsi, use_container_width=True)
                st.markdown("<div class='info-box'><b>ℹ️ RSI Değeri:</b> Fiyatın ne kadar hızlı ve sert hareket ettiğini gösterir. Kırmızı alan (70 üstü) fiyatta şişkinlik (Aşırı Alım), Yeşil alan (30 altı) piyasanın ucuzladığı (Aşırı Satım) bölgeleridir.</div>", unsafe_allow_html=True)

        # ==========================================
        # 11. POSTGRESQL HAM VERİ TABLOSU
        # ==========================================
        st.divider()
        with st.expander("📋 Ham Veri Logları (Terminal Çıktısı)"):
            display_cols = ['processed_time', 'symbol', 'average_price', 'predicted_price', 'cvd', 'vpin_score', 'imbalance_ratio', 'liq_buy_usd', 'liq_sell_usd']
            available_cols = [c for c in display_cols if c in df_filtered.columns]
            
            st.dataframe(
                df_filtered[available_cols].sort_values('processed_time', ascending=False).head(15).style.format({
                    'average_price': '{:.4f}', 'predicted_price': '{:.4f}', 'cvd': '${:,.0f}', 'vpin_score': '{:.3f}', 'imbalance_ratio': '{:.2f}', 'liq_buy_usd': '${:,.0f}', 'liq_sell_usd': '${:,.0f}'
                }), 
                use_container_width=True, hide_index=True
            )

# ==========================================
# 12. SAYAÇ YÖNETİMİ VE RERUN (LOOP)
# ==========================================
time.sleep(1)
st.session_state['refresh_counter'] -= 1

if st.session_state['refresh_counter'] <= 0:
    st.session_state['refresh_counter'] = 5 
    
st.rerun()