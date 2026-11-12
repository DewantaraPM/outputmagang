import io
import zipfile
import xml.etree.ElementTree as ET
from xml.sax.saxutils import escape
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
        padding-bottom: 3.5rem;
        max-width: 1280px;
    }
    div[data-testid="stVerticalBlockBorderWrapper"] {
        background-color: #FFFFFF;
        border-radius: 16px !important;
        border: 1px solid #D5E6DC !important;
        box-shadow: 0 4px 12px rgba(20, 83, 45, 0.05);
        padding: 6px;
    }
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
    .sec-banner {
        background: linear-gradient(90deg, #14532D 0%, #15803D 100%);
        color: #FFFFFF;
        padding: 9px 20px;
        border-radius: 12px;
        font-size: 1.02rem;
        font-weight: 800;
        letter-spacing: 0.03em;
        text-transform: uppercase;
        margin: 20px 0 12px 0;
        box-shadow: 0 4px 10px rgba(20, 83, 45, 0.12);
    }
    .pill-title {
        background: #14532D;
        color: #FFFFFF;
        font-size: 0.82rem;
        font-weight: 700;
        padding: 5px 14px;
        border-radius: 999px;
        display: inline-block;
        margin-bottom: 8px;
    }
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
    .stat-sub { font-size: 0.76rem; opacity: 0.92; margin-top: 4px; }
    .aksi-header {
        padding: 9px 14px;
        border-radius: 10px;
        color: #FFFFFF;
        font-weight: 700;
        font-size: 0.92rem;
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
    /* Tabel HTML Penuh Tanpa Scrollbar */
    .table-wrap {
        width: 100%;
        margin-top: 4px;
    }
    table.jkt-table {
        width: 100%;
        border-collapse: collapse;
        font-size: 0.83rem;
        color: #1E293B;
        background: #FFFFFF;
        border-radius: 10px;
        overflow: hidden;
        border: 1px solid #E2E8F0;
    }
    table.jkt-table thead th {
        background-color: #F0FDF4;
        color: #14532D;
        font-weight: 700;
        padding: 8px 10px;
        border-bottom: 2px solid #BBF7D0;
        font-size: 0.8rem;
    }
    table.jkt-table tbody td {
        padding: 7px 10px;
        border-bottom: 1px solid #EEF2F6;
        line-height: 1.38;
        vertical-align: top;
    }
    table.jkt-table tbody tr:nth-child(even) {
        background-color: #F8FAFC;
    }
    table.jkt-table tbody tr.row-total td {
        background-color: #DCFCE7 !important;
        color: #14532D;
        font-weight: 800;
        border-top: 1.5px solid #86EFAC;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


def fmt_id(x, d=0):
    if pd.isna(x):
        return "-"
    return f"{x:,.{d}f}".replace(",", "X").replace(".", ",").replace("X", ".")


def fmt_delta(val_baru, val_acuan, d=0, satuan=""):
    selisih = val_baru - val_acuan
    if abs(selisih) < 1e-4:
        return ""
    tanda = "+" if selisih > 0 else "−"
    return f'<span class="delta-pill">Δ {tanda}{fmt_id(abs(selisih), d)}{satuan}</span>'


def ke_angka(val, default=0.0):
    if pd.isna(val):
        return default
    if isinstance(val, (int, float)) and not isinstance(val, bool):
        return float(val)
    s = str(val).strip()
    if s in ["NE", "NO", "NA", "-", ""]:
        return default
    neg = False
    if s.startswith("(") and s.endswith(")"):
        neg = True
        s = s[1:-1].strip()
    if "," in s and "." not in s:
        s = s.replace(",", ".")
    elif "." in s and "," not in s:
        parts = s.split(".")
        if all(len(p) == 3 for p in parts[1:]):
            s = s.replace(".", "")
    try:
        v = float(s)
        return -v if neg else v
    except Exception:
        return default


def persingkat_aksi(nama):
    peta_singkat = {
        "Manajemen transportasi melalui penerapan sistem ITS": "Sistem ITS Transportasi",
        "Substitusi BBM ke gas di Pembangkit Muara Karang dan IP Tanjung Priok": "Substitusi Gas Pembangkit MK & Priok",
        "Substitusi BBM ke gas Pembangkit Muara Karang & Tanjung Priok": "Substitusi Gas Pembangkit MK & Priok",
        "Efisien energi di pembangkit Muara Karang": "Efisiensi Pembangkit Muara Karang",
        "Efisiensi energi di pembangkit Muara Karang": "Efisiensi Pembangkit Muara Karang",
        "Feeder busway": "Feeder Busway",
        "Penggunaan biofuel": "Biofuel Transportasi",
        "Penggunaan biofuel transportasi": "Biofuel Transportasi",
        "Busway": "Busway (BRT Transjakarta)",
        "Busway (BRT Transjakarta)": "Busway (BRT Transjakarta)",
        "Penggunaan LHE untuk lampu jalan": "Lampu Jalan Hemat Energi (LHE)",
        "Penggunaan LHE untuk lampu jalan (PJU)": "Lampu Jalan Hemat Energi (LHE)",
        "Penggunaan biofuel di sub sektor industri": "Biofuel Industri",
        "Penggunaan biofuel di subsektor industri": "Biofuel Industri",
        "Bus listrik": "Bus Listrik Transjakarta",
        "Kegiatan 3R kertas": "Kegiatan 3R Kertas",
        "Penggunaan kereta api Listrik (KRL)": "Kereta Api Listrik (KRL)",
        "Penerapan green building di gedung pemerintah dan komersial": "Green Building Gedung",
    }
    s = str(nama).strip()
    if s in peta_singkat:
        return peta_singkat[s]
    return s if len(s) <= 36 else s[:33] + "..."


def buat_tabel_html(df, rata_kanan_mulai=1, baris_total=False):
    ths = []
    for idx, col in enumerate(df.columns):
        align = "right" if idx >= rata_kanan_mulai else "left"
        ths.append(f'<th style="text-align:{align};">{escape(str(col))}</th>')
    thead = f"<thead><tr>{''.join(ths)}</tr></thead>"

    trs = []
    n_rows = len(df)
    for r_idx, row in enumerate(df.itertuples(index=False)):
        is_last_total = baris_total and (r_idx == n_rows - 1)
        tr_class = ' class="row-total"' if is_last_total else ""
        tds = []
        for c_idx, val in enumerate(row):
            align = "right" if c_idx >= rata_kanan_mulai else "left"
            nowrap = "white-space:nowrap;font-variant-numeric:tabular-nums;" if c_idx >= rata_kanan_mulai else ""
            tds.append(f'<td style="text-align:{align};{nowrap}">{escape(str(val))}</td>')
        trs.append(f"<tr{tr_class}>{''.join(tds)}</tr>")
    tbody = f"<tbody>{''.join(trs)}</tbody>"
    return f'<div class="table-wrap"><table class="jkt-table">{thead}{tbody}</table></div>'


def tata_letak(fig, y_title=None, tinggi=290, show_legend=True):
    fig.update_layout(
        template="plotly_white",
        font=dict(family=FONT, size=11.5, color="#1E293B"),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=8, r=12, t=28, b=8),
        height=tinggi,
        showlegend=show_legend,
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="left", x=0, title_text=""),
        hovermode="x unified",
        yaxis=dict(title=y_title, gridcolor="#E2E8F0", zerolinecolor="#CBD5E1"),
        xaxis=dict(showgrid=False),
    )
    return fig


# ==========================================================
# 2. ENGINE EXCEL (.XLSX) MURNI PYTHON (TANPA WAJIB OPENPYXL)
# ==========================================================
def _kol_huruf(n):
    s = ""
    while n >= 0:
        s = chr(n % 26 + 65) + s
        n = n // 26 - 1
    return s


def _df_ke_sheet_xml(df):
    baris_xml = []
    cols = list(df.columns)
    sel_header = [
        f'<c r="{_kol_huruf(c)}1" t="inlineStr"><is><t>{escape(str(k))}</t></is></c>'
        for c, k in enumerate(cols)
    ]
    baris_xml.append(f'<row r="1">{"".join(sel_header)}</row>')

    for r_idx, row in enumerate(df.itertuples(index=False), start=2):
        sel_data = []
        for c_idx, val in enumerate(row):
            ref = f"{_kol_huruf(c_idx)}{r_idx}"
            if pd.isna(val):
                continue
            if isinstance(val, (int, float)) and not isinstance(val, bool):
                sel_data.append(f'<c r="{ref}"><v>{val}</v></c>')
            else:
                sel_data.append(f'<c r="{ref}" t="inlineStr"><is><t>{escape(str(val))}</t></is></c>')
        baris_xml.append(f'<row r="{r_idx}">{"".join(sel_data)}</row>')

    return (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<worksheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main">'
        f'<sheetData>{"".join(baris_xml)}</sheetData></worksheet>'
    )


def konversi_ke_excel(daftar_sheet):
    buffer = io.BytesIO()
    try:
        with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
            for nama, df in daftar_sheet:
                df.to_excel(writer, sheet_name=nama, index=False)
        return buffer.getvalue()
    except Exception:
        buffer = io.BytesIO()
        with zipfile.ZipFile(buffer, "w", zipfile.ZIP_DEFLATED) as zf:
            overrides = "".join(
                f'<Override PartName="/xl/worksheets/sheet{i}.xml" '
                'ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.worksheet+xml"/>'
                for i in range(1, len(daftar_sheet) + 1)
            )
            zf.writestr(
                "[Content_Types].xml",
                '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
                '<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">'
                '<Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>'
                '<Default Extension="xml" ContentType="application/xml"/>'
                '<Override PartName="/xl/workbook.xml" '
                'ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet.main+xml"/>'
                f"{overrides}</Types>",
            )
            zf.writestr(
                "_rels/.rels",
                '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
                '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
                '<Relationship Id="rId1" '
                'Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" '
                'Target="xl/workbook.xml"/></Relationships>',
            )
            sheets_tag = "".join(
                f'<sheet name="{nama}" sheetId="{i}" r:id="rId{i}"/>'
                for i, (nama, _) in enumerate(daftar_sheet, start=1)
            )
            zf.writestr(
                "xl/workbook.xml",
                '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
                '<workbook xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main" '
                'xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships">'
                f"<sheets>{sheets_tag}</sheets></workbook>",
            )
            rels_tag = "".join(
                f'<Relationship Id="rId{i}" '
                'Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/worksheet" '
                f'Target="worksheets/sheet{i}.xml"/>'
                for i in range(1, len(daftar_sheet) + 1)
            )
            zf.writestr(
                "xl/_rels/workbook.xml.rels",
                '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
                '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
                f"{rels_tag}</Relationships>",
            )
            for i, (_, df) in enumerate(daftar_sheet, start=1):
                zf.writestr(f"xl/worksheets/sheet{i}.xml", _df_ke_sheet_xml(df))
        return buffer.getvalue()


def _indeks_kolom_ref(ref):
    huruf = "".join(ch for ch in ref if ch.isalpha())
    idx = 0
    for ch in huruf:
        idx = idx * 26 + (ord(ch.upper()) - 64)
    return idx - 1


def baca_excel_aman(uploaded_file):
    data_bytes = uploaded_file.getvalue()
    try:
        xls = pd.ExcelFile(io.BytesIO(data_bytes))
        return {nama: pd.read_excel(xls, nama) for nama in xls.sheet_names}
    except Exception:
        hasil = {}
        ns = {"a": "http://schemas.openxmlformats.org/spreadsheetml/2006/main"}
        with zipfile.ZipFile(io.BytesIO(data_bytes), "r") as zf:
            shared = []
            if "xl/sharedStrings.xml" in zf.namelist():
                root_ss = ET.fromstring(zf.read("xl/sharedStrings.xml"))
                for si in root_ss.findall("a:si", ns):
                    teks = "".join(t.text or "" for t in si.findall(".//a:t", ns))
                    shared.append(teks)

            wb_root = ET.fromstring(zf.read("xl/workbook.xml"))
            rels_root = ET.fromstring(zf.read("xl/_rels/workbook.xml.rels"))
            peta_target = {rel.attrib["Id"]: rel.attrib["Target"] for rel in rels_root}

            for sh in wb_root.findall(".//a:sheet", ns):
                nama = sh.attrib["name"]
                rid = sh.attrib.get("{http://schemas.openxmlformats.org/officeDocument/2006/relationships}id")
                target = peta_target.get(rid, "").lstrip("/")
                if not target.startswith("xl/"):
                    target = "xl/" + target
                ws_root = ET.fromstring(zf.read(target))
                rows_data = []
                for row_el in ws_root.findall(".//a:sheetData/a:row", ns):
                    row_dict = {}
                    for c_el in row_el.findall("a:c", ns):
                        col_idx = _indeks_kolom_ref(c_el.attrib.get("r", "A1"))
                        tipe = c_el.attrib.get("t", "")
                        if tipe == "inlineStr":
                            t_el = c_el.find(".//a:t", ns)
                            val = t_el.text if t_el is not None else ""
                        elif tipe == "s":
                            v_el = c_el.find("a:v", ns)
                            val = shared[int(v_el.text)] if v_el is not None and v_el.text else ""
                        else:
                            v_el = c_el.find("a:v", ns)
                            if v_el is not None and v_el.text is not None:
                                try:
                                    f_val = float(v_el.text)
                                    val = int(f_val) if f_val.is_integer() else f_val
                                except ValueError:
                                    val = v_el.text
                            else:
                                val = None
                        row_dict[col_idx] = val
                    rows_data.append(row_dict)
                if rows_data:
                    max_c = max(max(r.keys(), default=0) for r in rows_data)
                    headers = [rows_data[0].get(i, f"Col_{i}") for i in range(max_c + 1)]
                    isi = [[r.get(i, None) for i in range(max_c + 1)] for r in rows_data[1:]]
                    hasil[nama] = pd.DataFrame(isi, columns=headers)
        return hasil


# ==========================================================
# 3. DATA ACUAN RESMI (FORMAT MATRIKS RINGKASAN EKSEKUTIF)
# ==========================================================
@st.cache_data
def buat_data_acuan():
    tahun_kol = [str(y) for y in range(2010, 2026)]

    t2_ar2_rows = [
        ("1. Energi", [18822, 19570, 21120, 24023, 22662, 25559, 25781, 26485, 28354, 27665, 22779, 24885, 26715, 26919, 27669, 29311]),
        ("1A Aktivitas pembakaran bahan bakar", [18768, 19516, 21066, 23969, 22608, 25505, 25727, 26437, 28312, 27622, 22741, 24855, 26686, 26893, 27644, 29284]),
        ("1A1 Industri energi : Pembangkit listrik", [8044, 7785, 6843, 7521, 8010, 7737, 7227, 6673, 7938, 8744, 7301, 8530, 7217, 7443, 7803, 7128]),
        ("1A2 Industri Manufaktur", [2330, 2326, 2256, 2755, 1935, 2083, 2648, 3465, 3417, 2064, 2081, 2219, 2443, 1992, 2555, 2348]),
        ("1A3 Transportasi", [7258, 8201, 10722, 12453, 11424, 14102, 14293, 14671, 15325, 15364, 11903, 12642, 15543, 15992, 15806, 18293]),
        ("1A4 Lainnya (Komersial dan Residensial)", [1130, 1198, 1239, 1233, 1233, 1577, 1553, 1622, 1625, 1442, 1450, 1459, 1477, 1458, 1472, 1508]),
        ("1A4a Komersial", [90, 95, 99, 98, 98, 126, 124, 130, 130, 115, 116, 117, 118, 116, 117, 117]),
        ("1A4b Residensial (Rumah Tangga)", [1040, 1103, 1140, 1135, 1135, 1451, 1429, 1492, 1495, 1327, 1334, 1342, 1359, 1342, 1355, 1391]),
        ("1A5 Lain", [6, 6, 6, 6, 6, 6, 6, 6, 7, 7, 6, 6, 6, 7, 8, 7]),
        ("1B Emisi fugitive", [54, 54, 54, 54, 54, 54, 54, 48, 42, 43, 38, 30, 29, 25, 25, 28]),
        ("2. IPPU", ["NE"] * 16),
        ("3. AFOLU", [163, 187, 180, 184, 46, 39, 44, 51, 58, -14, -29, 38, -45, -60, -51, -40]),
        ("3A Peternakan", [1] * 16),
        ("3B Lahan*", [160, 185, 178, 182, 45, 38, 43, 49, 57, -16, -31, 37, -46, -61, -53, -41]),
        ("3C Sumber agregat dan emisi non CO2", [2, 1, 2, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0]),
        ("4. Limbah", [1873, 1837, 1746, 1845, 1915, 2000, 2083, 2199, 2284, 2305, 2396, 2450, 2478, 2369, 2362, 2444]),
        ("4A Pengelolaan limbah padat di TPA", [941, 892, 791, 886, 941, 1010, 1090, 1167, 1231, 1249, 1336, 1363, 1379, 1296, 1286, 1403]),
        ("4B Pengelolaan limbah padat secara biologis", ["-", 1.1, 1.1, 1.1, 1.1, 1.0, 1.0, 0.0, 0.1, 0.1, 0.1, 0.2, 0.2, 0.4, 0.2, 0.0]),
        ("4C Insinerasi dan pembakaran terbuka", ["-", "-", "-", "-", "-", "-", "-", 1, 1, "-", 0, 1, 1, 0.3, 0.1, 0.3]),
        ("4D Pengolahan limbah cair", [932, 944, 954, 958, 973, 989, 993, 1031, 1051, 1057, 1060, 1086, 1099, 1072, 1076, 1040]),
        ("Total emisi GRK direct", [20858, 21595, 23047, 26052, 24624, 27599, 27909, 28735, 30696, 29956, 25146, 27373, 29148, 29227, 29979, 31715]),
        ("Emisi GRK indirect", [19733, 21787, 24988, 29028, 26927, 29065, 30982, 28378, 29309, 30907, 29015, 29301, 31145, 33420, 34509, 34507]),
        ("Grand total emisi GRK (direct + indirect)", [40590, 43382, 48035, 55080, 51551, 56664, 58891, 57113, 60005, 60863, 54161, 56674, 60293, 62647, 64488, 66221]),
        ("Konsumsi Listrik PLN (GWh)", [21853, 24127, 27672, 32146, 29819, 32187, 34310, 31426, 32457, 34227, 32132, 32448, 34491, 37010, 38198, 38196]),
    ]
    df_ar2 = pd.DataFrame([[s] + v for s, v in t2_ar2_rows], columns=["Sektor"] + tahun_kol)

    t3_ar5_rows = [
        ("1. Energi", [18839, 19589, 21136, 24037, 22675, 25569, 25791, 26492, 28358, 27668, 22780, 24883, 26713, 26914, 27668, 29315]),
        ("1A Aktivitas pembakaran bahan bakar", [18770, 19520, 21067, 23967, 22606, 25500, 25721, 26431, 28304, 27613, 22731, 24845, 26676, 26881, 27635, 29278]),
        ("1A1 Industri energi: Pembangkit listrik", [8044, 7784, 6843, 7522, 8010, 7737, 7227, 6673, 7939, 8744, 7301, 8530, 7217, 7444, 7804, 7128]),
        ("1A2 Industri Manufaktur", [2330, 2326, 2256, 2755, 1935, 2083, 2648, 3465, 3417, 2064, 2081, 2219, 2442, 1992, 2555, 2348]),
        ("1A3 Transportasi", [7259, 8204, 10721, 12451, 11421, 14095, 14286, 14664, 15316, 15355, 11893, 12631, 15533, 15979, 15796, 18287]),
        ("1A4 Lainnya (Komersial dan Residensial)", [1130, 1199, 1240, 1234, 1234, 1578, 1554, 1622, 1625, 1443, 1450, 1460, 1478, 1459, 1473, 1509]),
        ("1A5 Lain", [6, 6, 6, 6, 6, 6, 6, 6, 7, 7, 6, 6, 6, 7, 8, 7]),
        ("1B Emisi fugitive", [69, 69, 69, 69, 69, 69, 69, 62, 54, 55, 48, 38, 37, 32, 32, 36]),
        ("2. IPPU", ["NE"] * 16),
        ("3. AFOLU", [163, 188, 181, 185, 47, 39, 45, 51, 59, -14, -29, 38, -45, -60, -51, -40]),
        ("3A Peternakan", [1] * 16),
        ("3B Lahan*", [160, 185, 178, 182, 45, 38, 43, 49, 57, -16, -31, 37, -46, -61, -53, -41]),
        ("3C Sumber agregat dan emisi non-CO2", [2, 2, 2, 2, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0]),
        ("4. Limbah", [2444, 2395, 2270, 2405, 2494, 2608, 2720, 2865, 2973, 3004, 3126, 3196, 3236, 3088, 3078, 3186]),
        ("4A Pengelolaan limbah padat di TPA", [1255, 1189, 1054, 1181, 1255, 1346, 1453, 1556, 1642, 1665, 1782, 1817, 1838, 1728, 1714, 1870]),
        ("4B Pengelolaan limbah padat secara biologis", ["-", 0.9, 0.9, 0.9, 0.9, 0.9, 0.8, 0.0, 0.1, 0.1, 0.1, 0.1, 0.1, 0.3, 0.2, 0.0]),
        ("4C Insinerasi dan pembakaran terbuka", ["-", "-", "-", "-", "-", "-", "-", 1, 1, "-", 0, 1, 1, 0, 0, 0]),
        ("4D Pengolahan limbah cair", [1189, 1205, 1214, 1223, 1238, 1261, 1266, 1308, 1330, 1339, 1344, 1378, 1397, 1360, 1364, 1315]),
        ("Total emisi GRK direct", [21446, 22171, 23586, 26626, 25216, 28216, 28555, 29408, 31390, 30658, 25876, 28118, 29905, 29942, 30694, 32461]),
        ("Emisi GRK indirect", [19733, 21787, 24988, 29028, 26927, 29065, 30982, 28378, 29309, 30907, 29015, 29301, 31145, 33420, 34509, 34507]),
        ("Grand total emisi GRK (direct + indirect)", [41179, 43959, 48574, 55654, 52143, 57281, 59536, 57787, 60699, 61565, 54891, 57419, 61050, 63362, 65204, 66967]),
    ]
    df_ar5 = pd.DataFrame([[s] + v for s, v in t3_ar5_rows], columns=["Sektor"] + tahun_kol)

    df_aksi = pd.DataFrame([
        {"Sektor": "Energi", "Aksi Mitigasi": "Efisien energi di pembangkit Muara Karang", "Tingkat emisi baseline (Ton CO₂e)": 4197637, "Tingkat emisi mitigasi (Ton CO₂e)": 2936879, "Penurunan emisi (Ton CO₂e)": 1260758},
        {"Sektor": "Energi", "Aksi Mitigasi": "Penggunaan PLTS rooftop di gedung pemerintahan, sekolah, komersial, industri, rumah tangga dan PLTS komunal", "Tingkat emisi baseline (Ton CO₂e)": 20678, "Tingkat emisi mitigasi (Ton CO₂e)": 0, "Penurunan emisi (Ton CO₂e)": 20678},
        {"Sektor": "Energi", "Aksi Mitigasi": "Energi bersih: PLTSa dan pembangkit listrik berbahan bakar LFG", "Tingkat emisi baseline (Ton CO₂e)": 9036, "Tingkat emisi mitigasi (Ton CO₂e)": 847, "Penurunan emisi (Ton CO₂e)": 8189},
        {"Sektor": "Energi", "Aksi Mitigasi": "Substitusi BBM ke gas di Pembangkit Muara Karang dan IP Tanjung Priok", "Tingkat emisi baseline (Ton CO₂e)": 10460482, "Tingkat emisi mitigasi (Ton CO₂e)": 7161905, "Penurunan emisi (Ton CO₂e)": 3298577},
        {"Sektor": "Energi", "Aksi Mitigasi": "Penggunaan biofuel di sub sektor industri", "Tingkat emisi baseline (Ton CO₂e)": 372543, "Tingkat emisi mitigasi (Ton CO₂e)": 225976, "Penurunan emisi (Ton CO₂e)": 146566},
        {"Sektor": "Energi", "Aksi Mitigasi": "Penggunaan biofuel di sub sektor komersial", "Tingkat emisi baseline (Ton CO₂e)": 24280, "Tingkat emisi mitigasi (Ton CO₂e)": 14728, "Penurunan emisi (Ton CO₂e)": 9552},
        {"Sektor": "Energi", "Aksi Mitigasi": "Penerapan green building di gedung pemerintah dan komersial", "Tingkat emisi baseline (Ton CO₂e)": 661638, "Tingkat emisi mitigasi (Ton CO₂e)": 575090, "Penurunan emisi (Ton CO₂e)": 86547},
        {"Sektor": "Energi", "Aksi Mitigasi": "Penggunaan LHE untuk lampu jalan", "Tingkat emisi baseline (Ton CO₂e)": 603905, "Tingkat emisi mitigasi (Ton CO₂e)": 334548, "Penurunan emisi (Ton CO₂e)": 269357},
        {"Sektor": "Energi", "Aksi Mitigasi": "Penggunaan PJU TS", "Tingkat emisi baseline (Ton CO₂e)": 113, "Tingkat emisi mitigasi (Ton CO₂e)": 0, "Penurunan emisi (Ton CO₂e)": 113},
        {"Sektor": "Energi", "Aksi Mitigasi": "Pemadaman Listrik berkala", "Tingkat emisi baseline (Ton CO₂e)": 366, "Tingkat emisi mitigasi (Ton CO₂e)": 0, "Penurunan emisi (Ton CO₂e)": 366},
        {"Sektor": "Transportasi", "Aksi Mitigasi": "Manajemen transportasi melalui penerapan sistem ITS", "Tingkat emisi baseline (Ton CO₂e)": 67670762, "Tingkat emisi mitigasi (Ton CO₂e)": 58883095, "Penurunan emisi (Ton CO₂e)": 8787667},
        {"Sektor": "Transportasi", "Aksi Mitigasi": "Busway", "Tingkat emisi baseline (Ton CO₂e)": 451139, "Tingkat emisi mitigasi (Ton CO₂e)": 49028, "Penurunan emisi (Ton CO₂e)": 402366},
        {"Sektor": "Transportasi", "Aksi Mitigasi": "Feeder busway", "Tingkat emisi baseline (Ton CO₂e)": 1190711, "Tingkat emisi mitigasi (Ton CO₂e)": 206661, "Penurunan emisi (Ton CO₂e)": 966073},
        {"Sektor": "Transportasi", "Aksi Mitigasi": "Penggunaan kereta api Listrik (KRL)", "Tingkat emisi baseline (Ton CO₂e)": 245318, "Tingkat emisi mitigasi (Ton CO₂e)": 144691, "Penurunan emisi (Ton CO₂e)": 100627},
        {"Sektor": "Transportasi", "Aksi Mitigasi": "Penggunaan MRT", "Tingkat emisi baseline (Ton CO₂e)": 16295, "Tingkat emisi mitigasi (Ton CO₂e)": 6143, "Penurunan emisi (Ton CO₂e)": 10153},
        {"Sektor": "Transportasi", "Aksi Mitigasi": "Penggunaan LRT", "Tingkat emisi baseline (Ton CO₂e)": 9843, "Tingkat emisi mitigasi (Ton CO₂e)": 3000, "Penurunan emisi (Ton CO₂e)": 6844},
        {"Sektor": "Transportasi", "Aksi Mitigasi": "Penggunaan biofuel", "Tingkat emisi baseline (Ton CO₂e)": 1974534, "Tingkat emisi mitigasi (Ton CO₂e)": 1262427, "Penurunan emisi (Ton CO₂e)": 712107},
        {"Sektor": "Transportasi", "Aksi Mitigasi": "Penggunaan BBG", "Tingkat emisi baseline (Ton CO₂e)": 70194, "Tingkat emisi mitigasi (Ton CO₂e)": 56951, "Penurunan emisi (Ton CO₂e)": 13243},
        {"Sektor": "Transportasi", "Aksi Mitigasi": "Bus listrik", "Tingkat emisi baseline (Ton CO₂e)": 183134, "Tingkat emisi mitigasi (Ton CO₂e)": 38150, "Penurunan emisi (Ton CO₂e)": 144984},
        {"Sektor": "Transportasi", "Aksi Mitigasi": "Car Free Day", "Tingkat emisi baseline (Ton CO₂e)": 7029, "Tingkat emisi mitigasi (Ton CO₂e)": 0, "Penurunan emisi (Ton CO₂e)": 7029},
        {"Sektor": "Limbah", "Aksi Mitigasi": "LFG Recovery di TPA Bantar Gebang", "Tingkat emisi baseline (Ton CO₂e)": 1574250, "Tingkat emisi mitigasi (Ton CO₂e)": 1537203, "Penurunan emisi (Ton CO₂e)": 37352},
        {"Sektor": "Limbah", "Aksi Mitigasi": "Pengomposan sampah organik", "Tingkat emisi baseline (Ton CO₂e)": 1574250, "Tingkat emisi mitigasi (Ton CO₂e)": 1565718, "Penurunan emisi (Ton CO₂e)": 8837},
        {"Sektor": "Limbah", "Aksi Mitigasi": "Kegiatan 3R kertas", "Tingkat emisi baseline (Ton CO₂e)": 1574250, "Tingkat emisi mitigasi (Ton CO₂e)": 1465372, "Penurunan emisi (Ton CO₂e)": 109183},
        {"Sektor": "Limbah", "Aksi Mitigasi": "PLTSa dan RDF serta Pemanfaatan/pengolahan lain (maggot, pakan, biodigester, dan sumber energi lainnya)", "Tingkat emisi baseline (Ton CO₂e)": 1574250, "Tingkat emisi mitigasi (Ton CO₂e)": 1558827, "Penurunan emisi (Ton CO₂e)": 15727},
        {"Sektor": "Limbah", "Aksi Mitigasi": "Landfill Mining", "Tingkat emisi baseline (Ton CO₂e)": 1574250, "Tingkat emisi mitigasi (Ton CO₂e)": 1574269, "Penurunan emisi (Ton CO₂e)": 285},
        {"Sektor": "Limbah", "Aksi Mitigasi": "Pengolahan limbah cair on-site (IPAL)", "Tingkat emisi baseline (Ton CO₂e)": 1083405, "Tingkat emisi mitigasi (Ton CO₂e)": 1078576, "Penurunan emisi (Ton CO₂e)": 4829},
        {"Sektor": "Limbah", "Aksi Mitigasi": "Pengolahan limbah cair off-site (IPLT)", "Tingkat emisi baseline (Ton CO₂e)": 1083405, "Tingkat emisi mitigasi (Ton CO₂e)": 1082747, "Penurunan emisi (Ton CO₂e)": 658},
        {"Sektor": "Kehutanan", "Aksi Mitigasi": "Penanaman/Penghijauan", "Tingkat emisi baseline (Ton CO₂e)": 40967, "Tingkat emisi mitigasi (Ton CO₂e)": 39043, "Penurunan emisi (Ton CO₂e)": 1924},
        {"Sektor": "Kehutanan", "Aksi Mitigasi": "Konservasi Hutan Mangrove (HL Angke Kapuk)", "Tingkat emisi baseline (Ton CO₂e)": 40967, "Tingkat emisi mitigasi (Ton CO₂e)": 34803, "Penurunan emisi (Ton CO₂e)": 6164},
    ])

    df_tren = pd.DataFrame({
        "Tahun": list(range(2015, 2031)),
        "Baseline_JtTon": [63.0, 64.0, 65.0, 69.0, 73.0, 73.3, 78.0, 81.0, 85.0, 88.0, 92.0, 94.0, 98.0, 100.0, 103.0, 107.0],
        "Inventori_JtTon": [56.7, 58.9, 57.1, 60.0, 60.9, 54.2, 56.7, 60.3, 62.6, 64.5, 66.2, None, None, None, None, None],
    })

    df_tabel3 = pd.DataFrame({
        "Tahun": [2025, 2026, 2027, 2028, 2029, 2030],
        "Energi (Final)": [12198, 14268, 16414, 18638, 20943, 23305],
        "Pembangkit Listrik": [8471, 8251, 8546, 8775, 8995, 9170],
        "Limbah": [416, 632, 803, 1085, 1316, 1598],
        "FOLU": [29, 26, 23, 20, 18, 16],
        "TOTAL": [21114, 23178, 25789, 28521, 31235, 34090],
    })

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

    return df_ar2, df_ar5, df_aksi, df_tren, df_tabel3, df_tabel5


def ekstrak_profil_dari_matriks(df_ar2, df_ar5, df_tren):
    col_sektor = df_ar2.columns[0]
    tahun_cols = [str(c).strip() for c in df_ar2.columns[1:] if str(c).strip().isdigit()]
    thn_terbaru = tahun_cols[-1] if tahun_cols else "2025"

    map_ar2 = {}
    for _, r in df_ar2.iterrows():
        k = str(r[col_sektor]).strip()
        map_ar2[k] = ke_angka(r.get(thn_terbaru, r.iloc[-1]))

    col_sektor5 = df_ar5.columns[0]
    map_ar5 = {}
    for _, r in df_ar5.iterrows():
        k = str(r[col_sektor5]).strip()
        map_ar5[k] = ke_angka(r.get(thn_terbaru, r.iloc[-1]))

    def cari_nilai(m, kata_kunci, default=0.0):
        for k, v in m.items():
            if kata_kunci.lower() in k.lower():
                return v
        return default

    gt_ar2 = cari_nilai(map_ar2, "Grand total", 66221)
    gt_ar5 = cari_nilai(map_ar5, "Grand total", 66967)
    dir_ar2 = cari_nilai(map_ar2, "Total emisi GRK direct", 31715)
    dir_ar5 = cari_nilai(map_ar5, "Total emisi GRK direct", 32461)
    ind_val = cari_nilai(map_ar2, "Emisi GRK indirect", 34507)
    gwh_val = cari_nilai(map_ar2, "Konsumsi Listrik", 38196)

    energi_ar2 = cari_nilai(map_ar2, "1. Energi", 29311)
    limbah_ar2 = cari_nilai(map_ar2, "4. Limbah", 2444)
    afolu_ar2 = cari_nilai(map_ar2, "3. AFOLU", -40)

    top1_trans = cari_nilai(map_ar2, "1A3 Transportasi", 18293)
    top2_pemb = cari_nilai(map_ar2, "1A1 Industri energi", 7128)
    top3_ind = cari_nilai(map_ar2, "1A2 Industri Manufaktur", 2348)
    top4_tpa = cari_nilai(map_ar2, "4A Pengelolaan limbah padat", 1403)
    if any("1A4b" in k for k in map_ar2.keys()):
        top5_res = cari_nilai(map_ar2, "1A4b", 1391)
    else:
        val_1a4 = cari_nilai(map_ar2, "1A4 Lainnya", 1508)
        top5_res = 1391 if val_1a4 == 1508 else val_1a4

    df_tr_valid = df_tren.dropna(subset=[df_tren.columns[2]])
    if not df_tr_valid.empty:
        bau_last = ke_angka(df_tr_valid.iloc[-1, 1], 92.0)
        inv_last = ke_angka(df_tr_valid.iloc[-1, 2], 66.2)
        red_jt = round(bau_last - inv_last, 2)
        red_pct = round((red_jt / bau_last) * 100.0, 1) if bau_last else 28.0
    else:
        red_jt, red_pct = 25.80, 28.0

    return {
        "Tahun_Laporan": int(thn_terbaru),
        "Grand_Total_AR2": gt_ar2,
        "Grand_Total_AR5": gt_ar5,
        "Total_Direct_AR2": dir_ar2,
        "Total_Direct_AR5": dir_ar5,
        "Total_Indirect_Listrik": ind_val,
        "Konsumsi_Listrik_GWh": gwh_val,
        "Direct_Energi": energi_ar2,
        "Direct_Limbah": limbah_ar2,
        "Direct_AFOLU": afolu_ar2,
        "Top1_Transportasi": top1_trans,
        "Top2_Pembangkit": top2_pemb,
        "Top3_Industri": top3_ind,
        "Top4_Limbah_TPA": top4_tpa,
        "Top5_Residensial": top5_res,
        "Reduksi_Sektoral_JtTon": red_jt,
        "Persen_Reduksi_Sektoral": red_pct,
    }


df_ar2_base, df_ar5_base, df_ak_base, df_tr_base, df_t3_base, df_t5_base = buat_data_acuan()
DAFTAR_SHEET_ACUAN = [
    ("1_Profil_Emisi_AR2", df_ar2_base),
    ("2_Profil_Emisi_AR5", df_ar5_base),
    ("3_Capaian_Aksi_Mitigasi_2025", df_ak_base),
    ("4_Tren_Baseline_Inventori", df_tr_base),
    ("5_Target_2025_2030", df_t3_base),
    ("6_Proyeksi_2035_2050", df_t5_base),
]

# ==========================================================
# 4. HEADER UTAMA & PANEL UNDUH / UNGGAH EXCEL TAHUNAN
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
    u1, u2, u3 = st.columns([1.15, 1.35, 1], gap="medium")
    with u1:
        st.markdown("**1. Unduh Spreadsheet Acuan**")
        st.caption("Berisi 6 sheet dengan format tabel matriks persis seperti Ringkasan Eksekutif Laporan 2026.")
        file_excel_acuan = konversi_ke_excel(DAFTAR_SHEET_ACUAN)
        st.download_button(
            "📥 Unduh Template Excel Acuan (.xlsx)",
            data=file_excel_acuan,
            file_name="Data_Acuan_IGRK_DKI_2026.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True,
        )
    with u2:
        st.markdown("**2. Unggah Spreadsheet yang Telah Diedit**")
        uploaded_excel = st.file_uploader("Pilih file .xlsx hasil edit:", type=["xlsx", "xlsm"], label_visibility="collapsed")
    with u3:
        st.markdown("**3. Mode Tampilan Pembanding**")
        tampilkan_delta = st.toggle("Tampilkan Selisih (Δ) vs Data Acuan", value=True)
        if uploaded_excel is not None:
            st.success("✅ Data berhasil diperbarui dari file Excel yang diunggah!")
        else:
            st.info("ℹ️ Menampilkan Data Acuan Bawaan (Laporan 2026).")

if uploaded_excel is not None:
    try:
        sheets_dict = baca_excel_aman(uploaded_excel)
        df_ar2 = sheets_dict.get("1_Profil_Emisi_AR2", df_ar2_base)
        df_ar5 = sheets_dict.get("2_Profil_Emisi_AR5", df_ar5_base)
        df_ak = sheets_dict.get("3_Capaian_Aksi_Mitigasi_2025", sheets_dict.get("5_Aksi_Mitigasi", df_ak_base))
        df_tr = sheets_dict.get("4_Tren_Baseline_Inventori", sheets_dict.get("2_Tren_Historis", df_tr_base))
        df_t3 = sheets_dict.get("5_Target_2025_2030", sheets_dict.get("3_Target_2025_2030", df_t3_base))
        df_t5 = sheets_dict.get("6_Proyeksi_2035_2050", sheets_dict.get("4_Proyeksi_2035_2050", df_t5_base))
    except Exception as e:
        st.error(f"Format sheet tidak sesuai template: {e}. Menggunakan data acuan bawaan.")
        df_ar2, df_ar5, df_ak, df_tr, df_t3, df_t5 = df_ar2_base, df_ar5_base, df_ak_base, df_tr_base, df_t3_base, df_t5_base
else:
    df_ar2, df_ar5, df_ak, df_tr, df_t3, df_t5 = df_ar2_base, df_ar5_base, df_ak_base, df_tr_base, df_t3_base, df_t5_base

p_ref = ekstrak_profil_dari_matriks(df_ar2_base, df_ar5_base, df_tr_base)
p_now = ekstrak_profil_dari_matriks(df_ar2, df_ar5, df_tr)
thn_lap = int(p_now.get("Tahun_Laporan", 2025))

kol_reduksi_ak = "Penurunan emisi (Ton CO₂e)" if "Penurunan emisi (Ton CO₂e)" in df_ak.columns else df_ak.columns[-1]
df_ak[kol_reduksi_ak] = df_ak[kol_reduksi_ak].map(ke_angka)

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

    porsi_dir = (dir_ar2 / gt_ar2) * 100.0 if gt_ar2 else 0.0
    porsi_ind = (ind_val / gt_ar2) * 100.0 if gt_ar2 else 0.0

    # Persentase Energi, Limbah, dan AFOLU pada Emisi Direct kini 100% dinamis mengikuti Excel baru
    p_energi_dir = (p_now["Direct_Energi"] / dir_ar2) * 100.0 if dir_ar2 else 0.0
    p_limbah_dir = (p_now["Direct_Limbah"] / dir_ar2) * 100.0 if dir_ar2 else 0.0
    p_afolu_dir = (p_now["Direct_AFOLU"] / dir_ar2) * 100.0 if dir_ar2 else 0.0

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
            <div class="stat-sub">
                Energi: {fmt_id(p_now['Direct_Energi'])} Gg ({fmt_id(p_energi_dir, 0)}%) | 
                Limbah: {fmt_id(p_now['Direct_Limbah'])} Gg ({fmt_id(p_limbah_dir, 0)}%) | 
                AFOLU: {fmt_id(p_now['Direct_AFOLU'])} Gg ({fmt_id(p_afolu_dir, 1)}%)
            </div>
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
        st.plotly_chart(tata_letak(fig_top5, "Gg CO₂e", 265, show_legend=False), use_container_width=True, config={"displayModeBar": False})

# ==========================================================
# BLOK 2: TREN & KONTRIBUSI EMISI GRK (2015–2030)
# ==========================================================
st.markdown('<div class="sec-banner">2. Tren & Kontribusi Sumber Emisi GRK</div>', unsafe_allow_html=True)

b2_kiri, b2_kanan = st.columns([1.02, 1.38], gap="medium")

with b2_kiri:
    with st.container(border=True):
        st.markdown(f'<div class="pill-title">Kontribusi Sumber Emisi ({thn_lap})</div>', unsafe_allow_html=True)
        d1, d2 = st.columns(2)
        with d1:
            non_pembangkit = max(0.0, p_now["Direct_Energi"] - p_now["Top2_Pembangkit"])
            vals_pie1 = [ind_val, non_pembangkit, p_now["Top2_Pembangkit"], p_now["Direct_Limbah"]]
            tot_p1 = sum(vals_pie1) if sum(vals_pie1) > 0 else 1.0
            lbls_pie1 = [
                f"Listrik Indirect ({ind_val/tot_p1*100:.1f}%)",
                f"Direct Non-Pembangkit ({non_pembangkit/tot_p1*100:.1f}%)",
                f"Pembangkit Listrik ({p_now['Top2_Pembangkit']/tot_p1*100:.1f}%)",
                f"Limbah ({p_now['Direct_Limbah']/tot_p1*100:.1f}%)",
            ]
            fig_pie1 = go.Figure(go.Pie(
                labels=lbls_pie1,
                values=vals_pie1,
                hole=0.62,
                marker=dict(colors=[WARNA["biru"], WARNA["oranye"], WARNA["hijau_utama"], "#8B5CF6"]),
                textinfo="percent",
                textposition="inside",
                insidetextorientation="horizontal",
                sort=False,
            ))
            fig_pie1.update_layout(
                annotations=[dict(text=f"<b>Total</b><br>{fmt_id(gt_ar2)}<br>Gg", x=0.5, y=0.5, font_size=11.5, showarrow=False)],
                margin=dict(l=6, r=6, t=10, b=95),
                height=295,
                paper_bgcolor="rgba(0,0,0,0)",
                legend=dict(orientation="h", yanchor="top", y=-0.06, xanchor="center", x=0.5, font=dict(size=10)),
            )
            st.plotly_chart(fig_pie1, use_container_width=True, config={"displayModeBar": False})
        with d2:
            vals_pie2 = [p_now["Direct_Energi"], p_now["Direct_Limbah"]]
            tot_p2 = sum(vals_pie2) if sum(vals_pie2) > 0 else 1.0
            lbls_pie2 = [
                f"Energi ({p_now['Direct_Energi']/tot_p2*100:.1f}%)",
                f"Limbah ({p_now['Direct_Limbah']/tot_p2*100:.1f}%)",
            ]
            fig_pie2 = go.Figure(go.Pie(
                labels=lbls_pie2,
                values=vals_pie2,
                hole=0.62,
                marker=dict(colors=[WARNA["biru"], WARNA["oranye"]]),
                textinfo="percent",
                textposition="inside",
                insidetextorientation="horizontal",
                sort=False,
            ))
            fig_pie2.update_layout(
                annotations=[dict(text=f"<b>Direct</b><br>{fmt_id(dir_ar2)}<br>Gg", x=0.5, y=0.5, font_size=11.5, showarrow=False)],
                margin=dict(l=6, r=6, t=10, b=95),
                height=295,
                paper_bgcolor="rgba(0,0,0,0)",
                legend=dict(orientation="h", yanchor="top", y=-0.06, xanchor="center", x=0.5, font=dict(size=10.5)),
            )
            st.plotly_chart(fig_pie2, use_container_width=True, config={"displayModeBar": False})
        st.caption(f"Catatan: Sektor AFOLU mencatat serapan bersih sebesar **{fmt_id(p_now['Direct_AFOLU'])} Gg CO₂e ({fmt_id(p_afolu_dir, 1)}%)**.")

with b2_kanan:
    with st.container(border=True):
        st.markdown('<div class="pill-title">Tren Baseline vs Inventori Aktual (2015–2030)</div>', unsafe_allow_html=True)
        fig_tr = go.Figure()
        df_tr_valid = df_tr.dropna(subset=["Inventori_JtTon"]).copy()
        df_tr_valid["Inventori_Num"] = df_tr_valid["Inventori_JtTon"].map(ke_angka)
        df_tr["Baseline_Num"] = df_tr["Baseline_JtTon"].map(ke_angka)

        fig_tr.add_trace(go.Bar(
            x=df_tr_valid["Tahun"],
            y=df_tr_valid["Inventori_Num"],
            name="Realisasi Inventori (Juta Ton)",
            marker_color=WARNA["hijau_utama"],
            marker_cornerradius=4,
            text=[fmt_id(v, 1) for v in df_tr_valid["Inventori_Num"]],
            textposition="inside",
            insidetextanchor="end",
            textfont=dict(color="#FFFFFF", size=10, family=FONT),
        ))
        fig_tr.add_trace(go.Scatter(
            x=df_tr["Tahun"],
            y=df_tr["Baseline_Num"],
            name="Tingkat Emisi Baseline",
            mode="lines+markers+text",
            text=[fmt_id(v, 0) if float(v).is_integer() else fmt_id(v, 1) for v in df_tr["Baseline_Num"]],
            textposition="top center",
            textfont=dict(color=WARNA["koral"], size=10, family=FONT),
            line=dict(color=WARNA["koral"], width=2.5, dash="dash"),
        ))
        fig_tr.update_xaxes(dtick=1)
        fig_tr = tata_letak(fig_tr, "Juta Ton CO₂e", 255)
        fig_tr.update_layout(yaxis=dict(range=[0, max(df_tr["Baseline_Num"]) * 1.18]))
        st.plotly_chart(fig_tr, use_container_width=True, config={"displayModeBar": False})

        bau_now = ke_angka(df_tr_valid["Baseline_JtTon"].iloc[-1], 92.0)
        inv_now = ke_angka(df_tr_valid["Inventori_JtTon"].iloc[-1], 66.2)
        red_jt = p_now["Reduksi_Sektoral_JtTon"]
        red_pct = p_now["Persen_Reduksi_Sektoral"]
        st.markdown(
            f"""
            <div style="display:grid;grid-template-columns:repeat(3,1fr);gap:8px;margin-top:6px;">
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
# BLOK 3: ROADMAP DEKARBONISASI PER SEKTOR (2025–2050)
# Disusun ke bawah agar setiap tabel tampil 100% utuh tanpa scroll
# ==========================================================
st.markdown('<div class="sec-banner">3. Roadmap Dekarbonisasi per Sektor (2025–2050)</div>', unsafe_allow_html=True)

# ---- SUB-BLOK 3A: TABEL 3 (TARGET REDUKSI TAHUNAN 2025–2030) ----
with st.container(border=True):
    st.markdown('<div class="pill-title">3A. Target Penurunan Emisi Tahunan per Sektor 2025–2030 (Tabel 3, Gg CO₂e)</div>', unsafe_allow_html=True)
    t3_kiri, t3_kanan = st.columns([1.15, 1], gap="medium")

    with t3_kiri:
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
        st.plotly_chart(tata_letak(fig_t3, "Gg CO₂e", 250), use_container_width=True, config={"displayModeBar": False})

    with t3_kanan:
        sektor_t3 = ["Energi (Final)", "Pembangkit Listrik", "Limbah", "FOLU", "TOTAL"]
        rows_t3 = []
        for s in sektor_t3:
            baris = {"Sektor": s}
            for _, r in df_t3.iterrows():
                baris[str(int(r["Tahun"]))] = fmt_id(r[s])
            rows_t3.append(baris)
        df_tampil_t3 = pd.DataFrame(rows_t3)
        st.markdown(buat_tabel_html(df_tampil_t3, rata_kanan_mulai=1, baris_total=True), unsafe_allow_html=True)

# ---- SUB-BLOK 3B: TABEL 5 (PROYEKSI TINGKAT EMISI 2019–2050 CPOS VS NZE) ----
with st.container(border=True):
    st.markdown('<div class="pill-title">3B. Proyeksi Tingkat Emisi 2019–2050: Skenario CPOS vs NZE (Tabel 5, Gg CO₂e)</div>', unsafe_allow_html=True)

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
    fig_t5 = tata_letak(fig_t5, "Gg CO₂e", 262)
    fig_t5.update_layout(yaxis=dict(range=[min(0, df_t5[kol_nze].min() * 1.2), maks_y5 * 1.18]))
    st.plotly_chart(fig_t5, use_container_width=True, config={"displayModeBar": False})

    rows_t5 = []
    for label_s, k_c, k_n in [
        ("Energi (Final)", "Energi (Final)_CPOS", "Energi (Final)_NZE"),
        ("Pembangkit Listrik", "Pembangkit_CPOS", "Pembangkit_NZE"),
        ("Limbah", "Limbah_CPOS", "Limbah_NZE"),
        ("FOLU", "FOLU_CPOS", "FOLU_NZE"),
        ("TOTAL EMISI", "Total_CPOS", "Total_NZE"),
    ]:
        r_2019 = ke_angka(df_t5[k_c].iloc[0])
        c_2035, n_2035 = ke_angka(df_t5[k_c].iloc[1]), ke_angka(df_t5[k_n].iloc[1])
        c_2050, n_2050 = ke_angka(df_t5[k_c].iloc[-1]), ke_angka(df_t5[k_n].iloc[-1])
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
        total_proyek_jt = df_ak[kol_reduksi_ak].sum() / 1e6
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
        df_top_aksi = df_ak.sort_values(kol_reduksi_ak, ascending=False).head(6)
        fig_ak = go.Figure(go.Bar(
            x=df_top_aksi[kol_reduksi_ak] / 1e6,
            y=df_top_aksi["Aksi Mitigasi"],
            orientation="h",
            marker_color=WARNA["hijau_utama"],
            marker_cornerradius=6,
            text=[f"<b>{fmt_id(v/1e6, 2)} Jt Ton</b>" for v in df_top_aksi[kol_reduksi_ak]],
            textposition="auto",
        ))
        fig_ak.update_layout(yaxis=dict(autorange="reversed"))
        st.plotly_chart(tata_letak(fig_ak, "Juta Ton CO₂e", 260, show_legend=False), use_container_width=True, config={"displayModeBar": False})

with b4_kanan:
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
                sub_df = df_ak[df_ak["Sektor"] == nama_s].sort_values(kol_reduksi_ak, ascending=False)
                tot_s_ton = sub_df[kol_reduksi_ak].sum()
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
                    "Penurunan Emisi (Ton)": sub_df[kol_reduksi_ak].map(lambda v: fmt_id(v, 0)),
                })
                st.dataframe(tampil_sub, hide_index=True, use_container_width=True, height=175)
