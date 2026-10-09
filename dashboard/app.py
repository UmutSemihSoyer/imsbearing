import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from pathlib import Path
from scipy.fft import fft, fftfreq
import os
import sys

# Config yollarını içe aktarma
sys.path.append(".")
from src.config import PROCESSED_DATA_DIR, RAW_DATA_DIR, SAMPLING_RATE, BPFO, BPFI, BSF, FTF, RESULTS_DIR
from src.data_loader import get_sorted_file_list, load_single_ims_file
from src.advanced_signal_processing import compute_envelope_spectrum, compute_fast_kurtogram
from src.plant_monitor import PlantFleetMonitor
from src.alert_system import AlertDispatcher
from src.report_generator import generate_excel_report, generate_pdf_report

# Streamlit Sayfa Yapılandırması
st.set_page_config(
    page_title="IMS Bearing - Enterprise Predictive Maintenance Platform",
    page_icon="⚙️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom Dark Glassmorphism CSS
st.markdown("""
<style>
    .main {
        background-color: #0b0f19;
        color: #e2e8f0;
    }
    .stMetric {
        background: rgba(30, 41, 59, 0.7);
        border: 1px solid rgba(255, 255, 255, 0.1);
        padding: 15px;
        border-radius: 12px;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3);
    }
    .status-normal {
        color: #10b981;
        font-weight: bold;
        font-size: 1.2rem;
    }
    .status-warning {
        color: #f59e0b;
        font-weight: bold;
        font-size: 1.2rem;
    }
    .status-critical {
        color: #ef4444;
        font-weight: bold;
        font-size: 1.2rem;
    }
</style>
""", unsafe_allow_dict=True)

@st.cache_data
def load_predictions_data():
    pred_file = PROCESSED_DATA_DIR / "final_predictions_test2.csv"
    if not pred_file.exists():
        return None
    return pd.read_csv(pred_file)

@st.cache_data
def load_advanced_envelope_data():
    adv_file = PROCESSED_DATA_DIR / "features_advanced_envelope_test2.csv"
    if not adv_file.exists():
        return None
    return pd.read_csv(adv_file)

# Başlık Paneli
st.title("⚙️ NASA IMS Bearing - Enterprise Predictive Maintenance & RUL Platform")
st.markdown("---")

df_pred = load_predictions_data()
df_adv = load_advanced_envelope_data()

if df_pred is None:
    st.error("⚠️ İşlenmiş tahmin verisi bulunamadı (`data/processed/final_predictions_test2.csv`). Lütfen öncelikle veri işleme aşamalarını çalıştırın.")
    st.stop()

# Kenar Çubuğu (Sidebar)
st.sidebar.header("🎛️ Zaman Akışı ve Kontrol")
max_idx = len(df_pred) - 1
selected_idx = st.sidebar.slider("Zaman Adımı (Snapshot Index):", 0, max_idx, max_idx // 2)

current_row = df_pred.iloc[selected_idx]
hi_val = current_row["health_index_pca"]
state = current_row["health_state"]
rul_val = current_row.get("predicted_rul", current_row["target_rul"])
anomaly_forest = current_row.get("anomaly_iso_forest", 0)

# Üst Metrik Kartları (KPI Cards)
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(label="Rulman Sağlık İndeksi (HI)", value=f"{hi_val * 100:.1f} %", delta=f"{(hi_val - 1.0) * 100:.1f}%")

with col2:
    if state == "Normal":
        st.markdown(f"**Durum:** <span class='status-normal'>🟢 Normal</span>", unsafe_allow_dict=True)
    elif state == "Warning":
        st.markdown(f"**Durum:** <span class='status-warning'>🟡 Erken Aşınma Uyarısı</span>", unsafe_allow_dict=True)
    else:
        st.markdown(f"**Durum:** <span class='status-critical'>🔴 Kritik Arıza Seviyesi</span>", unsafe_allow_dict=True)

with col3:
    st.metric(label="Kalan Faydalı Ömür (RUL)", value=f"{int(rul_val)} Saat", delta_color="inverse")

with col4:
    anom_text = "🚨 Anomali Tespit Edildi" if anomaly_forest == 1 else "✅ Normal Çalışma"
    st.metric(label="Anomali Durumu (IsoForest)", value=anom_text)

st.markdown("---")

# Ana Sekme Yapısı
main_tab1, main_tab2, main_tab3, main_tab4 = st.tabs([
    "📈 Single Bearing RUL & Signal Trends",
    "🔍 FFT & Hilbert Envelope Spectrum",
    "🏢 Plant Fleet Health & Enterprise Map",
    "⚡ MLOps, REST API & Report Export"
])

with main_tab1:
    st.subheader("📈 Rulman Yıpranma ve Titreşim Trendleri")
    
    tab1, tab2, tab3, tab4 = st.tabs([
        "📉 Sağlık İndeksi (HI) Trendi",
        "📊 RMS & Kurtosis Trendi",
        "🎯 RUL Tahmin Trendi",
        "⚡ Gelişmiş Zarf (Envelope) Trendi"
    ])
    
    with tab1:
        fig_hi = go.Figure()
        fig_hi.add_trace(go.Scatter(x=df_pred["file_idx"], y=df_pred["health_index_pca"], mode="lines", name="Sağlık İndeksi (HI)", line=dict(color="#00f2fe", width=2.5)))
        fig_hi.add_vline(x=selected_idx, line_dash="dash", line_color="#f59e0b", annotation_text=f"Seçilen An: {selected_idx}")
        fig_hi.update_layout(template="plotly_dark", title="Zamana Göre Sağlık İndeksi Değişimi", xaxis_title="Zaman Adımı", yaxis_title="HI (0.0 - 1.0)")
        st.plotly_chart(fig_hi, use_container_width=True)
    
    with tab2:
        fig_rms = go.Figure()
        fig_rms.add_trace(go.Scatter(x=df_pred["file_idx"], y=df_pred["ch1_rms"], mode="lines", name="Kanal 1 RMS", line=dict(color="#38ef7d")))
        fig_rms.add_trace(go.Scatter(x=df_pred["file_idx"], y=df_pred["ch1_kurtosis"], mode="lines", name="Kanal 1 Kurtosis", line=dict(color="#ff9966")))
        fig_rms.add_vline(x=selected_idx, line_dash="dash", line_color="#f59e0b")
        fig_rms.update_layout(template="plotly_dark", title="Zamana Göre Titreşim Şiddeti (RMS & Kurtosis)", xaxis_title="Zaman Adımı")
        st.plotly_chart(fig_rms, use_container_width=True)
    
    with tab3:
        fig_rul = go.Figure()
        fig_rul.add_trace(go.Scatter(x=df_pred["file_idx"], y=df_pred["target_rul"], mode="lines", name="Gerçek RUL", line=dict(color="#4facfe")))
        if "predicted_rul" in df_pred.columns:
            fig_rul.add_trace(go.Scatter(x=df_pred["file_idx"], y=df_pred["predicted_rul"], mode="lines", name="Tahmin Edilen RUL", line=dict(color="#00f2fe", dash="dot")))
        fig_rul.add_vline(x=selected_idx, line_dash="dash", line_color="#f59e0b")
        fig_rul.update_layout(template="plotly_dark", title="Kalan Faydalı Ömür (RUL) Tahmin Performansı", xaxis_title="Zaman Adımı", yaxis_title="Kalan Ömür")
        st.plotly_chart(fig_rul, use_container_width=True)
    
    with tab4:
        if df_adv is not None:
            fig_env = go.Figure()
            fig_env.add_trace(go.Scatter(x=df_adv["file_idx"], y=df_adv["envelope_bpfo_peak"], mode="lines", name="BPFO Zarf Genliği (236.4 Hz)", line=dict(color="#ef4444", width=2)))
            fig_env.add_trace(go.Scatter(x=df_adv["file_idx"], y=df_adv["envelope_bpfi_peak"], mode="lines", name="BPFI Zarf Genliği (296.9 Hz)", line=dict(color="#f59e0b", width=2)))
            fig_env.add_vline(x=selected_idx, line_dash="dash", line_color="#00f2fe")
            fig_env.update_layout(template="plotly_dark", title="Hilbert Zarf Spektrumu BPFO / BPFI Arıza Frekans Genlik Değişimi", xaxis_title="Zaman Adımı", yaxis_title="Zarf Genliği")
            st.plotly_chart(fig_env, use_container_width=True)
        else:
            st.info("Zarf analizi verisi yüklenemedi.")

with main_tab2:
    st.subheader("🔍 Anlık Sinyal, FFT Spektrumu ve Zarf Spektrumu (Hilbert Transform)")
    
    raw_files = get_sorted_file_list(RAW_DATA_DIR / "test2")
    if selected_idx < len(raw_files):
        selected_file = raw_files[selected_idx]
        raw_signal = load_single_ims_file(selected_file)[:, 0] # Channel 1
        
        col_left, col_right = st.columns(2)
        
        with col_left:
            # Ham FFT
            N = len(raw_signal)
            yf = np.abs(fft(raw_signal))[:N // 2]
            xf = fftfreq(N, 1 / SAMPLING_RATE)[:N // 2]
            
            fig_fft = go.Figure()
            fig_fft.add_trace(go.Scatter(x=xf[:5000], y=yf[:5000], mode="lines", name="Ham FFT Spektrumu", line=dict(color="#00c6ff")))
            fig_fft.add_vline(x=BPFO, line_dash="dash", line_color="#ef4444", annotation_text="BPFO (236.4 Hz)")
            fig_fft.add_vline(x=BPFI, line_dash="dash", line_color="#f59e0b", annotation_text="BPFI (296.9 Hz)")
            fig_fft.update_layout(template="plotly_dark", title="Ham FFT Spektrumu & Karakteristik Frekanslar", xaxis_title="Frekans (Hz)", yaxis_title="Genlik")
            st.plotly_chart(fig_fft, use_container_width=True)
            
        with col_right:
            # Fast Kurtogram & Envelope Spectrum
            best_band, k_val = compute_fast_kurtogram(raw_signal)
            env_freqs, env_fft, envelope = compute_envelope_spectrum(raw_signal, lowcut=best_band[0], highcut=best_band[1])
            
            fig_env_spec = go.Figure()
            fig_env_spec.add_trace(go.Scatter(x=env_freqs[:2000], y=env_fft[:2000], mode="lines", name="Hilbert Zarf Spektrumu", line=dict(color="#ff007f")))
            fig_env_spec.add_vline(x=BPFO, line_dash="dash", line_color="#ef4444", annotation_text="BPFO (236.4 Hz)")
            fig_env_spec.add_vline(x=BPFI, line_dash="dash", line_color="#f59e0b", annotation_text="BPFI (296.9 Hz)")
            fig_env_spec.update_layout(
                template="plotly_dark",
                title=f"Hilbert Zarf Spektrumu (Kurtogram: {int(best_band[0])}-{int(best_band[1])} Hz)",
                xaxis_title="Frekans (Hz)",
                yaxis_title="Zarf Genliği"
            )
            st.plotly_chart(fig_env_spec, use_container_width=True)

with main_tab3:
    st.subheader("🏢 Fabrika & Tesis Çoklu Rulman Filo Sağlık İzleme")
    plant_monitor = PlantFleetMonitor()
    summary = plant_monitor.get_plant_health_summary()
    
    col_p1, col_p2, col_p3 = st.columns(3)
    with col_p1:
        st.metric("Tesis Genel Sağlık Skoru", f"{summary['overall_health_score']} %")
    with col_p2:
        st.metric("İzlenen Toplam Ekipman", f"{summary['total_assets']} Adet Rulman")
    with col_p3:
        st.metric("En Kritik Ekipman", summary['top_critical_asset'])

    st.markdown("#### 📋 Filo Ekipman Durum Tablosu ve Bakım Sıralaması")
    df_fleet = pd.DataFrame(summary["fleet_status_table"])
    st.dataframe(df_fleet[["asset_id", "line", "location", "rms", "kurtosis", "health_index", "status", "action_required"]], use_container_width=True)

    # Bar chart of asset health index
    fig_fleet = px.bar(
        df_fleet,
        x="asset_id",
        y="health_index",
        color="status",
        title="Tesis Ekipmanları Sağlık İndeksi (HI) Karşılaştırması",
        color_discrete_map={"CRITICAL": "#ef4444", "WARNING": "#f59e0b", "HEALTHY": "#10b981"},
        template="plotly_dark"
    )
    st.plotly_chart(fig_fleet, use_container_width=True)

with main_tab4:
    st.subheader("⚡ MLOps, REST API & Kurumsal Raporlama Sistemleri")
    
    col_r1, col_r2 = st.columns(2)
    
    with col_r1:
        st.markdown("### 📄 Kurumsal PDF & Excel Bakım Raporları")
        st.info("Tesis yöneticileri için otomatik 1-tıklamayla teknik bakım raporu üretin.")
        
        if st.button("📊 Excel ve PDF Bakım Raporunu Yeniden Üret"):
            excel_p = generate_excel_report(df_pred)
            pdf_p = generate_pdf_report(df_pred)
            st.success(f"✅ Raporlar üretildi:\n- `{excel_p}`\n- `{pdf_p}`")
            
        pdf_file_path = os.path.join(RESULTS_DIR, "bearing_health_report.pdf")
        if os.path.exists(pdf_file_path):
            with open(pdf_file_path, "rb") as f:
                st.download_button("📥 Teknik PDF Raporunu İndir", f, file_name="bearing_health_report.pdf", mime="application/pdf")

    with col_r2:
        st.markdown("### 🔔 Telegram / Slack Bakım Alarm Testi")
        st.info("Kritik eşik aşımlarında Telegram/Slack alarm kanalına otomatik bildirim gönderir.")
        
        bearing_test_id = st.text_input("Rulman ID", "PUMP-01-BRG1")
        test_rms = st.slider("Test RMS Değeri (g)", 0.05, 0.90, float(current_row["ch1_rms"]))
        
        if st.button("🚨 Alarm Tetikleme Testi"):
            dispatcher = AlertDispatcher()
            result = dispatcher.evaluate_and_notify(
                bearing_test_id,
                {"rms": test_rms, "kurtosis": float(current_row["ch1_kurtosis"])},
                float(rul_val)
            )
            if result["alert_triggered"]:
                st.warning(f"🚨 ALERT DISPATCHED [{result['severity']}]\n\n{result['message']}")
            else:
                st.success("✅ Normal Operating Condition - No alarm triggered.")
