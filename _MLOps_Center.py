import streamlit as st
import pandas as pd
import mlflow
import plotly.express as px
import plotly.graph_objects as go
from utils import inject_custom_css, init_mlflow

st.set_page_config(page_title="AutoML Liderlik Tablosu", layout="wide", page_icon="🏆")
inject_custom_css()

# MLflow bağlantısını kontrol ediyorum. Bağlantı yoksa sayfayı boşuna yüklemem.
is_connected, active_uri = init_mlflow()

# --- BAŞLIK VE DURUM ---
c1, c2 = st.columns([3, 1])
with c1:
    st.title("🏆 AutoML Liderlik Tablosu")
    st.caption("Proje: Gerçek Zamanlı Finansal Tahmin | Hedef Değişken: Fiyat ($)")
with c2:
    if is_connected:
        st.success(f"Bağlantı Başarılı: {active_uri}")
    else:
        st.error("Bağlantı Yok (Offline)")

# --- VERİ İŞLEME VE ANALİZ ---
if is_connected:
    try:
        runs = mlflow.search_runs(search_all_experiments=True)
    except:
        runs = pd.DataFrame()

    if not runs.empty:
        # 1. VERİ TEMİZLİĞİ VE STANDARDİZASYON
        # MLflow'dan gelen veriler bazen karışık olabilir. Algoritma isimlerini temizleyip
        # okunabilir hale getiriyorum (örn: 'random_forest' -> 'RANDOM FOREST')
        if 'tags.winner_algo' in runs.columns:
            runs['Model'] = runs['tags.winner_algo'].fillna('Bilinmeyen Model')
        else:
            runs['Model'] = runs.get('tags.mlflow.runName', 'Model')
        
        runs['Model'] = runs['Model'].str.replace('_', ' ').str.upper()

        # Metrikleri sayısal formata çeviriyorum, yoksa grafik çizemeyiz.
        if 'metrics.rmse' in runs.columns:
            runs['RMSE'] = pd.to_numeric(runs['metrics.rmse'], errors='coerce').fillna(9999)
        else:
            runs['RMSE'] = 9999.0
            
        if 'metrics.r2' in runs.columns:
            runs['R2'] = pd.to_numeric(runs['metrics.r2'], errors='coerce').fillna(0)
        else:
            runs['R2'] = 0.0
        
        # Eğitim süresini hesaplıyorum. Hızlı model mi yavaş model mi anlamak için kritik.
        if 'end_time' in runs.columns and 'start_time' in runs.columns:
            runs['Sure_ms'] = (pd.to_datetime(runs['end_time']) - pd.to_datetime(runs['start_time'])).dt.total_seconds() * 1000
        else:
            runs['Sure_ms'] = pd.to_numeric(runs.get('metrics.training_duration', 100), errors='coerce').fillna(100)

        # 2. SIRALAMA MANTIĞI (LEADERBOARD LOGIC)
        leaderboard = runs.sort_values(by='RMSE', ascending=True).reset_index(drop=True)
        leaderboard['Sira'] = leaderboard.index + 1
        
        leaderboard['Balon_Boyutu'] = leaderboard['R2'].apply(lambda x: max(float(x), 0.01))
        
        champion = leaderboard.iloc[0]

        def get_badges(row):
            badges = []
            if row['Sira'] == 1: badges.append("🏆 ŞAMPİYON")
            if row['Sure_ms'] == leaderboard['Sure_ms'].min(): badges.append("⚡ EN HIZLI")
            if row['R2'] > 0.95: badges.append("💎 HASSAS")
            return " ".join(badges)

        leaderboard['Rozetler'] = leaderboard.apply(get_badges, axis=1)

        # --- GÖRSEL ALAN (DASHBOARD) ---
        
        st.markdown("### 🥇 Canlıya Alınması Önerilen Model")
        with st.container():
            col_bp, col_metrics = st.columns([2, 1])
            
            with col_bp:
                st.markdown(f"""
                <div style="display: flex; align-items: center; gap: 10px; padding: 20px; overflow-x: auto;">
                    <div style="background: #333; padding: 10px; border-radius: 4px; color: #fff; white-space: nowrap;">HAM VERİ</div>
                    <div style="color: #666;">➜</div>
                    <div style="background: #333; padding: 10px; border-radius: 4px; color: #fff; white-space: nowrap;">ÖN İŞLEME</div>
                    <div style="color: #666;">➜</div>
                    <div style="background: #00CC96; padding: 15px; border-radius: 4px; color: #000; font-weight: bold; border: 2px solid white; white-space: nowrap;">
                        {champion['Model']}
                    </div>
                    <div style="color: #666;">➜</div>
                    <div style="background: #333; padding: 10px; border-radius: 4px; color: #fff; white-space: nowrap;">TAHMİN</div>
                </div>
                """, unsafe_allow_html=True)
                
            with col_metrics:
                c1, c2 = st.columns(2)
                c1.metric("RMSE (Hata Payı)", f"{champion['RMSE']:.4f}", delta_color="inverse")
                c2.metric("R2 Başarısı", f"{champion['R2']:.4f}")
                st.info(f"Eğitim Süresi: {champion['Sure_ms']:.0f} ms")

        st.divider()

        # ORTA KISIM: HIZ vs BAŞARI ANALİZİ
        st.markdown("### 📈 Hız ve Başarı Analizi")
        
        fig = px.scatter(
            leaderboard, 
            x="Sure_ms", 
            y="RMSE", 
            color="Model", 
            size="Balon_Boyutu", 
            hover_data=["Sira", "Rozetler", "R2"],
            template="plotly_dark",
            color_discrete_sequence=px.colors.qualitative.Pastel
        )
        
        fig.update_layout(
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            xaxis_title="Tahmin Süresi (ms) [Düşük daha iyi]",
            yaxis_title="RMSE Hata (Düşük daha iyi)",
            font=dict(family="Arial", size=12, color="white"),
            legend=dict(orientation="h", y=1.1)
        )
        
        if not leaderboard.empty:
            min_dur = leaderboard['Sure_ms'].min()
            min_rmse = leaderboard['RMSE'].min()
            mean_dur = leaderboard['Sure_ms'].mean()
            mean_rmse = leaderboard['RMSE'].mean()
            
            fig.add_shape(type="rect",
                x0=min_dur * 0.9, y0=min_rmse * 0.9,
                x1=mean_dur, y1=mean_rmse,
                line=dict(color="#00CC96", width=2, dash="dot"),
            )
            
        st.plotly_chart(fig, use_container_width=True)

        # ALT KISIM: DETAYLI TABLO
        st.markdown("### 📋 Model Sıralaması")
        
        display_df = leaderboard[['Sira', 'Model', 'Rozetler', 'RMSE', 'R2', 'Sure_ms', 'run_id']]
        
        st.dataframe(
            display_df,
            column_config={
                "Sira": st.column_config.NumberColumn("Sıra", format="#%d"),
                "RMSE": st.column_config.NumberColumn("Hata (RMSE)", format="%.4f"),
                "R2": st.column_config.ProgressColumn("Doğruluk (R2)", format="%.2f", min_value=-1, max_value=1),
                "Sure_ms": st.column_config.NumberColumn("Süre (ms)", format="%d ms"),
                "Rozetler": st.column_config.TextColumn("Ödüller"),
            },
            use_container_width=True,
            hide_index=True
        )
        
    else:
        st.warning("Henüz eğitilmiş model bulunamadı.")
        st.info("Lütfen önce 'train_model.py' dosyasını çalıştırın.")
else:
    st.error("MLflow bağlantısı kurulamadı. Lütfen Docker ayarlarınızı kontrol edin.")