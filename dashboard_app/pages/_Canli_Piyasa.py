import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import time
import json
import os
import requests
from datetime import datetime
from kafka import KafkaConsumer
from sqlalchemy import create_engine
import redis
from collections import deque

# ==========================================
# 0. SAYFA KONFİGÜRASYONU
# ==========================================
st.set_page_config(page_title="Enterprise Trading Terminal | VIP", layout="wide", page_icon="📈")

# ==========================================
# 1. BAĞLANTI VE ALTYAPI AYARLARI
# ==========================================
PG_USER = "admin_lakehouse"
PG_PASS = "SuperSecret_DB_Password_2026"
PG_HOST = os.getenv("POSTGRES_HOST", "postgres")
PG_DB = "market_db"
DB_URL = f"postgresql://{PG_USER}:{PG_PASS}@{PG_HOST}:5432/{PG_DB}"

KAFKA_SERVER = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "kafka:9092")
REDIS_HOST = os.getenv("REDIS_HOST", "redis")
API_BASE_URL = os.getenv("API_BASE_URL", "http://api-gateway:8000") 
API_KEY = "sk_live_demo"

try:
    redis_client = redis.Redis(host=REDIS_HOST, port=6379, db=0, decode_responses=True)
except:
    redis_client = None

# Kafka Tape Hafızası
if 'kafka_tape' not in st.session_state:
    st.session_state['kafka_tape'] = deque(maxlen=50)

