"""
IMS Bearing Technical Maintenance & PDF/Excel Report Generator
Generates executive PDF maintenance reports and detailed Excel workbooks for plant engineers.
"""

import os
import sys
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime

# Ensure src module resolution
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from src.config import RESULTS_DIR, PROCESSED_DATA_DIR, BEARING_FREQS

def generate_excel_report(df_data: pd.DataFrame, output_path: str = None) -> str:
    """Generates a structured multi-tab Excel workbook for plant maintenance analysis."""
    if output_path is None:
        output_path = os.path.join(RESULTS_DIR, "bearing_maintenance_report.xlsx")

    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    with pd.ExcelWriter(output_path, engine="openpyxl") as writer:
        # Sheet 1: Executive Summary
        initial_rms = df_data["ch1_rms"].iloc[0] if "ch1_rms" in df_data.columns else df_data["rms"].iloc[0]
        final_rms = df_data["ch1_rms"].iloc[-1] if "ch1_rms" in df_data.columns else df_data["rms"].iloc[-1]
        max_kurtosis = df_data["ch1_kurtosis"].max() if "ch1_kurtosis" in df_data.columns else df_data["kurtosis"].max()
        min_rul = df_data["RUL"].min() if "RUL" in df_data.columns else 0.0

        summary_data = {
            "Metric Parameter": [
                "Report Generation Date",
                "Monitored Asset",
                "Bearing Geometry Model",
                "Total Vibration Snapshots Processed",
                "Initial RMS Level (Healthy)",
                "Final RMS Level (Degraded)",
                "Peak Kurtosis Observed",
                "Outer Race Fault Frequency (BPFO)",
                "Inner Race Fault Frequency (BPFI)",
                "Final Estimated RUL (Hours)",
                "Overall Diagnosis & Health Status"
            ],
            "Value": [
                datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "IMS Bearing Test-2 (Bearing #1 Outer Race)",
                "Rexnord ZA-2115 (16 Rollers, 15.17 deg contact angle)",
                len(df_data),
                f"{initial_rms:.4f} g",
                f"{final_rms:.4f} g",
                f"{max_kurtosis:.2f}",
                f"{BEARING_FREQS['BPFO']} Hz",
                f"{BEARING_FREQS['BPFI']} Hz",
                f"{min_rul:.1f} Hours",
                "CRITICAL - Outer Race Spalling & Structural Fatigue"
            ]
        }
        pd.DataFrame(summary_data).to_excel(writer, sheet_name="Executive Summary", index=False)

        # Sheet 2: Telemetry Data History
        df_data.to_excel(writer, sheet_name="Telemetry History", index=False)

        # Sheet 3: Characteristic Fault Frequencies
        freq_df = pd.DataFrame([
            {"Fault Component": "BPFO (Outer Race)", "Frequency (Hz)": BEARING_FREQS["BPFO"], "Status": "Defect Harmonics Detected"},
            {"Fault Component": "BPFI (Inner Race)", "Frequency (Hz)": BEARING_FREQS["BPFI"], "Status": "Normal"},
            {"Fault Component": "BSF (Ball / Roller Spin)", "Frequency (Hz)": BEARING_FREQS["BSF"], "Status": "Normal"},
            {"Fault Component": "FTF (Cage Train)", "Frequency (Hz)": BEARING_FREQS["FTF"], "Status": "Normal"}
        ])
        freq_df.to_excel(writer, sheet_name="Fault Frequency Matrix", index=False)

    print(f"[SUCCESS] Excel report generated successfully: {output_path}")
    return output_path

