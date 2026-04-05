import streamlit as st
import pandas as pd
import io
from io import BytesIO

# ─── Page Config ────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="PAGUREAL Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ─── Custom CSS ─────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Mono:wght@400;700&family=DM+Sans:wght@300;400;600;700&display=swap');

html, body, [class*="css"] {
    font-family: 'DM Sans', sans-serif;
}

.stApp {
    background: #0d1117;
    color: #e6edf3;
}

/* Sidebar */
[data-testid="stSidebar"] {
    background: #161b22 !important;
    border-right: 1px solid #21262d;
}

/* Header banner */
.header-banner {
    background: linear-gradient(135deg, #1f6feb 0%, #388bfd 50%, #58a6ff 100%);
    border-radius: 12px;
    padding: 32px 36px;
    margin-bottom: 28px;
    position: relative;
    overflow: hidden;
}
.header-banner::before {
    content: '';
    position: absolute;
    top: -50%;
    right: -10%;
    width: 300px;
    height: 300px;
    background: rgba(255,255,255,0.06);
    border-radius: 50%;
}
.header-banner h1 {
    font-family: 'Space Mono', monospace;
    font-size: 2rem;
    font-weight: 700;
    color: #fff;
    margin: 0 0 6px 0;
    letter-spacing: -0.5px;
}
.header-banner p {
    color: rgba(255,255,255,0.82);
    font-size: 0.95rem;
    margin: 0;
    font-weight: 300;
}

/* Cards */
.metric-card {
    background: #161b22;
    border: 1px solid #21262d;
    border-radius: 10px;
    padding: 20px 24px;
    margin-bottom: 16px;
    transition: border-color 0.2s;
}
.metric-card:hover {
    border-color: #388bfd;
}
.metric-label {
    font-size: 0.75rem;
    color: #8b949e;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    font-weight: 600;
    margin-bottom: 6px;
}
.metric-value {
    font-family: 'Space Mono', monospace;
    font-size: 1.6rem;
    font-weight: 700;
    color: #58a6ff;
}

/* Steps */
.step-box {
    background: #161b22;
    border: 1px solid #21262d;
    border-left: 3px solid #388bfd;
    border-radius: 8px;
    padding: 14px 18px;
    margin-bottom: 12px;
    font-size: 0.875rem;
    color: #c9d1d9;
}
.step-num {
    font-family: 'Space Mono', monospace;
    color: #58a6ff;
    font-weight: 700;
    margin-right: 8px;
}

/* Success / Info badges */
.badge-success {
    background: rgba(63,185,80,0.15);
    color: #3fb950;
    border: 1px solid rgba(63,185,80,0.3);
    border-radius: 20px;
    padding: 3px 12px;
    font-size: 0.78rem;
    font-weight: 600;
    display: inline-block;
}
.badge-info {
    background: rgba(88,166,255,0.15);
    color: #58a6ff;
    border: 1px solid rgba(88,166,255,0.3);
    border-radius: 20px;
    padding: 3px 12px;
    font-size: 0.78rem;
    font-weight: 600;
    display: inline-block;
}

/* Dataframe wrapper */
[data-testid="stDataFrame"] {
    border: 1px solid #21262d;
    border-radius: 8px;
    overflow: hidden;
}

/* Download button */
.stDownloadButton > button {
    background: linear-gradient(135deg, #1f6feb, #388bfd) !important;
    color: #fff !important;
    border: none !important;
    border-radius: 8px !important;
    font-weight: 600 !important;
    font-size: 0.9rem !important;
    padding: 10px 24px !important;
    width: 100% !important;
    transition: opacity 0.2s !important;
}
.stDownloadButton > button:hover {
    opacity: 0.88 !important;
}

/* File uploader */
[data-testid="stFileUploader"] {
    background: #161b22;
    border: 1.5px dashed #30363d;
    border-radius: 10px;
    padding: 10px;
}

/* Divider */
hr {
    border-color: #21262d !important;
    margin: 24px 0 !important;
}

/* Expander */
.streamlit-expanderHeader {
    background: #161b22 !important;
    border: 1px solid #21262d !important;
    border-radius: 8px !important;
    color: #c9d1d9 !important;
    font-weight: 600 !important;
}

h2, h3 {
    font-family: 'Space Mono', monospace;
    letter-spacing: -0.3px;
}
</style>
""", unsafe_allow_html=True)


# ─── Helper: Transformasi ───────────────────────────────────────────────────
def transform_data(df: pd.DataFrame) -> pd.DataFrame:
    """Transformasi DataFrame ke format long + hitung NILAI2."""

    id_cols = [c for c in df.columns if c not in ['PAGU_DIPA', 'REALISASI']]

    # Melt ke format long
    df_long = df.melt(
        id_vars=id_cols,
        value_vars=['PAGU_DIPA', 'REALISASI'],
        var_name='JenisAnggaran',
        value_name='NILAI'
    )

    # Hitung NILAI2
    def calculate_nilai2(row):
        if row['JenisAnggaran'] == 'PAGU_DIPA':
            mask = (
                (df_long['JenisAnggaran'] == 'REALISASI') &
                (df_long['NMAKUN'] == row['NMAKUN']) &
                (df_long['NMKABKOTA'] == row['NMKABKOTA']) &
                (df_long['NMOUTPUT'] == row['NMOUTPUT'])
            )
            vals = df_long[mask]['NILAI'].values
            return row['NILAI'] - vals[0] if vals.size > 0 else row['NILAI']
        elif row['JenisAnggaran'] == 'REALISASI':
            return row['NILAI']
        return None

    df_long['NILAI2'] = df_long.apply(calculate_nilai2, axis=1)
    return df_long


def to_excel_bytes(df: pd.DataFrame) -> bytes:
    buf = BytesIO()
    with pd.ExcelWriter(buf, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='PAGUREAL')
    return buf.getvalue()


# ─── Header ─────────────────────────────────────────────────────────────────
st.markdown("""
<div class="header-banner">
    <h1>📊 PAGUREAL Dashboard</h1>
    <p>Transformasi Data Anggaran · PAGU DIPA & Realisasi · Format Long Table</p>
</div>
""", unsafe_allow_html=True)


# ─── Sidebar ────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("### 🗂️ Upload File")
    uploaded = st.file_uploader(
        "Pilih file Excel (.xlsx / .xls)",
        type=["xlsx", "xls"],
        help="File harus memiliki kolom PAGU_DIPA, REALISASI, NMAKUN, NMKABKOTA, NMOUTPUT"
    )

    st.markdown("---")
    st.markdown("### 📋 Alur Transformasi")
    st.markdown("""
    <div class="step-box"><span class="step-num">01</span>Upload file Excel input</div>
    <div class="step-box"><span class="step-num">02</span>Preview data mentah</div>
    <div class="step-box"><span class="step-num">03</span>Melt → format long</div>
    <div class="step-box"><span class="step-num">04</span>Hitung kolom NILAI2</div>
    <div class="step-box"><span class="step-num">05</span>Download PAGUREAL.xlsx</div>
    """, unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("### ℹ️ Logika NILAI2")
    st.markdown("""
    <div style="font-size:0.82rem;color:#8b949e;line-height:1.7">
    • <b style="color:#c9d1d9">PAGU_DIPA</b>: NILAI − REALISASI<br>
      (matched by NMAKUN, NMKABKOTA, NMOUTPUT)<br><br>
    • <b style="color:#c9d1d9">REALISASI</b>: sama dengan NILAI
    </div>
    """, unsafe_allow_html=True)


# ─── Main Content ────────────────────────────────────────────────────────────
if uploaded is None:
    st.markdown("""
    <div style="text-align:center;padding:80px 0;color:#484f58">
        <div style="font-size:4rem;margin-bottom:16px">📂</div>
        <div style="font-size:1.1rem;font-weight:600;color:#8b949e">Belum ada file yang diunggah</div>
        <div style="font-size:0.875rem;margin-top:8px">Upload file Excel Anda melalui panel kiri untuk memulai</div>
    </div>
    """, unsafe_allow_html=True)
    st.stop()


# ─── Load & Validate ────────────────────────────────────────────────────────
try:
    df_raw = pd.read_excel(uploaded)
except Exception as e:
    st.error(f"❌ Gagal membaca file: {e}")
    st.stop()

required_cols = {'PAGU_DIPA', 'REALISASI', 'NMAKUN', 'NMKABKOTA', 'NMOUTPUT'}
missing = required_cols - set(df_raw.columns)
if missing:
    st.error(f"❌ Kolom wajib tidak ditemukan: **{', '.join(missing)}**")
    st.stop()


# ─── Metrics Row ────────────────────────────────────────────────────────────
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-label">Total Baris Input</div>
        <div class="metric-value">{len(df_raw):,}</div>
    </div>""", unsafe_allow_html=True)

with col2:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-label">Total Kolom Input</div>
        <div class="metric-value">{len(df_raw.columns)}</div>
    </div>""", unsafe_allow_html=True)

with col3:
    total_pagu = df_raw['PAGU_DIPA'].sum()
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-label">Total PAGU DIPA</div>
        <div class="metric-value" style="font-size:1.1rem">{total_pagu:,.0f}</div>
    </div>""", unsafe_allow_html=True)