# ==========================================
# 2. KURUMSAL UI/UX TASARIMI (CSS)
# ==========================================
st.markdown("""
<style>
    .stApp { background-color: #0b0e11; color: #eaecef; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; }
    .block-container { padding-top: 2rem; max-width: 98%; }
    [data-testid="stMetricValue"] { font-size: 24px; font-weight: bold; color: #FCD535 !important; }
    div[data-testid="metric-container"] { background-color: #1e2329; padding: 15px; border-radius: 6px; border: 1px solid #2b3139; }
    .analysis-box { background-color: #161a1e; padding: 15px; border-radius: 6px; border-left: 5px solid #00d2ff; font-size: 14px; color: #d1d4dc; margin-top: 10px; margin-bottom: 20px; line-height: 1.6; }
    
    .radar-box { background-color: #161a1e; padding: 15px; border-radius: 6px; border: 1px solid #2b3139; margin-bottom: 15px; }
    .radar-title { font-size: 16px; font-weight: 900; margin-bottom: 10px; text-transform: uppercase; letter-spacing: 1px; }
    
    .highlight-up { color: #0ecb81; font-weight: bold; }
    .highlight-down { color: #f6465d; font-weight: bold; }
    .live-indicator { color: #00e676; font-weight: bold; animation: blinker 1.5s linear infinite; font-size: 18px; margin-right: 10px;}
    .live-clock { color: #848E9C; font-size: 20px; font-weight: bold; font-family: 'Courier New', Courier, monospace; background-color: #1e2329; padding: 5px 15px; border-radius: 4px; border: 1px solid #2b3139;}
    @keyframes blinker { 50% { opacity: 0; } }
    @keyframes pulse-red { 100% { box-shadow: 0 0 20px rgba(255, 59, 92, 0.4); } }
    div[data-baseweb="select"] { font-size: 18px; font-weight: bold;}
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
    premium_cols = [c for c in ['trade_side', 'is_buyer_maker', 'cvd'] if c in df.columns]
    indicators = df[base_cols + premium_cols].resample(interval).last()
    
    if 'volume_usd' in df.columns: ohlc['volume_usd_sum'] = df['volume_usd'].resample(interval).sum()
    return pd.concat([ohlc, indicators], axis=1).dropna().reset_index()

# ==========================================
# 4. DATA FETCH (DB, REDIS, API, KAFKA)
# ==========================================
@st.cache_data(ttl=5, show_spinner=False)
def get_data_from_db():
    try:
        engine = create_engine(DB_URL)
        df = pd.read_sql("SELECT * FROM market_data ORDER BY processed_time DESC LIMIT 1000", engine)
        if not df.empty:
            df = df.sort_values('processed_time')
            df = df.groupby('symbol').apply(calculate_technical_indicators).reset_index(drop=True)
        return df
    except: return pd.DataFrame()

# 🔴 HATA BURADAYDI: get_god_mode_redis olarak adlandırıldı
def get_god_mode_redis(symbol):
    if redis_client:
        try:
            d = redis_client.get(f"GOD_MODE_{symbol}")
            if d: return json.loads(d)
        except: pass
    return {}

def api_request(endpoint):
    try:
        r = requests.get(f"{API_BASE_URL}{endpoint}", headers={"X-API-Key": API_KEY}, timeout=2)
        if r.status_code == 200: return r.json()
    except: pass
    return None

if 'kafka_consumer' not in st.session_state:
    try:
        st.session_state['kafka_consumer'] = KafkaConsumer(
            'market_data', bootstrap_servers=KAFKA_SERVER, auto_offset_reset='latest',
            enable_auto_commit=False, value_deserializer=lambda x: json.loads(x.decode('utf-8')),
            consumer_timeout_ms=50
        )
    except: st.session_state['kafka_consumer'] = None

def process_kafka_tape(symbol):
    live_p = None
    if st.session_state['kafka_consumer']:
        try:
            msg_pack = st.session_state['kafka_consumer'].poll(timeout_ms=50)
            for tp, messages in msg_pack.items():
                for msg in messages:
                    d = msg.value
                    if d.get('symbol') == symbol:
                        live_p = float(d.get('price', 0))
                        vol = float(d.get('volume_usd', 0))
                        l_buy = float(d.get('liq_buy_usd', 0))
                        l_sell = float(d.get('liq_sell_usd', 0))
                        if vol > 5000 or l_buy > 0 or l_sell > 0:
                            d['ts_str'] = datetime.now().strftime("%H:%M:%S.%f")[:-3]
                            st.session_state['kafka_tape'].appendleft(d)
        except: pass
    return live_p

# ==========================================
# 5. UI STATE VE YAN PANEL (SIDEBAR)
# ==========================================
if 'selected_coin' not in st.session_state: st.session_state['selected_coin'] = "BTCUSDT"
if 'refresh_counter' not in st.session_state: st.session_state['refresh_counter'] = 5

with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/9676/9676527.png", width=60)
    st.header("⚙️ Terminal Ayarları")
    interval_choice = st.select_slider("Mum Zaman Aralığı", options=['1s', '5s', '15s', '30s', '1m'], value='5s')
    y_axis_mode = st.radio("Y-Eksen Fiyat Ölçeği", ["Odaklanmış (Zoom)", "Tam Ölçek"])
    chart_type = st.radio("Grafik Tipi", ["Candlestick (Mum)", "Line (Çizgi)"])
    
    st.divider()
    st.markdown("### 📰 CANLI HABER AKIŞI (API)")
    news_res = api_request("/api/v1/news")
    if news_res and news_res.get('status') == 'success' and news_res.get('data'):
        for n in news_res['data'][:4]:
            st.markdown(f"<div style='background:#1e2329; padding:8px; border-left:3px solid #2962FF; margin-bottom:6px; border-radius:4px; font-size:11px;'><a href='{n['link']}' target='_blank' style='color:#d1d4dc; text-decoration:none;'>{n['title']}</a></div>", unsafe_allow_html=True)
    else:
        st.caption("Haber taranıyor...")

    st.divider()
    st.write("🔄 Yapay Zeka Güncellemesi:")
    st.progress(st.session_state['refresh_counter'] / 5.0)

# ==========================================
# 6. ANA EKRAN DÜZENİ 
# ==========================================
df_raw = get_data_from_db()

if not df_raw.empty:
    available_symbols = sorted(df_raw['symbol'].unique())
    if st.session_state['selected_coin'] not in available_symbols:
        st.session_state['selected_coin'] = available_symbols[0]
    
    c_head1, c_head2 = st.columns([1, 1])
    with c_head1:
        selected_sym = st.selectbox("🪙 İZLENEN VARLIK", available_symbols, index=available_symbols.index(st.session_state['selected_coin']))
        st.session_state['selected_coin'] = selected_sym
    with c_head2:
        current_time_str = datetime.now().strftime("%d %b %Y - %H:%M:%S")
        st.markdown(f"<div style='text-align: right; margin-top: 30px;'><span class='live-indicator'>● KAFKA LİVE</span> <span class='live-clock'>🕒 {current_time_str}</span></div>", unsafe_allow_html=True)

    df_filtered = df_raw[df_raw['symbol'] == selected_sym]
    live_price = process_kafka_tape(selected_sym)
    
    # 🔴 DÜZELTİLEN KISIM
    god_data = get_god_mode_redis(selected_sym)
    
    if not df_filtered.empty:
        df_ohlc = process_data_to_ohlc(df_filtered.copy(), interval=interval_choice)
        last_raw = df_filtered.iloc[-1]
        last_ohlc = df_ohlc.iloc[-1] if not df_ohlc.empty else last_raw
        
        display_price = live_price if live_price else god_data.get('p', last_raw['average_price'])
        pred_price = god_data.get('predicted_price', last_raw['predicted_price'])
        cvd_val = god_data.get('cvd', last_raw.get('cvd', 0))
        vpin_val = god_data.get('vpin', last_raw.get('vpin_score', 0))
        
        # --- SATIR 1: TEMEL METRİKLER ---
        st.write("") 
        k1, k2, k3, k4 = st.columns(4)
        k1.metric("💰 Anlık Fiyat (Kafka)", f"{display_price:,.5f} $")
        k2.metric("🤖 Yapay Zeka Hedefi", f"{pred_price:,.5f} $", f"{pred_price - display_price:+.5f} $", delta_color="normal" if pred_price > display_price else "inverse")
        k3.metric("🎯 Sistem Sinyali", "AL 🟢" if pred_price > display_price else "SAT 🔴")
        rsi_val = last_raw['RSI']
        k4.metric("📊 RSI (14)", f"{rsi_val:.1f}", "Aşırı Alım" if rsi_val > 70 else "Aşırı Satım" if rsi_val < 30 else "Nötr")

        # --- SATIR 2: İSTİHBARAT METRİKLERİ ---
        st.write("")
        p1, p2, p3, p4 = st.columns(4)
        p1.metric("🌊 Son İşlem Hacmi", f"${last_raw.get('volume_usd', 0):,.0f}")
        side_val = last_raw.get('trade_side', 'N/A')
        p2.metric("⚖️ Son İşlem Yönü", "🟢 ALICI" if side_val == 'BUY' else "🔴 SATICI" if side_val == 'SELL' else "⚪ NÖTR")
        p3.metric("☣️ VPIN Flow Risk", f"{vpin_val:.2f}", "🚨 TOKSİK AKIŞ" if vpin_val > 0.75 else "🟢 Temiz", delta_color="inverse" if vpin_val > 0.75 else "normal")
        p4.metric("🐋 Akıllı Para (CVD)", f"${cvd_val:,.0f}", delta="Alıcı Baskısı" if cvd_val > 0 else "Satıcı Baskısı", delta_color="normal" if cvd_val > 0 else "inverse")

        st.divider()

        # ==========================================
        # 🚀 İSTİHBARAT RADARLARI (YAN YANA 4 KUTU)
        # ==========================================
        c_liq, c_anom, c_arb, c_dom = st.columns(4)
        
        # 1. LİKİDASYON MIKNATISI
        with c_liq:
            st.markdown("<div class='radar-box' style='border-color:#FCD535;'><div class='radar-title' style='color:#FCD535;'>🧲 Likidasyon Mıknatısı</div>", unsafe_allow_html=True)
            st.write(f"🔴 25x Short: **${god_data.get('liq_up_25x', display_price*1.04):,.0f}**")
            st.write(f"🔴 50x Short: **${god_data.get('liq_up_50x', display_price*1.02):,.0f}**")
            st.write(f"🟢 50x Long: **${god_data.get('liq_dn_50x', display_price*0.98):,.0f}**")
            st.write(f"🟢 25x Long: **${god_data.get('liq_dn_25x', display_price*0.96):,.0f}**")
            st.markdown("</div>", unsafe_allow_html=True)

        # 2. Z-SCORE ANOMALİ RADARI
        with c_anom:
            a_wash = god_data.get('anomaly_wash', False)
            a_spoof = god_data.get('anomaly_spoof', False)
            a_zscore = god_data.get('anomaly_zscore', 0.0)
            if a_wash or a_spoof:
                r = [x for x, y in [("Wash Trading", a_wash), ("Spoofing", a_spoof)] if y]
                st.markdown(f"<div class='radar-box' style='border-color:#ff3b5c; animation: pulse-red 1s infinite alternate;'><div class='radar-title' style='color:#ff3b5c;'>🛡️ AI Anomali Radarı</div><span style='color:#ff3b5c; font-size:18px; font-weight:bold;'>⚠️ MANİPÜLASYON</span><br>Z-Score: <b>{a_zscore:.2f}</b><br>Neden: {' & '.join(r)}</div>", unsafe_allow_html=True)
            else:
                st.markdown(f"<div class='radar-box' style='border-color:#00e676;'><div class='radar-title' style='color:#00e676;'>🛡️ AI Anomali Radarı</div><span style='color:#00e676; font-size:18px; font-weight:bold;'>✅ TEMİZ PİYASA</span><br>Z-Score: <b>{a_zscore:.2f}</b><br>Organik Fiyatlama.</div>", unsafe_allow_html=True)

        # 3. 8 BORSA ARBİTRAJI VE MAX PAIN
        with c_arb:
            arb_res = api_request(f"/api/v1/arbitrage/{selected_sym}")
            m_pain = god_data.get('max_pain', 'Hesaplanıyor')
            if arb_res and arb_res.get('status') == 'success':
                d = arb_res['data']
                if d['spread_pct'] > 0.05:
                    st.markdown(f"<div class='radar-box' style='border-color:#2962FF;'><div class='radar-title' style='color:#2962FF;'>⚖️ Arbitraj & Opsiyon</div><span style='color:#00e676; font-weight:bold;'>🚨 FIRSAT: {d['max_exchange']} SAT ➡️ {d['min_exchange']} AL</span><br>Makas: <b>${d['spread_usd']:.2f} (%{d['spread_pct']:.2f})</b><br>🎯 Max Pain: <b style='color:#9c27b0;'>${m_pain}</b></div>", unsafe_allow_html=True)
                else:
                    st.markdown(f"<div class='radar-box' style='border-color:#2962FF;'><div class='radar-title' style='color:#2962FF;'>⚖️ Arbitraj & Opsiyon</div><span style='color:#64748b;'>DENGELİ (Makas Dar)</span><br>Makas: <b>${d['spread_usd']:.2f} (%{d['spread_pct']:.2f})</b><br>🎯 Max Pain: <b style='color:#9c27b0;'>${m_pain}</b></div>", unsafe_allow_html=True)
            else:
                st.markdown("<div class='radar-box' style='border-color:#2962FF;'><div class='radar-title' style='color:#2962FF;'>⚖️ Arbitraj & Opsiyon</div>Taranıyor...</div>", unsafe_allow_html=True)

        # 4. CANLI EMİR DEFTERİ (DOM)
        with c_dom:
            b_wall = god_data.get('buy_wall_usd', 0)
            s_wall = god_data.get('sell_wall_usd', 0)
            t_wall = b_wall + s_wall if (b_wall + s_wall) > 0 else 1
            st.markdown("<div class='radar-box' style='border-color:#d1d4dc;'><div class='radar-title' style='color:#d1d4dc;'>🏦 Canlı Emir Defteri (DOM)</div>", unsafe_allow_html=True)
            st.write(f"🟢 Bids: **${b_wall:,.0f}**")
            st.progress(min(b_wall / t_wall, 1.0))
            st.write(f"🔴 Asks: **${s_wall:,.0f}**")
            st.progress(min(s_wall / t_wall, 1.0))
            st.markdown("</div>", unsafe_allow_html=True)

        # ==========================================
        # 8. ANA FİYAT GRAFİĞİ (ESKİ KOD + REDIS ÇİZGİLERİ)
        # ==========================================
        st.markdown(f"<h3 style='color: #eaecef;'>Fiyat, Yapay Zeka ve Bollinger Bantları ({interval_choice})</h3>", unsafe_allow_html=True)
        if not df_ohlc.empty:
            fig = go.Figure()
            if chart_type == "Candlestick (Mum)":
                fig.add_trace(go.Candlestick(x=df_ohlc['processed_time'], open=df_ohlc['open'], high=df_ohlc['high'], low=df_ohlc['low'], close=df_ohlc['close'], name='Mum', increasing_line_color='#0ecb81', decreasing_line_color='#f6465d'))
            else:
                fig.add_trace(go.Scatter(x=df_ohlc['processed_time'], y=df_ohlc['close'], name='Fiyat', line=dict(color='#0ecb81', width=3)))
            
            fig.add_trace(go.Scatter(x=df_ohlc['processed_time'], y=df_ohlc['Bollinger_Upper'], line=dict(width=0), showlegend=False, hoverinfo='skip'))
            fig.add_trace(go.Scatter(x=df_ohlc['processed_time'], y=df_ohlc['Bollinger_Lower'], fill='tonexty', fillcolor='rgba(132, 142, 156, 0.05)', line=dict(width=0), name='Bollinger Bandı'))
            fig.add_trace(go.Scatter(x=df_ohlc['processed_time'], y=df_ohlc['predicted_price'], name='AI Tahmini', line=dict(dash='dot', color='#FCD535', width=2)))

            # Likidasyon Çizgileri (Redis Exact)
            fig.add_hline(y=god_data.get('liq_up_25x', display_price*1.04), line_dash="solid", line_color="#ff3b5c", annotation_text="25x Short Liq", annotation_position="top right", opacity=0.6)
            fig.add_hline(y=god_data.get('liq_dn_25x', display_price*0.96), line_dash="solid", line_color="#00e676", annotation_text="25x Long Liq", annotation_position="bottom right", opacity=0.6)
            fig.add_hline(y=god_data.get('liq_up_50x', display_price*1.02), line_dash="dash", line_color="rgba(255,59,92,0.8)", annotation_text="50x Short Liq", annotation_position="top right")
            fig.add_hline(y=god_data.get('liq_dn_50x', display_price*0.98), line_dash="dash", line_color="rgba(14,203,129,0.8)", annotation_text="50x Long Liq", annotation_position="bottom right")

            # Max Pain Çizgisi
            m_pain_line = god_data.get('max_pain')
            if m_pain_line: fig.add_hline(y=m_pain_line, line_dash="solid", line_color="#9c27b0", line_width=3, annotation_text="🎯 MAX PAIN", annotation_font_color="#9c27b0")

            if y_axis_mode == "Odaklanmış (Zoom)":
                fig.update_yaxes(range=[df_ohlc['low'].min() * 0.95, df_ohlc['high'].max() * 1.05])
            
            fig.update_layout(template="plotly_dark", height=500, margin=dict(l=0,r=0,t=10,b=0), plot_bgcolor='#0b0e11', paper_bgcolor='#0b0e11', xaxis_rangeslider_visible=False)
            st.plotly_chart(fig, use_container_width=True)

        # 💡 ANALİZ METNİ
        dist_up = last_ohlc['Bollinger_Upper'] - last_ohlc['close']
        dist_down = last_ohlc['close'] - last_ohlc['Bollinger_Lower']
        p_status = "Bollinger üst bandına (Direnç) yaklaşıyor, satış baskısı artabilir." if dist_up < dist_down else "Bollinger alt bandına (Destek) yakın, tepki alımı gelebilir."
        t_status = f"Yapay zeka tahmini mevcut fiyatın <span class='highlight-{'up' if pred_price > display_price else 'down'}'>{'üzerinde (Yükseliş Beklentisi)' if pred_price > display_price else 'altında (Düşüş Beklentisi)'}</span>."
        st.markdown(f"<div class='analysis-box' style='border-left-color: #fcd535;'><b>💡 Dinamik Fiyat ve Trend Analizi:</b><br>• {p_status}<br>• {t_status}</div>", unsafe_allow_html=True)

        # ==========================================
        # 9. ALT GRAFİKLER (CVD, VOL, MACD, RSI)
        # ==========================================
        st.divider()
        if 'cvd' in df_ohlc.columns and 'volume_usd_sum' in df_ohlc.columns:
            st.markdown("<h3 style='color: #00d2ff;'>🐋 Smart Money & Hacim (Order Flow)</h3>", unsafe_allow_html=True)
            col_cvd, col_vol = st.columns(2)
            with col_cvd:
                st.markdown("<h5 style='color: #848E9C;'>Kümülatif Hacim Deltası (CVD)</h5>", unsafe_allow_html=True)
                fig_cvd = go.Figure()
                cvd_colors = ['#0ecb81' if val > 0 else '#f6465d' for val in df_ohlc['cvd']]
                fig_cvd.add_trace(go.Bar(x=df_ohlc['processed_time'], y=df_ohlc['cvd'], marker_color=cvd_colors))
                fig_cvd.update_layout(template="plotly_dark", height=200, margin=dict(l=0,r=0,t=0,b=0), plot_bgcolor='#0b0e11', paper_bgcolor='#0b0e11')
                st.plotly_chart(fig_cvd, use_container_width=True)
            with col_vol:
                st.markdown("<h5 style='color: #848E9C;'>Toplam İşlem Hacmi (Volume)</h5>", unsafe_allow_html=True)
                fig_vol = go.Figure()
                vol_colors = ['#0ecb81' if row['close'] >= row['open'] else '#f6465d' for index, row in df_ohlc.iterrows()]
                fig_vol.add_trace(go.Bar(x=df_ohlc['processed_time'], y=df_ohlc['volume_usd_sum'], marker_color=vol_colors))
                fig_vol.update_layout(template="plotly_dark", height=200, margin=dict(l=0,r=0,t=0,b=0), plot_bgcolor='#0b0e11', paper_bgcolor='#0b0e11')
                st.plotly_chart(fig_vol, use_container_width=True)

        st.write("")
        col_left, col_right = st.columns(2)
        with col_left:
            st.markdown("<h5 style='color: #848E9C;'>Momentum (MACD)</h5>", unsafe_allow_html=True)
            fig_macd = go.Figure()
            macd_hist = df_ohlc['MACD'] - df_ohlc['Signal_Line']
            fig_macd.add_trace(go.Bar(x=df_ohlc['processed_time'], y=macd_hist, marker_color=['#0ecb81' if x > 0 else '#f6465d' for x in macd_hist]))
            fig_macd.add_trace(go.Scatter(x=df_ohlc['processed_time'], y=df_ohlc['MACD'], line=dict(color='#3498db', width=1.5)))
            fig_macd.update_layout(template="plotly_dark", height=200, margin=dict(l=0,r=0,t=0,b=0), plot_bgcolor='#0b0e11', paper_bgcolor='#0b0e11', showlegend=False)
            st.plotly_chart(fig_macd, use_container_width=True)

        with col_right:
            st.markdown("<h5 style='color: #848E9C;'>Güç Endeksi (RSI)</h5>", unsafe_allow_html=True)
            fig_rsi = go.Figure()
            fig_rsi.add_hrect(y0=70, y1=100, fillcolor='#f6465d', opacity=0.1, line_width=0)
            fig_rsi.add_hrect(y0=0, y1=30, fillcolor='#0ecb81', opacity=0.1, line_width=0)
            fig_rsi.add_trace(go.Scatter(x=df_ohlc['processed_time'], y=df_ohlc['RSI'], line=dict(color='#FF6692', width=2)))
            fig_rsi.update_layout(template="plotly_dark", height=200, margin=dict(l=0,r=0,t=0,b=0), plot_bgcolor='#0b0e11', paper_bgcolor='#0b0e11', yaxis=dict(range=[0, 100]))
            st.plotly_chart(fig_rsi, use_container_width=True)

        # ==========================================
        # 10. KAFKA TAPE (CANLI AKIŞ)
        # ==========================================
        st.divider()
        st.markdown("### 🔥 Canlı İşlem ve Likidasyon Akışı (Kafka Tape)")
        if st.session_state['kafka_tape']:
            tape_df = pd.DataFrame(list(st.session_state['kafka_tape']))
            def style_tape(row):
                if pd.notna(row.get('liq_buy_usd')) and float(row['liq_buy_usd']) > 0: return ['background-color: rgba(0,230,118,0.2); color: #00e676; font-weight:bold'] * len(row)
                if pd.notna(row.get('liq_sell_usd')) and float(row['liq_sell_usd']) > 0: return ['background-color: rgba(255,59,92,0.2); color: #ff3b5c; font-weight:bold'] * len(row)
                if row.get('trade_side') == 'BUY': return ['color: #00e676'] * len(row)
                if row.get('trade_side') == 'SELL': return ['color: #ff3b5c'] * len(row)
                return [''] * len(row)
                
            cols_to_show = ['ts_str', 'symbol', 'trade_side', 'price', 'volume_usd', 'liq_buy_usd', 'liq_sell_usd']
            valid_cols = [c for c in cols_to_show if c in tape_df.columns]
            st.dataframe(tape_df[valid_cols].style.apply(style_tape, axis=1), use_container_width=True, hide_index=True)
        else:
            st.info("Kafka'dan balina işlemi veya likidasyon bekleniyor... (Hacim > $5000)")

        # ==========================================
        # 11. POSTGRESQL HAM VERİ TABLOSU
        # ==========================================
        st.divider()
        with st.expander("📋 Veritabanı Kayıtları (Son 10 İşlem)"):
            display_cols = ['processed_time', 'symbol', 'average_price', 'predicted_price', 'cvd', 'trade_side', 'volume_usd', 'is_buyer_maker']
            available_cols = [c for c in display_cols if c in df_filtered.columns]
            
            st.dataframe(
                df_filtered[available_cols].sort_values('processed_time', ascending=False).head(10).style.format({
                    'average_price': '{:.5f}', 'predicted_price': '{:.5f}', 'cvd': '${:,.2f}', 'volume_usd': '${:,.2f}'
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