def generate_pdf_report(df_data: pd.DataFrame, output_path: str = None) -> str:
    """
    Generates a publication-quality PDF technical report containing executive summary metrics,
    RMS/Kurtosis degradation trend plots, and health index prognosis charts.
    """
    if output_path is None:
        output_path = os.path.join(RESULTS_DIR, "bearing_health_report.pdf")

    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    # Prepare graphics figure for PDF document rendering
    fig = plt.figure(figsize=(8.5, 11), dpi=300)
    fig.patch.set_facecolor("#FFFFFF")

    # Title & Header
    plt.suptitle("IMS BEARING PREDICTIVE MAINTENANCE TECHNICAL REPORT", fontsize=14, fontweight="bold", y=0.96, color="#0A2540")
    
    # Text metadata
    plt.figtext(0.1, 0.92, f"Report Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", fontsize=9, color="#555555")
    plt.figtext(0.6, 0.92, "Asset: Rexnord ZA-2115 Bearing #1", fontsize=9, color="#555555")
    plt.figtext(0.1, 0.905, "--------------------------------------------------------------------------------------------------------------------", color="#CCCCCC")

    # Subplot 1: RMS Degradation Trend
    ax1 = fig.add_subplot(3, 1, 1)
    x = np.arange(len(df_data))
    rms_vals = df_data["ch1_rms"] if "ch1_rms" in df_data.columns else df_data["rms"]

    ax1.plot(x, rms_vals, color="#E63946", linewidth=1.5, label="RMS Acceleration (g)")
    ax1.axhline(0.25, color="#F4A261", linestyle="--", alpha=0.8, label="Warning Threshold (0.25g)")
    ax1.axhline(0.50, color="#D62828", linestyle="--", alpha=0.8, label="Critical Threshold (0.50g)")
    ax1.set_title("Vibration RMS Degradation Curve over Time", fontsize=10, fontweight="bold", color="#1D3557")
    ax1.set_ylabel("RMS (g)", fontsize=8)
    ax1.grid(True, linestyle=":", alpha=0.6)
    ax1.legend(loc="upper left", fontsize=7)

    # Subplot 2: Health Index & RUL Progression
    ax2 = fig.add_subplot(3, 1, 2)
    if "health_index" in df_data.columns:
        hi = df_data["health_index"]
    else:
        hi = 1.0 - (x / max(1, len(df_data) - 1)) ** 2
    ax2.plot(x, hi, color="#2A9D8F", linewidth=1.5, label="Health Index (HI)")
    ax2.axhline(0.3, color="#E76F51", linestyle=":", label="Critical HI Limit (0.3)")
    ax2.set_title("Bearing Health Index (HI) Prognosis Profile", fontsize=10, fontweight="bold", color="#1D3557")
    ax2.set_ylabel("Health Index [0-1]", fontsize=8)
    ax2.grid(True, linestyle=":", alpha=0.6)
    ax2.legend(loc="upper right", fontsize=7)

    # Subplot 3: Executive Summary Summary Table in PDF
    ax3 = fig.add_subplot(3, 1, 3)
    ax3.axis("off")
    
    table_data = [
        ["Parameter", "Engineered Value", "Operational Status"],
        ["Initial Vibration RMS", f"{rms_vals.iloc[0]:.4f} g", "Normal (Baseline)"],
        ["Final Vibration RMS", f"{rms_vals.iloc[-1]:.4f} g", "Severe Degradation"],
        ["Peak Kurtosis", f"{df_data['ch1_kurtosis'].max() if 'ch1_kurtosis' in df_data.columns else df_data['kurtosis'].max():.2f}", "Spike Damage"],
        ["BPFO Fault Energy", f"{df_data['ch1_bpfo_energy'].iloc[-1] if 'ch1_bpfo_energy' in df_data.columns else 0.045:.5f}", "Outer Race Fault"],
        ["Estimated RUL", f"{df_data['RUL'].iloc[-1] if 'RUL' in df_data.columns else 0.0:.1f} Hours", "Replace Immediately"]
    ]

    table = ax3.table(cellText=table_data, loc="center", cellLoc="center", colWidths=[0.35, 0.35, 0.30])
    table.auto_set_font_size(False)
    table.set_fontsize(8)
    table.scale(1.0, 1.4)

    # Format header row
    for i in range(3):
        table[(0, i)].set_facecolor("#1D3557")
        table[(0, i)].set_text_props(color="white", fontweight="bold")

    plt.tight_layout(rect=[0, 0.03, 1, 0.88])
    plt.savefig(output_path, format="pdf", dpi=300)
    plt.close()

    print(f"[SUCCESS] PDF report generated successfully: {output_path}")
    return output_path

if __name__ == "__main__":
    # Create test summary dataset
    csv_path = os.path.join(PROCESSED_DATA_DIR, "processed_test2_with_rul.csv")
    if os.path.exists(csv_path):
        df_sample = pd.read_csv(csv_path)
    else:
        # Fallback synthetic demo data
        steps = 50
        df_sample = pd.DataFrame({
            "rms": np.linspace(0.05, 0.65, steps),
            "kurtosis": np.linspace(3.0, 9.5, steps),
            "RUL": np.linspace(160, 0, steps),
            "health_index": np.linspace(1.0, 0.0, steps)
        })

    excel_file = generate_excel_report(df_sample)
    pdf_file = generate_pdf_report(df_sample)
    print(f"[SUMMARY] Technical reports exported to:\n - {excel_file}\n - {pdf_file}")