with col4:
    total_real = df_raw['REALISASI'].sum()
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-label">Total REALISASI</div>
        <div class="metric-value" style="font-size:1.1rem">{total_real:,.0f}</div>
    </div>""", unsafe_allow_html=True)


# ─── Preview Input ──────────────────────────────────────────────────────────
with st.expander("🔍 Preview Data Mentah (Input)", expanded=False):
    st.dataframe(df_raw.head(100), use_container_width=True, height=300)
    st.caption(f"Menampilkan maks. 100 baris dari {len(df_raw):,} total baris")


st.markdown("---")

# ─── Transformasi ───────────────────────────────────────────────────────────
with st.spinner("⚙️  Memproses transformasi data..."):
    try:
        df_result = transform_data(df_raw)
        success = True
    except KeyError as ke:
        st.error(f"❌ Kolom tidak ditemukan saat transformasi: {ke}")
        success = False
    except Exception as e:
        st.error(f"❌ Error transformasi: {e}")
        success = False

if not success:
    st.stop()

# ─── Result Section ─────────────────────────────────────────────────────────
st.markdown("### ✅ Hasil Transformasi")

col_a, col_b = st.columns([2, 1])
with col_a:
    st.markdown(f'<span class="badge-success">✓ Transformasi berhasil</span>&nbsp;&nbsp;<span class="badge-info">{len(df_result):,} baris hasil</span>', unsafe_allow_html=True)
with col_b:
    excel_bytes = to_excel_bytes(df_result)
    st.download_button(
        label="⬇️  Download PAGUREAL.xlsx",
        data=excel_bytes,
        file_name="PAGUREAL.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

st.markdown("<br>", unsafe_allow_html=True)

# Filter preview
col_f1, col_f2 = st.columns(2)
with col_f1:
    jenis_filter = st.multiselect(
        "Filter JenisAnggaran",
        options=df_result['JenisAnggaran'].unique().tolist(),
        default=df_result['JenisAnggaran'].unique().tolist()
    )
with col_f2:
    if 'NMKABKOTA' in df_result.columns:
        kab_opts = ['Semua'] + sorted(df_result['NMKABKOTA'].dropna().unique().tolist())
        kab_filter = st.selectbox("Filter NMKABKOTA", kab_opts)
    else:
        kab_filter = 'Semua'

df_view = df_result[df_result['JenisAnggaran'].isin(jenis_filter)]
if kab_filter != 'Semua':
    df_view = df_view[df_view['NMKABKOTA'] == kab_filter]

st.dataframe(df_view.head(500), use_container_width=True, height=400)
st.caption(f"Preview maks. 500 baris · Total hasil: {len(df_result):,} baris · Kolom baru: JenisAnggaran, NILAI, NILAI2")

# ─── Ringkasan NILAI2 ────────────────────────────────────────────────────────
st.markdown("---")
st.markdown("### 📈 Ringkasan NILAI & NILAI2 per JenisAnggaran")

summary = df_result.groupby('JenisAnggaran')[['NILAI', 'NILAI2']].agg(['sum', 'mean', 'count'])
summary.columns = ['NILAI_Sum', 'NILAI_Mean', 'NILAI_Count', 'NILAI2_Sum', 'NILAI2_Mean', 'NILAI2_Count']
summary = summary.reset_index()
st.dataframe(summary.style.format({
    'NILAI_Sum': '{:,.0f}', 'NILAI_Mean': '{:,.2f}',
    'NILAI2_Sum': '{:,.0f}', 'NILAI2_Mean': '{:,.2f}'
}), use_container_width=True)

st.markdown("""
<div style="margin-top:32px;padding:16px 20px;background:#161b22;border:1px solid #21262d;border-radius:8px;font-size:0.8rem;color:#8b949e">
    <b style="color:#c9d1d9">Catatan:</b> NILAI2 pada baris PAGU_DIPA = PAGU − REALISASI (sisa anggaran).
    NILAI2 pada baris REALISASI = sama dengan NILAI (realisasi aktual).
</div>
""", unsafe_allow_html=True)
