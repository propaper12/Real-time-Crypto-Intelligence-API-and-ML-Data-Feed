import streamlit as st
import requests
import pandas as pd
import time
import plotly.express as px


st.set_page_config(page_title="RadarPro | Veri Terminali", layout="wide", page_icon="📡")

API_BASE_URL = "http://api-gateway:8000/api/v1"
# Streamlit Docker dışındaysa http://localhost:8000/api/v1 kullanmalısın, Docker içindeyse api-gateway kalsın.
# Eğer API'ye bağlanmazsa yukarıyı http://localhost:8000/api/v1 olarak değiştir!

COINS = [
    "BTCUSDT", "ETHUSDT", "BNBUSDT", "SOLUSDT", "XRPUSDT", "ADAUSDT", "AVAXUSDT", 
    "DOGEUSDT", "DOTUSDT", "MATICUSDT", "LINKUSDT", "UNIUSDT", "LTCUSDT"
]

if "api_key" not in st.session_state: st.session_state["api_key"] = None
if "tier" not in st.session_state: st.session_state["tier"] = None
if "email" not in st.session_state: st.session_state["email"] = None

# ==============================================================================
# 🔐 GİRİŞ EKRANI
# ==============================================================================
def auth_screen():
    st.markdown("<h1 style='text-align: center;'>Radar<span style='color:#2962FF'>Pro</span> DaaS Terminal</h1>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1,2,1])
    with col2:
        tab_login, tab_register = st.tabs(["🔐 Giriş Yap", "📝 Kayıt Ol"])
        
        with tab_login:
            log_email = st.text_input("E-posta Adresi", placeholder="ornek@radar.com", key="login_email")
            log_pass = st.text_input("Şifre", type="password", key="login_pass")
            if st.button("Sisteme Gir", use_container_width=True, key="login_btn"):
                try:
                    res = requests.post(f"{API_BASE_URL}/auth/login", json={"email": log_email, "password": log_pass})
                    if res.status_code == 200 and res.json().get("status") == "success":
                        data = res.json()["data"]
                        st.session_state.update({"api_key": data["api_key"], "tier": data["tier"], "email": data["email"]})
                        st.rerun()
                    else: st.error("Giriş Başarısız. Lütfen bilgilerinizi kontrol edin.")
                except Exception as e:
                    st.error("Bağlantı Hatası. API çalışıyor mu?")
                    
        with tab_register:
            reg_username = st.text_input("Kullanıcı Adı", placeholder="kullanici", key="register_username")
            reg_email = st.text_input("E-posta Adresi", placeholder="ornek@radarpro.io", key="register_email")
            reg_pass = st.text_input("Şifre", type="password", key="register_pass")
            if st.button("Kayıt Ol ve Giriş Yap", use_container_width=True, key="register_btn"):
                if not reg_username or not reg_email or not reg_pass:
                    st.error("Lütfen tüm alanları doldurun.")
                else:
                    try:
                        res = requests.post(f"{API_BASE_URL}/auth/register", json={
                            "username": reg_username,
                            "email": reg_email,
                            "password": reg_pass
                        })
                        if res.status_code == 200:
                            payload = res.json()
                            if payload.get("status") == "success":
                                api_key = payload.get("api_key")
                                st.session_state.update({"api_key": api_key, "tier": "VIP", "email": reg_email})
                                st.success("🎉 Kayıt Başarılı ve VIP Lisansınız Tanımlandı!")
                                time.sleep(1.5)
                                st.rerun()
                            else:
                                st.error(f"Kayıt Başarısız: {payload.get('message')}")
                        else:
                            st.error(f"Hata Kodu: {res.status_code}")
                    except Exception as e:
                        st.error(f"Bağlantı Hatası: {e}")

# ==============================================================================
# 📊 ANA TERMİNAL
# ==============================================================================
@st.fragment(run_every=2)
def render_live_data(symbol, api_key):
    headers = {"X-API-Key": api_key}
    try:
        res = requests.get(f"{API_BASE_URL}/market/{symbol}", headers=headers)
        if res.status_code == 200:
            payload = res.json()
            veri = payload["data"]
            tier_info = payload["tier"]
            
            if tier_info == "FREE": 
                st.error(f"⏳ **FREE Paket:** Veriler 1 dakika gecikmelidir. Ana veritabanına erişim kısıtlıdır.")
                
                st.markdown("### 📊 1 Dk Gecikmeli Fiyat & Günlük Özet")
                c1, c2, c3, c4 = st.columns(4)
                c1.metric("Gecikmeli Fiyat", f"${veri.get('delayed_price') or 0:,.2f}")
                c2.metric("24s Ortalama", f"${veri.get('avg_p') or 0:,.2f}")
                c3.metric("24s Zirve", f"${veri.get('max_p') or 0:,.2f}")
                c4.metric("24s Dip", f"${veri.get('min_p') or 0:,.2f}")
                st.caption(f"Veritabanı Zaman Damgası: {veri.get('processed_time', '')}")
                
            else:
                st.success(f"💎 **{tier_info} Paket:** Gerçek zamanlı veri akışı devrede.")
                st.markdown("### ⚡ Anlık Piyasa Verileri")
                col1, col2, col3 = st.columns(3)
                col1.metric(f"Mevcut Fiyat ({symbol})", f"${veri.get('average_price') or 0:,.2f}")
                col2.metric("İşlem Hacmi (USD)", f"${veri.get('volume_usd') or 0:,.0f}")
                col3.metric("Veri Zamanı", veri.get('processed_time', '')[11:19])

                st.markdown("### 🧠 AI Model & Derin Analiz")
                pc1, pc2, pc3 = st.columns(3)
                
                if tier_info == "VIP":
                    fark = (veri.get('predicted_price') or 0) - (veri.get('average_price') or 0)
                    pc1.metric("Yapay Zeka Fiyat Tahmini", f"${veri.get('predicted_price') or 0:,.2f}", delta=f"{fark:,.2f} USD")
                    pc2.metric("CVD (Alım/Satım Baskısı)", f"{veri.get('cvd') or 0:,.2f}")
                    pc3.metric("Yön Sinyali", str(veri.get('trade_side', 'N/A')))
                else:
                    pc1.metric("Yapay Zeka Tahmini", "🔒 VIP'ye Özel")
                    pc2.metric("CVD (Baskı Endeksi)", "🔒 VIP'ye Özel")
                    pc3.metric("Sinyal Yönü", "🔒 VIP'ye Özel")

        elif res.status_code == 404:
            st.warning(f"⚠️ '{symbol}' için veri bekleniyor... (Sistemde henüz 1 dakikalık veri birikmemiş olabilir, lütfen 30 saniye bekleyin.)")
        else:
            st.error(f"Hata kodu: {res.status_code}")
            
    except Exception as e:
        st.error(f"API Bağlantı Hatası: {e}")

def render_bot_settings(api_key):
    headers = {"X-API-Key": api_key}
    bot_settings = {}
    try:
        res = requests.get(f"{API_BASE_URL}/bot/settings", headers=headers)
        if res.status_code == 200:
            bot_settings = res.json().get("data", {})
    except Exception as e:
        st.error(f"Bot ayarları yüklenemedi: {e}")
        return

    st.markdown("### ⚙️ Bot Parametreleri")
    with st.form("bot_settings_form"):
        bot_active = st.toggle("Bot Çalışıyor", value=bot_settings.get("bot_active", False), help="Botu aktif ettiğinizde milisaniyelik arbitraj tarayıcı ve emir tetikleyici çalışır.")
        bot_sim_mode = st.toggle("Yatırımcı Simülasyon Modu", value=bot_settings.get("bot_sim_mode", True), help="Sunum ve yatırımcı toplantıları için sanal kâr ve işlem simülasyonu.")
        
        bot_min_spread = st.slider("Min. Arbitraj Makası (%)", min_value=0.01, max_value=2.0, value=float(bot_settings.get("bot_min_spread", 0.15)), step=0.01)
        bot_min_trust = st.slider("Min. Spark Güven Skoru", min_value=0, max_value=100, value=int(bot_settings.get("bot_min_trust", 80)), step=5)
        
        submit_settings = st.form_submit_button("💾 Ayarları Kaydet ve Başlat", use_container_width=True)
        if submit_settings:
            try:
                update_res = requests.post(f"{API_BASE_URL}/bot/settings", json={
                    "bot_active": bot_active,
                    "bot_sim_mode": bot_sim_mode,
                    "bot_min_spread": bot_min_spread,
                    "bot_min_trust": bot_min_trust
                }, headers=headers)
                if update_res.status_code == 200:
                    st.success("✅ HFT Bot ayarları güncellendi!")
                    time.sleep(1)
                    st.rerun()
                else:
                    st.error("❌ Ayarlar güncellenemedi.")
            except Exception as e:
                st.error(f"Bağlantı hatası: {e}")

@st.fragment(run_every=2)
def render_bot_performance(api_key, container):
    headers = {"X-API-Key": api_key}
    with container:
        try:
            trades_res = requests.get(f"{API_BASE_URL}/bot/trades", headers=headers)
            if trades_res.status_code == 200:
                trades_data = trades_res.json()
                stats = trades_data.get("stats", {})
                trades_list = trades_data.get("trades", [])
                
                st.markdown("### 📊 HFT Bot Performans Raporu")
                m1, m2 = st.columns(2)
                total_p = stats.get("total_profit_usd", 0.0)
                total_t = stats.get("total_trades", 0)
                succ_t = stats.get("successful_trades", 0)
                success_rate = (succ_t / total_t * 100) if total_t > 0 else 0.0
                
                m1.metric("Toplam Simüle/Gerçek Kâr", f"${total_p:,.4f}", delta=f"+${total_p:,.4f}" if total_p > 0 else None)
                m2.metric("Başarı Oranı", f"%{success_rate:.2f}", delta=f"{succ_t}/{total_t} işlem")
                
                # Plotly chart for cumulative profit
                if trades_list:
                    df_trades = pd.DataFrame(trades_list)
                    df_trades['processed_time'] = pd.to_datetime(df_trades['processed_time'])
                    df_trades = df_trades.sort_values(by='processed_time')
                    df_trades['cumulative_profit'] = df_trades['profit_usd'].cumsum()
                    
                    fig = px.line(
                        df_trades, 
                        x='processed_time', 
                        y='cumulative_profit', 
                        labels={'processed_time': 'İşlem Zamanı', 'cumulative_profit': 'Kâr (USD)'},
                        template="plotly_dark"
                    )
                    fig.update_traces(line_color='#00E5FF', line_width=2)
                    fig.update_layout(
                        margin=dict(l=10, r=10, t=10, b=10),
                        height=200,
                        paper_bgcolor='rgba(0,0,0,0)',
                        plot_bgcolor='rgba(0,0,0,0)'
                    )
                    st.plotly_chart(fig, use_container_width=True)
                    
                    # Scrolling trade logs table
                    st.markdown("### 📜 Canlı İşlem Akışı (HFT Log)")
                    df_display = pd.DataFrame(trades_list)[['processed_time', 'symbol', 'buy_exchange', 'sell_exchange', 'spread_pct', 'profit_usd', 'mode', 'status']].sort_values(by='processed_time', ascending=False)
                    df_display.columns = ['Zaman', 'Sembol', 'Alış Borsası', 'Satış Borsası', 'Makas (%)', 'Kâr (USD)', 'Mod', 'Durum']
                    st.dataframe(df_display, use_container_width=True, hide_index=True)
                else:
                    st.info("Piyasa taranıyor... Uygun arbitraj fırsatı oluştuğunda işlemler burada listelenecektir.")
            else:
                st.error("Veriler okunamadı.")
        except Exception as e:
            st.error(f"Performans verisi çekilemedi: {e}")

def main_dashboard():
    # --- YAN PANEL ---
    with st.sidebar:
        st.markdown("### 🛠️ Geliştirici Paneli")
        st.caption(f"Kullanıcı: {st.session_state['email']}")
        
        new_tier = st.radio("Yetki Değiştir (Test):", ["FREE", "PRO", "VIP"], index=["FREE", "PRO", "VIP"].index(st.session_state['tier']))
        if st.button("Yetkiyi Güncelle"):
            requests.post(f"{API_BASE_URL}/auth/admin_update_tier", json={"email": st.session_state['email'], "new_tier": new_tier})
            st.session_state['tier'] = new_tier
            st.success(f"Yetki {new_tier} yapıldı!")
            time.sleep(1)
            st.rerun()
            
        st.markdown("---")
        st.markdown("### 📥 Veri İndirme Merkezi")
        
        # 🚀 YENİ: TIER'A GÖRE İNDİRME BUTONLARI
        if st.session_state['tier'] == "FREE":
            st.info("💡 FREE kullanıcılar harici kaynaklardan (Yahoo Finance) gecikmeli geçmiş verileri indirebilir.")
            if st.button("📈 1 Aylık Geçmişi İndir (YFinance)"):
                with st.spinner("Harici kaynaktan çekiliyor..."):
                    h_res = requests.get(f"{API_BASE_URL}/history/BTCUSDT", headers={"X-API-Key": st.session_state['api_key']})
                    if h_res.status_code == 200:
                        df_history = pd.DataFrame(h_res.json()['data'])
                        csv = df_history.to_csv(index=False).encode('utf-8')
                        st.download_button(label="📥 CSV'yi Kaydet", data=csv, file_name="yfinance_free_data.csv", mime="text/csv")
                    else:
                        st.error("Veri çekilemedi.")
        else:
            st.success(f"⚡ {st.session_state['tier']} Paket: Veritabanından yüksek hızda ham veri indirme aktif.")
            st.markdown(f"Son {'6 Saat' if st.session_state['tier'] == 'PRO' else '24 Saat'} - Saniyelik Veri")
            st.markdown("[📥 Ana Veritabanından İndir (API Endpoint)](http://localhost:8000/api/v1/download/market)")
        
        st.markdown("---")
        if st.button("🚪 Çıkış Yap"):
            st.session_state.clear()
            st.rerun()

    # --- ANA EKRAN SEKMELERİ ---
    tab1, tab2, tab3 = st.tabs(["📡 Canlı Veri Terminali", "🤖 Otonom HFT Bot", "⚙️ API Anahtarları"])
    
    with tab1:
        st.title("📡 Canlı Veri Akışı")
        symbol = st.selectbox("Görüntülenecek Sembol:", COINS, index=0)
        st.markdown("---")
        render_live_data(symbol, st.session_state["api_key"])
        
    with tab2:
        st.title("🤖 Otonom HFT Arbitraj Botu")
        st.markdown("TimescaleDB ve Redis entegrasyonlu milisaniyelik arbitraj ve Spark akıllı filtreleme paneli.")
        
        col_ctrl, col_perf = st.columns([2, 3])
        with col_ctrl:
            render_bot_settings(st.session_state["api_key"])
        render_bot_performance(st.session_state["api_key"], col_perf)
        
    with tab3:
        st.title("⚙️ Borsa API Entegrasyonu")
        st.markdown("Botun gerçek para ile çalışabilmesi için borsa API anahtarlarınızı girin. Anahtarlarınız XOR maskesi kullanılarak şifrelenir ve veritabanında saklanır.")
        
        headers = {"X-API-Key": st.session_state["api_key"]}
        with st.form("api_keys_form"):
            st.markdown("#### 🔸 Binance API Anahtarları (CCXT Destekli)")
            binance_key = st.text_input("Binance API Key", type="password", placeholder="Binance API Key giriniz...")
            binance_secret = st.text_input("Binance Secret Key", type="password", placeholder="Binance Secret Key giriniz...")
            
            st.markdown("#### 🔸 OKX API Anahtarları (CCXT Destekli)")
            okx_key = st.text_input("OKX API Key", type="password", placeholder="OKX API Key giriniz...")
            okx_secret = st.text_input("OKX Secret Key", type="password", placeholder="OKX Secret Key giriniz...")
            okx_pass = st.text_input("OKX Passphrase", type="password", placeholder="OKX Passphrase giriniz...")
            
            submit_keys = st.form_submit_button("🔐 Anahtarları Güvenli Kaydet", use_container_width=True)
            if submit_keys:
                if not (binance_key or okx_key):
                    st.warning("⚠️ Lütfen en az bir borsanın anahtarlarını giriniz.")
                else:
                    try:
                        keys_res = requests.post(f"{API_BASE_URL}/bot/keys", json={
                            "binance_key": binance_key,
                            "binance_secret": binance_secret,
                            "okx_key": okx_key,
                            "okx_secret": okx_secret,
                            "okx_pass": okx_pass
                        }, headers=headers)
                        if keys_res.status_code == 200:
                            st.success("✅ API anahtarları şifrelenerek veritabanına kaydedildi!")
                        else:
                            st.error("❌ Anahtarlar kaydedilemedi.")
                    except Exception as e:
                        st.error(f"Bağlantı hatası: {e}")

if st.session_state["api_key"]: main_dashboard()
else: auth_screen()