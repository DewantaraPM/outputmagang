import io
import streamlit as st
import pandas as pd
import plotly.graph_objects as go

# ==========================================================
# 1. KONFIGURASI HALAMAN & GAYA VISUAL GREEN JAKARTA
# ==========================================================
st.set_page_config(
    page_title="Ringkasan Eksekutif IGRK DKI Jakarta",
    page_icon="🌿",
    layout="wide",
    initial_sidebar_state="collapsed",
)

FONT = "Inter, -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif"
WARNA = {
    "hijau_tua": "#14532D",
    "hijau_utama": "#15803D",
    "hijau_muda": "#10B981",
    "teal": "#0D9488",
    "biru": "#1D4ED8",
    "emas": "#D97706",
    "oranye": "#EA580C",
    "koral": "#E11D48",
    "abu": "#64748B",
}

st.markdown(
    """
    <style>
    [data-testid="stSidebar"], [data-testid="collapsedControl"], #MainMenu, footer {
        display: none !important;
    }
    .stApp {
        background-color: #EAF3EE;
        font-family: Inter, -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
        color: #0F172A;
    }
    .block-container {
        padding-top: 1.2rem;
        padding-bottom: 3rem;
        max-width: 1260px;
    }
    /* Mengubah st.container(border=True) menjadi Kartu Bento Putih Rapi */
    div[data-testid="stVerticalBlockBorderWrapper"] {
        background-color: #FFFFFF;
        border-radius: 16px !important;
        border: 1px solid #D5E6DC !important;
        box-shadow: 0 4px 12px rgba(20, 83, 45, 0.05);
        padding: 4px;
    }
    /* Banner Utama Ikonik Jakarta */
    .jkt-hero {
        background: linear-gradient(130deg, #0F3F24 0%, #15803D 62%, #0D9488 100%);
        border-radius: 20px;
        padding: 24px 30px 20px 30px;
        color: #FFFFFF;
        box-shadow: 0 10px 24px rgba(20, 83, 45, 0.15);
        margin-bottom: 1rem;
    }
    .jkt-badge {
        display: inline-block;
        background: rgba(255, 255, 255, 0.18);
        color: #DCFCE7;
        padding: 4px 12px;
        border-radius: 999px;
        font-size: 0.75rem;
        font-weight: 600;
        letter-spacing: 0.04em;
        text-transform: uppercase;
        margin-bottom: 6px;
    }
    .jkt-title {
        font-size: 1.75rem;
        font-weight: 800;
        margin: 0 0 6px 0;
        color: #FFFFFF;
    }
    .jkt-sub {
        font-size: 0.9rem;
        color: #E2F8EC;
        margin: 0;
        line-height: 1.5;
    }
    /* Pita Judul Seksi ala Infografis */
    .sec-banner {
        background: linear-gradient(90deg, #14532D 0%, #15803D 100%);
        color: #FFFFFF;
        padding: 9px 20px;
        border-radius: 12px;
        font-size: 1.02rem;
        font-weight: 800;
        letter-spacing: 0.03em;
        text-transform: uppercase;
        margin: 18px 0 12px 0;
        box-shadow: 0 4px 10px rgba(20, 83, 45, 0.12);
    }
    .pill-title {
        background: #14532D;
        color: #FFFFFF;
        font-size: 0.8rem;
        font-weight: 700;
        padding: 5px 14px;
        border-radius: 999px;
        display: inline-block;
        margin-bottom: 8px;
    }
    /* Kartu Warna Profil Atas */
    .stat-box {
        border-radius: 14px;
        padding: 14px 18px;
        color: #FFFFFF;
        margin-bottom: 10px;
    }
    .stat-box.amber { background: linear-gradient(135deg, #D97706 0%, #F59E0B 100%); }
    .stat-box.crimson { background: linear-gradient(135deg, #991B1B 0%, #DC2626 100%); }
    .stat-box.blue { background: linear-gradient(135deg, #1E3A8A 0%, #2563EB 100%); }
    .stat-num { font-size: 1.85rem; font-weight: 800; line-height: 1.1; margin: 2px 0; }
    .stat-lbl { font-size: 0.8rem; opacity: 0.95; font-weight: 600; }
    .stat-sub { font-size: 0.74rem; opacity: 0.88; margin-top: 4px; }
    /* Kartu 4 Sektor Aksi Mitigasi di Bawah */
    .aksi-header {
        padding: 8px 14px;
        border-radius: 10px;
        color: #FFFFFF;
        font-weight: 700;
        font-size: 0.9rem;
        margin-bottom: 8px;
        display: flex;
        justify-content: space-between;
        align-items: center;
    }
    .delta-pill {
        display: inline-block;
        background: rgba(255,255,255,0.24);
        padding: 2px 8px;
        border-radius: 999px;
        font-size: 0.72rem;
        font-weight: 700;
        margin-left: 6px;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


def fmt_id(x, d=0):
    return f"{x:,.{d}f}".replace(",", "X").replace(".", ",").replace("X", ".")


def fmt_delta(val_baru, val_acuan, d=0, satuan=""):
    selisih = val_baru - val_acuan
    if abs(selisih) < 1e-4:
        return ""
    tanda = "+" if selisih > 0 else "−"
    return f'<span class="delta-pill">Δ {tanda}{fmt_id(abs(selisih), d)}{satuan}</span>'


def tata_letak(fig, y_title=None, tinggi=290, show_legend=True):
    fig.update_layout(
        template="plotly_white",
        font=dict(family=FONT, size=11.5, color="#1E293B"),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=8, r=8, t=26, b=8),
        height=tinggi,
        showlegend=show_legend,
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="left", x=0, title_text=""),
        hovermode="x unified",
        yaxis=dict(title=y_title, gridcolor="#E2E8F0", zerolinecolor="#CBD5E1"),
        xaxis=dict(showgrid=False),
    )
    return fig


# ==========================================================
# 2. DATA ACUAN RESMI (RINGKASAN EKSEKUTIF LAPORAN DLH 2026)
# ==========================================================
@st.cache_data
def buat_data_acuan():
    # Sheet 1: Ringkasan Profil & Top 5 Direct (Tahun Berjalan 2025)
    df_profil = pd.DataFrame([
        {"Parameter": "Tahun_Laporan", "Nilai": 2025, "Satuan": "Tahun", "Keterangan": "Tahun inventarisasi terbaru"},
        {"Parameter": "Grand_Total_AR2", "Nilai": 66221, "Satuan": "Gg CO2e", "Keterangan": "Total emisi Direct + Indirect (AR2)"},
        {"Parameter": "Grand_Total_AR5", "Nilai": 66967, "Satuan": "Gg CO2e", "Keterangan": "Total emisi Direct + Indirect (AR5)"},
        {"Parameter": "Total_Direct_AR2", "Nilai": 31715, "Satuan": "Gg CO2e", "Keterangan": "Total emisi langsung (AR2)"},
        {"Parameter": "Total_Direct_AR5", "Nilai": 32461, "Satuan": "Gg CO2e", "Keterangan": "Total emisi langsung (AR5)"},
        {"Parameter": "Total_Indirect_Listrik", "Nilai": 34507, "Satuan": "Gg CO2e", "Keterangan": "Emisi tidak langsung listrik Jamali"},
        {"Parameter": "Konsumsi_Listrik_GWh", "Nilai": 38196, "Satuan": "GWh", "Keterangan": "Konsumsi listrik PLN DKI Jakarta"},
        {"Parameter": "Direct_Energi", "Nilai": 29311, "Satuan": "Gg CO2e", "Keterangan": "Sektor Energi (Tabel 1 AR2)"},
        {"Parameter": "Direct_Limbah", "Nilai": 2444, "Satuan": "Gg CO2e", "Keterangan": "Sektor Limbah (Tabel 1 AR2)"},
        {"Parameter": "Direct_AFOLU", "Nilai": -40, "Satuan": "Gg CO2e", "Keterangan": "Sektor AFOLU serapan bersih (Tabel 1 AR2)"},
        {"Parameter": "Top1_Transportasi", "Nilai": 18293, "Satuan": "Gg CO2e", "Keterangan": "Subsektor Transportasi (Tabel 5.8)"},
        {"Parameter": "Top2_Pembangkit", "Nilai": 7128, "Satuan": "Gg CO2e", "Keterangan": "Subsektor Pembangkit Listrik (Tabel 5.8)"},
        {"Parameter": "Top3_Industri", "Nilai": 2348, "Satuan": "Gg CO2e", "Keterangan": "Subsektor Industri Manufaktur (Tabel 5.8)"},
        {"Parameter": "Top4_Limbah_TPA", "Nilai": 1403, "Satuan": "Gg CO2e", "Keterangan": "Subsektor Limbah Padat TPA (Tabel 5.8)"},
        {"Parameter": "Top5_Residensial", "Nilai": 1391, "Satuan": "Gg CO2e", "Keterangan": "Subsektor Rumah Tangga Direct (Tabel 5.8)"},
        {"Parameter": "Reduksi_Sektoral_JtTon", "Nilai": 25.80, "Satuan": "Juta Ton CO2e", "Keterangan": "Selisih Baseline vs Inventori"},
        {"Parameter": "Persen_Reduksi_Sektoral", "Nilai": 28.0, "Satuan": "%", "Keterangan": "Persentase reduksi terhadap Baseline"},
    ])

    # Sheet 2: Deret Historis Baseline vs Inventori (Gambar 2 Ringkasan Eksekutif, 2015–2030)
    df_tren = pd.DataFrame({
        "Tahun": list(range(2015, 2031)),
        "Baseline_JtTon": [63.0, 64.0, 65.0, 69.0, 73.0, 73.3, 78.0, 81.0, 85.0, 88.0, 92.0, 94.0, 98.0, 100.0, 103.0, 107.0],
        "Inventori_JtTon": [56.7, 58.9, 57.1, 60.0, 60.9, 54.2, 56.7, 60.3, 62.6, 64.5, 66.2, None, None, None, None, None],
    })

    # Sheet 3: Tabel 3 Target Penurunan Emisi GRK Tahunan per 4 Sektor (2025–2030, dalam Gg CO2e)
    df_tabel3 = pd.DataFrame({
        "Tahun": [2025, 2026, 2027, 2028, 2029, 2030],
        "Energi (Final)": [12198, 14268, 16414, 18638, 20943, 23305],
        "Pembangkit Listrik": [8471, 8251, 8546, 8775, 8995, 9170],
        "Limbah": [416, 632, 803, 1085, 1316, 1598],
        "FOLU": [29, 26, 23, 20, 18, 16],
        "TOTAL": [21114, 23178, 25789, 28521, 31235, 34090],
    })

    # Sheet 4: Tabel 5 Proyeksi Tingkat Emisi 2019–2050 CPOS vs NZE (Disederhanakan 4 Sektor, dalam Gg CO2e)
    # Catatan: Energi (Final) = Komersial + Rumah Tangga + Industri + Transportasi pada Tabel 5
    df_tabel5 = pd.DataFrame({
        "Tahun": [2019, 2035, 2040, 2045, 2050],
        "Energi (Final)_CPOS": [49898, 60301, 59590, 57832, 55026],
        "Energi (Final)_NZE": [49898, 56742, 49454, 45137, 26887],
        "Pembangkit_CPOS": [8744, 9859, 9859, 9859, 9859],
        "Pembangkit_NZE": [8744, 9591, 8685, 0, 0],
        "Limbah_CPOS": [2305, 2385, 2377, 2240, 2470],
        "Limbah_NZE": [2305, 2299, 2249, 2262, 2244],
        "FOLU_CPOS": [-14, 37, 43, 48, 55],
        "FOLU_NZE": [-14, 37, 38, 38, 49],
        "Total_CPOS": [60933, 72579, 71870, 70157, 67413],
        "Total_NZE": [60933, 68673, 60426, 47415, 29185],
    })

    # Sheet 5: Tabel 2 Rincian Capaian Aksi Mitigasi (Halaman viii–ix, dalam Ton CO2e)
    df_aksi = pd.DataFrame([
        {"Sektor": "Energi", "Aksi Mitigasi": "Substitusi BBM ke gas Pembangkit Muara Karang & Tanjung Priok", "Baseline_Ton": 10460482, "Mitigasi_Ton": 7161905, "Reduksi_Ton": 3298577},
        {"Sektor": "Energi", "Aksi Mitigasi": "Efisiensi energi di pembangkit Muara Karang", "Baseline_Ton": 4197637, "Mitigasi_Ton": 2936879, "Reduksi_Ton": 1260758},
        {"Sektor": "Energi", "Aksi Mitigasi": "Penggunaan LHE untuk lampu jalan (PJU)", "Baseline_Ton": 603905, "Mitigasi_Ton": 334548, "Reduksi_Ton": 269357},
        {"Sektor": "Energi", "Aksi Mitigasi": "Penggunaan biofuel di subsektor industri", "Baseline_Ton": 372543, "Mitigasi_Ton": 225976, "Reduksi_Ton": 146566},
        {"Sektor": "Energi", "Aksi Mitigasi": "Penerapan green building di gedung pemerintah & komersial", "Baseline_Ton": 661638, "Mitigasi_Ton": 575090, "Reduksi_Ton": 86547},
        {"Sektor": "Energi", "Aksi Mitigasi": "Penggunaan PLTS rooftop gedung & komunal", "Baseline_Ton": 20678, "Mitigasi_Ton": 0, "Reduksi_Ton": 20678},
        {"Sektor": "Energi", "Aksi Mitigasi": "Penggunaan biofuel di subsektor komersial", "Baseline_Ton": 24280, "Mitigasi_Ton": 14728, "Reduksi_Ton": 9552},
        {"Sektor": "Energi", "Aksi Mitigasi": "Energi bersih: PLTSa & pembangkit listrik LFG", "Baseline_Ton": 9036, "Mitigasi_Ton": 847, "Reduksi_Ton": 8189},
        {"Sektor": "Energi", "Aksi Mitigasi": "Pemadaman listrik berkala (Earth Hour)", "Baseline_Ton": 366, "Mitigasi_Ton": 0, "Reduksi_Ton": 366},
        {"Sektor": "Energi", "Aksi Mitigasi": "Penggunaan PJU Tenaga Surya (PJU TS)", "Baseline_Ton": 113, "Mitigasi_Ton": 0, "Reduksi_Ton": 113},
        {"Sektor": "Transportasi", "Aksi Mitigasi": "Manajemen transportasi melalui penerapan sistem ITS", "Baseline_Ton": 67670762, "Mitigasi_Ton": 58883095, "Reduksi_Ton": 8787667},
        {"Sektor": "Transportasi", "Aksi Mitigasi": "Feeder busway", "Baseline_Ton": 1190711, "Mitigasi_Ton": 206661, "Reduksi_Ton": 966073},
        {"Sektor": "Transportasi", "Aksi Mitigasi": "Penggunaan biofuel transportasi", "Baseline_Ton": 1974534, "Mitigasi_Ton": 1262427, "Reduksi_Ton": 712107},
        {"Sektor": "Transportasi", "Aksi Mitigasi": "Busway (BRT Transjakarta)", "Baseline_Ton": 451139, "Mitigasi_Ton": 49028, "Reduksi_Ton": 402366},
        {"Sektor": "Transportasi", "Aksi Mitigasi": "Bus listrik", "Baseline_Ton": 183134, "Mitigasi_Ton": 38150, "Reduksi_Ton": 144984},
        {"Sektor": "Transportasi", "Aksi Mitigasi": "Penggunaan Kereta Api Listrik (KRL)", "Baseline_Ton": 245318, "Mitigasi_Ton": 144691, "Reduksi_Ton": 100627},
        {"Sektor": "Transportasi", "Aksi Mitigasi": "Penggunaan BBG transportasi", "Baseline_Ton": 70194, "Mitigasi_Ton": 56951, "Reduksi_Ton": 13243},
        {"Sektor": "Transportasi", "Aksi Mitigasi": "Penggunaan MRT", "Baseline_Ton": 16295, "Mitigasi_Ton": 6143, "Reduksi_Ton": 10153},
        {"Sektor": "Transportasi", "Aksi Mitigasi": "Car Free Day (CFD)", "Baseline_Ton": 7029, "Mitigasi_Ton": 0, "Reduksi_Ton": 7029},
        {"Sektor": "Transportasi", "Aksi Mitigasi": "Penggunaan LRT", "Baseline_Ton": 9843, "Mitigasi_Ton": 3000, "Reduksi_Ton": 6844},
        {"Sektor": "Limbah", "Aksi Mitigasi": "Kegiatan 3R kertas", "Baseline_Ton": 1574250, "Mitigasi_Ton": 1465372, "Reduksi_Ton": 109183},
        {"Sektor": "Limbah", "Aksi Mitigasi": "LFG Recovery di TPA Bantar Gebang", "Baseline_Ton": 1574250, "Mitigasi_Ton": 1537203, "Reduksi_Ton": 37352},
        {"Sektor": "Limbah", "Aksi Mitigasi": "PLTSa, RDF, maggot, pakan & biodigester", "Baseline_Ton": 1574250, "Mitigasi_Ton": 1558827, "Reduksi_Ton": 15727},
        {"Sektor": "Limbah", "Aksi Mitigasi": "Pengomposan sampah organik", "Baseline_Ton": 1574250, "Mitigasi_Ton": 1565718, "Reduksi_Ton": 8837},
        {"Sektor": "Limbah", "Aksi Mitigasi": "Pengolahan limbah cair on-site (IPAL)", "Baseline_Ton": 1083405, "Mitigasi_Ton": 1078576, "Reduksi_Ton": 4829},
        {"Sektor": "Limbah", "Aksi Mitigasi": "Pengolahan limbah cair off-site (IPLT)", "Baseline_Ton": 1083405, "Mitigasi_Ton": 1082747, "Reduksi_Ton": 658},
        {"Sektor": "Limbah", "Aksi Mitigasi": "Landfill Mining", "Baseline_Ton": 1574250, "Mitigasi_Ton": 1574269, "Reduksi_Ton": 285},
        {"Sektor": "Kehutanan", "Aksi Mitigasi": "Konservasi Hutan Mangrove (HL Angke Kapuk)", "Baseline_Ton": 40967, "Mitigasi_Ton": 34803, "Reduksi_Ton": 6164},
        {"Sektor": "Kehutanan", "Aksi Mitigasi": "Penanaman / Penghijauan", "Baseline_Ton": 40967, "Mitigasi_Ton": 39043, "Reduksi_Ton": 1924},
    ])

    return df_profil, df_tren, df_tabel3, df_tabel5, df_aksi


def konversi_ke_excel(df_p, df_tr, df_t3, df_t5, df_ak):
    buffer = io.BytesIO()
    with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
        df_p.to_excel(writer, sheet_name="1_Profil_Utama", index=False)
        df_tr.to_excel(writer, sheet_name="2_Tren_Historis", index=False)
        df_t3.to_excel(writer, sheet_name="3_Target_2025_2030", index=False)
        df_t5.to_excel(writer, sheet_name="4_Proyeksi_2035_2050", index=False)
        df_ak.to_excel(writer, sheet_name="5_Aksi_Mitigasi", index=False)
    return buffer.getvalue()


df_p_base, df_tr_base, df_t3_base, df_t5_base, df_ak_base = buat_data_acuan()

# ==========================================================
# 3. HEADER UTAMA & PANEL UNDUH / UNGGAH EXCEL TAHUNAN
# ==========================================================
st.markdown(
    """
    <div class="jkt-hero">
        <div style="display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:16px;">
            <div style="flex:1;min-width:300px;">
                <div class="jkt-badge">🌿 Dinas Lingkungan Hidup Provinsi DKI Jakarta • Ringkasan Eksekutif</div>
                <div class="jkt-title">Laporan Akhir | Profil Emisi & Capaian Mitigasi GRK DKI Jakarta</div>
                <p class="jkt-sub">
                    Pemutakhiran Data Inventarisasi (2010–2025), Target Tahunan RPRKD (2025–2030), dan Proyeksi Menuju 
                    <i>Net Zero Emission</i> 2050 (Pergub No. 90/2021).
                </p>
            </div>
            <div style="opacity:0.92;">
                <svg width="230" height="86" viewBox="0 0 250 96" fill="none" xmlns="http://www.w3.org/2000/svg">
                    <path d="M0 90 L10 80 L20 90 L30 80 L40 90 L50 80 L60 90 L70 80 L80 90 L90 80 L100 90 L110 80 L120 90 L130 80 L140 90 L150 80 L160 90 L170 80 L180 90 L190 80 L200 90 L210 80 L220 90 L230 80 L240 90 L250 80 L250 96 L0 96 Z" fill="rgba(255,255,255,0.18)"/>
                    <rect x="22" y="42" width="22" height="42" rx="2" fill="rgba(255,255,255,0.22)"/>
                    <rect x="50" y="30" width="26" height="54" rx="2" fill="rgba(255,255,255,0.28)"/>
                    <rect x="176" y="34" width="24" height="50" rx="2" fill="rgba(255,255,255,0.25)"/>
                    <rect x="206" y="46" width="22" height="38" rx="2" fill="rgba(255,255,255,0.20)"/>
                    <path d="M98 84 L152 84 L144 74 L106 74 Z" fill="rgba(255,255,255,0.45)"/>
                    <path d="M92 66 L158 66 L146 74 L104 74 Z" fill="rgba(255,255,255,0.65)"/>
                    <rect x="121" y="22" width="8" height="44" fill="#FFFFFF"/>
                    <rect x="116" y="19" width="18" height="4" rx="1" fill="#FFFFFF"/>
                    <path d="M125 6 C129 11 131 15 125 19 C119 15 121 11 125 6 Z" fill="#FBBF24"/>
                </svg>
            </div>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

with st.expander("📂 Panel Pemutakhiran Data Tahunan (Unduh Template Acuan / Unggah Spreadsheet Baru)", expanded=False):
    u1, u2, u3 = st.columns([1.1, 1.4, 1], gap="medium")
    with u1:
        st.markdown("**1. Unduh Spreadsheet Acuan**")
        st.caption("Berisi 5 tabel Ringkasan Eksekutif Laporan 2026 yang siap diedit untuk pembaruan tahunan.")
        file_excel_acuan = konversi_ke_excel(df_p_base, df_tr_base, df_t3_base, df_t5_base, df_ak_base)
        st.download_button(
            "📥 Unduh Template Excel Acuan (.xlsx)",
            data=file_excel_acuan,
            file_name="Data_Acuan_IGRK_DKI_2026.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True,
        )
    with u2:
        st.markdown("**2. Unggah Spreadsheet yang Telah Diedit**")
        uploaded_excel = st.file_uploader("Pilih file .xlsx hasil edit:", type=["xlsx"], label_visibility="collapsed")
    with u3:
        st.markdown("**3. Mode Tampilan Pembanding**")
        tampilkan_delta = st.toggle("Tampilkan Selisih (Δ) vs Data Acuan", value=True)
        if uploaded_excel is not None:
            st.success("✅ Data berhasil diperbarui dari file Excel yang diunggah!")
        else:
            st.info("ℹ️ Menampilkan Data Acuan Bawaan (Laporan 2026).")

# Membaca data dari Excel yang diunggah (jika ada), atau gunakan data acuan
if uploaded_excel is not None:
    try:
        xls = pd.ExcelFile(uploaded_excel)
        df_p = pd.read_excel(xls, "1_Profil_Utama")
        df_tr = pd.read_excel(xls, "2_Tren_Historis")
        df_t3 = pd.read_excel(xls, "3_Target_2025_2030")
        df_t5 = pd.read_excel(xls, "4_Proyeksi_2035_2050")
        df_ak = pd.read_excel(xls, "5_Aksi_Mitigasi")
    except Exception as e:
        st.error(f"Format sheet tidak sesuai template: {e}. Menggunakan data acuan bawaan.")
        df_p, df_tr, df_t3, df_t5, df_ak = df_p_base, df_tr_base, df_t3_base, df_t5_base, df_ak_base
else:
    df_p, df_tr, df_t3, df_t5, df_ak = df_p_base, df_tr_base, df_t3_base, df_t5_base, df_ak_base

p_now = dict(zip(df_p["Parameter"], df_p["Nilai"]))
p_ref = dict(zip(df_p_base["Parameter"], df_p_base["Nilai"]))
thn_lap = int(p_now.get("Tahun_Laporan", 2025))

# ==========================================================
# BLOK 1: PROFIL EMISI DKI JAKARTA (TAHUN BERJALAN)
# ==========================================================
st.markdown(f'<div class="sec-banner">1. Profil Emisi DKI Jakarta ({thn_lap})</div>', unsafe_allow_html=True)

b1_kiri, b1_kanan = st.columns([1.05, 1.35], gap="medium")

with b1_kiri:
    gt_ar2 = p_now["Grand_Total_AR2"]
    gt_ar5 = p_now["Grand_Total_AR5"]
    dir_ar2 = p_now["Total_Direct_AR2"]
    ind_val = p_now["Total_Indirect_Listrik"]
    gwh_val = p_now["Konsumsi_Listrik_GWh"]

    d_gt = fmt_delta(gt_ar2, p_ref["Grand_Total_AR2"]) if tampilkan_delta else ""
    d_dir = fmt_delta(dir_ar2, p_ref["Total_Direct_AR2"]) if tampilkan_delta else ""
    d_ind = fmt_delta(ind_val, p_ref["Total_Indirect_Listrik"]) if tampilkan_delta else ""

    porsi_dir = (dir_ar2 / gt_ar2) * 100.0
    porsi_ind = (ind_val / gt_ar2) * 100.0

    st.markdown(
        f"""
        <div class="stat-box amber">
            <div class="stat-lbl">🌍 GRAND TOTAL EMISI (AR2) {d_gt}</div>
            <div class="stat-num">{fmt_id(gt_ar2)} Gg CO₂e</div>
            <div class="stat-sub">Standar GWP AR5: <b>{fmt_id(gt_ar5)} Gg CO₂e</b></div>
        </div>
        <div class="stat-box crimson">
            <div class="stat-lbl">🏭 EMISI LANGSUNG / DIRECT ({fmt_id(porsi_dir, 0)}%) {d_dir}</div>
            <div class="stat-num">{fmt_id(dir_ar2)} Gg CO₂e</div>
            <div class="stat-sub">Energi: {fmt_id(p_now['Direct_Energi'])} Gg (92%) | Limbah: {fmt_id(p_now['Direct_Limbah'])} Gg (8%) | AFOLU: {fmt_id(p_now['Direct_AFOLU'])} Gg</div>
        </div>
        <div class="stat-box blue">
            <div class="stat-lbl">⚡ EMISI TIDAK LANGSUNG / LISTRIK PLN ({fmt_id(porsi_ind, 0)}%) {d_ind}</div>
            <div class="stat-num">{fmt_id(ind_val)} Gg CO₂e</div>
            <div class="stat-sub">Konsumsi Listrik Jaringan Jamali: <b>{fmt_id(gwh_val)} GWh</b></div>
        </div>
        """,
        unsafe_allow_html=True,
    )

with b1_kanan:
    with st.container(border=True):
        st.markdown(f'<div class="pill-title">Top 5 Kontributor Emisi Direct ({fmt_id(dir_ar2)} Gg CO₂e)</div>', unsafe_allow_html=True)
        top5_nama = ["Transportasi", "Pembangkit Listrik", "Industri Manufaktur", "Limbah Padat TPA", "Residensial (RT)"]
        top5_val = [
            p_now["Top1_Transportasi"],
            p_now["Top2_Pembangkit"],
            p_now["Top3_Industri"],
            p_now["Top4_Limbah_TPA"],
            p_now["Top5_Residensial"],
        ]
        fig_top5 = go.Figure(go.Bar(
            x=top5_val,
            y=top5_nama,
            orientation="h",
            marker_color=[WARNA["hijau_tua"], WARNA["hijau_utama"], WARNA["teal"], WARNA["emas"], WARNA["hijau_muda"]],
            marker_cornerradius=7,
            text=[f"<b>{fmt_id(v)} Gg</b> ({v/dir_ar2*100:.0f}%)" for v in top5_val],
            textposition="auto",
        ))
        fig_top5.update_layout(yaxis=dict(autorange="reversed"))
        st.plotly_chart(tata_letak(fig_top5, "Gg CO₂e", 255, show_legend=False), use_container_width=True, config={"displayModeBar": False})

# ==========================================================
# BLOK 2: TREN & KONTRIBUSI EMISI GRK (2015–2030)
# ==========================================================
st.markdown('<div class="sec-banner">2. Tren & Kontribusi Sumber Emisi GRK</div>', unsafe_allow_html=True)

b2_kiri, b2_kanan = st.columns([1.05, 1.35], gap="medium")

with b2_kiri:
    with st.container(border=True):
        st.markdown(f'<div class="pill-title">Kontribusi Sumber Emisi ({thn_lap})</div>', unsafe_allow_html=True)
        d1, d2 = st.columns(2)
        with d1:
            non_pembangkit = max(0.0, p_now["Direct_Energi"] - p_now["Top2_Pembangkit"])
            fig_pie1 = go.Figure(go.Pie(
                labels=["Listrik Indirect", "Direct Non-Pembangkit", "Pembangkit Listrik", "Limbah"],
                values=[ind_val, non_pembangkit, p_now["Top2_Pembangkit"], p_now["Direct_Limbah"]],
                hole=0.62,
                marker=dict(colors=[WARNA["biru"], WARNA["oranye"], WARNA["hijau_utama"], "#8B5CF6"]),
                textinfo="percent",
            ))
            fig_pie1.update_layout(
                annotations=[dict(text=f"<b>Total</b><br>{fmt_id(gt_ar2)}<br>Gg", x=0.5, y=0.5, font_size=12, showarrow=False)],
                margin=dict(l=4, r=4, t=10, b=10), height=235, paper_bgcolor="rgba(0,0,0,0)",
                legend=dict(orientation="h", yanchor="bottom", y=-0.35, xanchor="center", x=0.5, font=dict(size=10)),
            )
            st.plotly_chart(fig_pie1, use_container_width=True, config={"displayModeBar": False})
        with d2:
            fig_pie2 = go.Figure(go.Pie(
                labels=["Energi (92%)", "Limbah (8%)"],
                values=[p_now["Direct_Energi"], p_now["Direct_Limbah"]],
                hole=0.62,
                marker=dict(colors=[WARNA["biru"], WARNA["oranye"]]),
                textinfo="percent",
            ))
            fig_pie2.update_layout(
                annotations=[dict(text=f"<b>Direct</b><br>{fmt_id(dir_ar2)}<br>Gg", x=0.5, y=0.5, font_size=12, showarrow=False)],
                margin=dict(l=4, r=4, t=10, b=10), height=235, paper_bgcolor="rgba(0,0,0,0)",
                legend=dict(orientation="h", yanchor="bottom", y=-0.35, xanchor="center", x=0.5, font=dict(size=10)),
            )
            st.plotly_chart(fig_pie2, use_container_width=True, config={"displayModeBar": False})
        st.caption(f"Catatan: Sektor AFOLU mencatat serapan bersih sebesar **{fmt_id(p_now['Direct_AFOLU'])} Gg CO₂e (-0,1%)**.")

with b2_kanan:
    with st.container(border=True):
        st.markdown('<div class="pill-title">Tren Baseline vs Inventori Aktual (2015–2030)</div>', unsafe_allow_html=True)
        fig_tr = go.Figure()
        df_tr_valid = df_tr.dropna(subset=["Inventori_JtTon"])
        fig_tr.add_trace(go.Bar(
            x=df_tr_valid["Tahun"],
            y=df_tr_valid["Inventori_JtTon"],
            name="Realisasi Inventori (Juta Ton)",
            marker_color=WARNA["hijau_utama"],
            marker_cornerradius=4,
        ))
        fig_tr.add_trace(go.Scatter(
            x=df_tr["Tahun"],
            y=df_tr["Baseline_JtTon"],
            name="Tingkat Emisi Baseline",
            mode="lines+markers",
            line=dict(color=WARNA["koral"], width=2.5, dash="dash"),
        ))
        fig_tr.update_xaxes(dtick=1)
        st.plotly_chart(tata_letak(fig_tr, "Juta Ton CO₂e", 225), use_container_width=True, config={"displayModeBar": False})

        bau_now = df_tr_valid["Baseline_JtTon"].iloc[-1]
        inv_now = df_tr_valid["Inventori_JtTon"].iloc[-1]
        red_jt = p_now["Reduksi_Sektoral_JtTon"]
        red_pct = p_now["Persen_Reduksi_Sektoral"]
        st.markdown(
            f"""
            <div style="display:grid;grid-template-columns:repeat(3,1fr);gap:8px;margin-top:4px;">
                <div style="background:#FEE2E2;padding:8px 12px;border-radius:10px;text-align:center;">
                    <div style="font-size:0.74rem;color:#991B1B;font-weight:700;">Baseline {thn_lap}</div>
                    <div style="font-size:1.05rem;font-weight:800;color:#7F1D1D;">{fmt_id(bau_now, 1)} Jt Ton</div>
                </div>
                <div style="background:#FEF3C7;padding:8px 12px;border-radius:10px;text-align:center;">
                    <div style="font-size:0.74rem;color:#92400E;font-weight:700;">Inventori {thn_lap}</div>
                    <div style="font-size:1.05rem;font-weight:800;color:#78350F;">{fmt_id(inv_now, 1)} Jt Ton (−{fmt_id(red_pct, 1)}%)</div>
                </div>
                <div style="background:#DCFCE7;padding:8px 12px;border-radius:10px;text-align:center;">
                    <div style="font-size:0.74rem;color:#166534;font-weight:700;">Reduksi {thn_lap} vs Target 2030</div>
                    <div style="font-size:1.05rem;font-weight:800;color:#14532D;">{fmt_id(red_jt, 1)} / 34,09 Jt Ton</div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

# ==========================================================
# BLOK 3: ROADMAP DEKARBONISASI PER SEKTOR (2025–2050) — PERBAIKAN UTAMA
# ==========================================================
st.markdown('<div class="sec-banner">3. Roadmap Dekarbonisasi per Sektor (2025–2050)</div>', unsafe_allow_html=True)

b3_kiri, b3_kanan = st.columns(2, gap="medium")

# ---- KIRI: TABEL 3 (DERET TAHUNAN 2025–2030 UNTUK 4 SEKTOR) ----
with b3_kiri:
    with st.container(border=True):
        st.markdown('<div class="pill-title">Target Penurunan Emisi Tahunan per Sektor 2025–2030 (Tabel 3, Gg CO₂e)</div>', unsafe_allow_html=True)

        fig_t3 = go.Figure()
        for kol, wrn in [
            ("Energi (Final)", WARNA["hijau_utama"]),
            ("Pembangkit Listrik", WARNA["teal"]),
            ("Limbah", WARNA["emas"]),
            ("FOLU", WARNA["koral"]),
        ]:
            fig_t3.add_trace(go.Bar(
                x=df_t3["Tahun"],
                y=df_t3[kol],
                name=kol,
                marker_color=wrn,
                marker_cornerradius=4,
            ))
        fig_t3.add_trace(go.Scatter(
            x=df_t3["Tahun"],
            y=df_t3["TOTAL"],
            name="Total Target (Gg)",
            mode="lines+markers+text",
            text=[fmt_id(v) for v in df_t3["TOTAL"]],
            textposition="top center",
            line=dict(color="#0F172A", width=2.5),
        ))
        fig_t3.update_layout(barmode="stack", yaxis=dict(range=[0, max(df_t3["TOTAL"]) * 1.18]))
        fig_t3.update_xaxes(dtick=1)
        st.plotly_chart(tata_letak(fig_t3, "Gg CO₂e", 260), use_container_width=True, config={"displayModeBar": False})

        # Tabel Matriks Deret Tahun 2025-2030 (4 Sektor + Total)
        sektor_t3 = ["Energi (Final)", "Pembangkit Listrik", "Limbah", "FOLU", "TOTAL"]
        rows_t3 = []
        for s in sektor_t3:
            baris = {"Sektor": s}
            for _, r in df_t3.iterrows():
                baris[str(int(r["Tahun"]))] = fmt_id(r[s])
            awal = df_t3[s].iloc[0]
            akhir = df_t3[s].iloc[-1]
            baris["Perubahan (25→30)"] = ("+" if akhir >= awal else "−") + fmt_id(abs(akhir - awal))
            rows_t3.append(baris)
        st.dataframe(pd.DataFrame(rows_t3), hide_index=True, use_container_width=True)

# ---- KANAN: TABEL 5 (PROYEKSI 2019–2050 CPOS VS NZE UNTUK 4 SEKTOR) ----
with b3_kanan:
    with st.container(border=True):
        st.markdown('<div class="pill-title">Proyeksi Tingkat Emisi 2019–2050: Skenario CPOS vs NZE (Tabel 5, Gg CO₂e)</div>', unsafe_allow_html=True)

        pilihan_sektor_t5 = st.selectbox(
            "Pilih Sektor untuk Grafik Perbandingan CPOS vs NZE:",
            ["Total Seluruh Sektor", "Energi (Final) [Komersial+RT+Industri+Transportasi]", "Pembangkit", "Limbah", "FOLU"],
            index=0,
            label_visibility="collapsed",
        )
        peta_kol_t5 = {
            "Total Seluruh Sektor": ("Total_CPOS", "Total_NZE"),
            "Energi (Final) [Komersial+RT+Industri+Transportasi]": ("Energi (Final)_CPOS", "Energi (Final)_NZE"),
            "Pembangkit": ("Pembangkit_CPOS", "Pembangkit_NZE"),
            "Limbah": ("Limbah_CPOS", "Limbah_NZE"),
            "FOLU": ("FOLU_CPOS", "FOLU_NZE"),
        }
        kol_cpos, kol_nze = peta_kol_t5[pilihan_sektor_t5]
        x_thn_t5 = df_t5["Tahun"].astype(str)

        fig_t5 = go.Figure()
        fig_t5.add_trace(go.Scatter(
            x=x_thn_t5,
            y=df_t5[kol_cpos],
            name="Skenario CPOS (Kebijakan Berjalan)",
            mode="lines+markers+text",
            text=[fmt_id(v) for v in df_t5[kol_cpos]],
            textposition="top center",
            line=dict(color=WARNA["oranye"], width=3, dash="dash"),
        ))
        fig_t5.add_trace(go.Scatter(
            x=x_thn_t5,
            y=df_t5[kol_nze],
            name="Skenario NZE (Net Zero Emission)",
            mode="lines+markers+text",
            text=[fmt_id(v) for v in df_t5[kol_nze]],
            textposition="bottom center",
            fill="tonexty",
            fillcolor="rgba(21, 128, 61, 0.13)",
            line=dict(color=WARNA["hijau_utama"], width=3.5),
        ))
        maks_y5 = max(df_t5[kol_cpos].max(), df_t5[kol_nze].max())
        fig_t5 = tata_letak(fig_t5, "Gg CO₂e", 222)
        fig_t5.update_layout(yaxis=dict(range=[min(0, df_t5[kol_nze].min() * 1.2), maks_y5 * 1.18]))
        st.plotly_chart(fig_t5, use_container_width=True, config={"displayModeBar": False})

        # Tabel Perbandingan CPOS vs NZE (4 Sektor Gabungan + Total)
        rows_t5 = []
        for label_s, k_c, k_n in [
            ("Energi (Final)", "Energi (Final)_CPOS", "Energi (Final)_NZE"),
            ("Pembangkit Listrik", "Pembangkit_CPOS", "Pembangkit_NZE"),
            ("Limbah", "Limbah_CPOS", "Limbah_NZE"),
            ("FOLU", "FOLU_CPOS", "FOLU_NZE"),
            ("TOTAL EMISI", "Total_CPOS", "Total_NZE"),
        ]:
            r_2019 = df_t5[k_c].iloc[0]
            c_2035, n_2035 = df_t5[k_c].iloc[1], df_t5[k_n].iloc[1]
            c_2050, n_2050 = df_t5[k_c].iloc[-1], df_t5[k_n].iloc[-1]
            rows_t5.append({
                "Sektor (4 Kelompok)": label_s,
                "2019 (Ref)": fmt_id(r_2019),
                "2035 (CPOS | NZE)": f"{fmt_id(c_2035)} | {fmt_id(n_2035)}",
                "2050 (CPOS | NZE)": f"{fmt_id(c_2050)} | {fmt_id(n_2050)}",
                "Selisih NZE vs CPOS 2050": "−" + fmt_id(abs(c_2050 - n_2050)),
            })
        st.dataframe(pd.DataFrame(rows_t5), hide_index=True, use_container_width=True)

# ==========================================================
# BLOK 4: RINCIAN CAPAIAN 29 AKSI MITIGASI (TABEL 2 HALAMAN VIII–IX)
# ==========================================================
st.markdown(f'<div class="sec-banner">4. Rincian Capaian {len(df_ak)} Aksi Mitigasi ({thn_lap})</div>', unsafe_allow_html=True)

b4_kiri, b4_kanan = st.columns([1, 1.45], gap="medium")

with b4_kiri:
    with st.container(border=True):
        total_proyek_jt = df_ak["Reduksi_Ton"].sum() / 1e6
        st.markdown(
            f"""
            <div style="background:#F0FDF4;border:1px solid #BBF7D0;border-radius:12px;padding:12px 16px;margin-bottom:10px;">
                <div style="font-size:0.78rem;font-weight:700;color:#166534;text-transform:uppercase;">Total Capaian Penurunan Emisi</div>
                <div style="font-size:1.75rem;font-weight:800;color:#14532D;">{len(df_ak)} Aksi Mitigasi</div>
                <div style="font-size:0.84rem;color:#1E293B;">
                    Reduksi Sektoral: <b>{fmt_id(p_now['Reduksi_Sektoral_JtTon'], 2)} Jt Ton ({fmt_id(p_now['Persen_Reduksi_Sektoral'], 1)}%)</b><br>
                    Akumulasi Tabel 2 Proyek: <b>{fmt_id(total_proyek_jt, 2)} Jt Ton CO₂e</b>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.markdown('<div class="pill-title">Top 6 Aksi Mitigasi dengan Reduksi Tertinggi</div>', unsafe_allow_html=True)
        df_top_aksi = df_ak.sort_values("Reduksi_Ton", ascending=False).head(6)
        fig_ak = go.Figure(go.Bar(
            x=df_top_aksi["Reduksi_Ton"] / 1e6,
            y=df_top_aksi["Aksi Mitigasi"],
            orientation="h",
            marker_color=WARNA["hijau_utama"],
            marker_cornerradius=6,
            text=[f"<b>{fmt_id(v/1e6, 2)} Jt Ton</b>" for v in df_top_aksi["Reduksi_Ton"]],
            textposition="auto",
        ))
        fig_ak.update_layout(yaxis=dict(autorange="reversed"))
        st.plotly_chart(tata_letak(fig_ak, "Juta Ton CO₂e", 260, show_legend=False), use_container_width=True, config={"displayModeBar": False})

with b4_kanan:
    # 4 Kotak Sektor Rapi dalam Grid 2x2 Tanpa Terhimpit
    g_atas1, g_atas2 = st.columns(2, gap="small")
    g_bawah1, g_bawah2 = st.columns(2, gap="small")

    konfigurasi_sektor = [
        ("Energi", "⚡ Sektor Energi", WARNA["biru"], g_atas1),
        ("Transportasi", "🚌 Sektor Transportasi", WARNA["teal"], g_atas2),
        ("Limbah", "♻️ Sektor Limbah", WARNA["oranye"], g_bawah1),
        ("Kehutanan", "🌳 Sektor Kehutanan", WARNA["hijau_utama"], g_bawah2),
    ]

    for nama_s, judul_s, warna_s, kol_ui in konfigurasi_sektor:
        with kol_ui:
            with st.container(border=True):
                sub_df = df_ak[df_ak["Sektor"] == nama_s].sort_values("Reduksi_Ton", ascending=False)
                tot_s_ton = sub_df["Reduksi_Ton"].sum()
                label_tot = f"{fmt_id(tot_s_ton/1e6, 2)} Jt Ton" if tot_s_ton >= 1e5 else f"{fmt_id(tot_s_ton/1e3, 1)} Rb Ton"
                st.markdown(
                    f"""
                    <div class="aksi-header" style="background:{warna_s};">
                        <span>{judul_s} ({len(sub_df)} Aksi)</span>
                        <span>{label_tot}</span>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
                tampil_sub = pd.DataFrame({
                    "Aksi Mitigasi": sub_df["Aksi Mitigasi"],
                    "Reduksi (Ton)": sub_df["Reduksi_Ton"].map(lambda v: fmt_id(v, 0)),
                })
                st.dataframe(tampil_sub, hide_index=True, use_container_width=True, height=175)
