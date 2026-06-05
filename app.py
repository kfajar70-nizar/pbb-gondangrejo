import streamlit as st
import pandas as pd

# ==========================================
# CONSTANTS & CONFIGURATION
# ==========================================
st.set_page_config(
    page_title="PBB Gondangrejo 2026", 
    page_icon="⚡",
    layout="centered"
)

# MASUKKAN ID GOOGLE SHEETS KAMU DI SINI
SHEET_ID = "1u5-c-80qizd21xU4jw5sD4LZE2dGlPqWbCUh5AMc5Jw"
SHEET_NAME = "Sheet1"  # Sesuaikan dengan nama sheet di Google Sheets kamu

# URL untuk membaca data Google Sheets secara langsung dalam bentuk CSV
GOOGLE_SHEET_URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet={SHEET_NAME}"

# ==========================================
# CUSTOM CSS FOR FUTURISTIC UI (DARK & NEON)
# ==========================================
st.markdown("""
<style>
    .stApp {
        background: radial-gradient(circle, #0d1b2a 0%, #010811 100%);
        color: #e0e1dd;
    }
    h1 {
        color: #00f5d4 !important;
        text-shadow: 0 0 10px rgba(0, 245, 212, 0.5);
        font-family: 'Segoe UI', Roboto, Helvetica, sans-serif;
        font-weight: 800 !important;
        text-align: center;
    }
    h3 {
        color: #9b5de5 !important;
    }
    .futuristic-card {
        background: rgba(255, 255, 255, 0.03);
        border: 1px solid rgba(0, 245, 212, 0.2);
        border-radius: 15px;
        padding: 20px;
        margin-bottom: 15px;
        box-shadow: 0 4px 30px rgba(0, 0, 0, 0.5);
        backdrop-filter: blur(5px);
        transition: all 0.3s ease-in-out;
    }
    .futuristic-card:hover {
        border-color: #00f5d4;
        box-shadow: 0 0 15px rgba(0, 245, 212, 0.3);
    }
    .stButton>button {
        background: linear-gradient(45deg, #00f5d4, #7b2cbf) !important;
        color: white !important;
        border: none !important;
        border-radius: 8px !important;
        padding: 10px 24px !important;
        font-weight: bold !important;
        width: 100%;
        box-shadow: 0 4px 15px rgba(0, 245, 212, 0.2);
    }
    .stButton>button:hover {
        box-shadow: 0 4px 20px rgba(0, 245, 212, 0.5);
    }
    label {
        color: #00f5d4 !important;
        font-weight: 600 !important;
    }
</style>
""", unsafe_allow_html=True)

# ==========================================
# DATA LOADING FUNCTION (SUPER SMART & FLEXIBLE)
# ==========================================
def load_data_from_sheets():
    try:
        # Lompat langsung ke baris tabel inti
        df = pd.read_csv(GOOGLE_SHEET_URL, skiprows=4)
        
        # Bersihkan spasi liar di nama kolom dan paksa jadi HURUF BESAR
        df.columns = df.columns.str.strip().str.upper()
        return df
    except Exception as e:
        st.error(f"⚠️ Gagal terhubung ke Google Sheets. Error: {e}")
        st.stop()

df_master = load_data_from_sheets()

# Deteksi otomatis nama kolom asli menggunakan sistem pencari kata kunci parcial (Sangat Aman!)
col_nop = [c for c in df_master.columns if 'NOP' in c][0] if len([c for c in df_master.columns if 'NOP' in c]) > 0 else None
col_nama = [c for c in df_master.columns if 'NAMA' in c][0] if len([c for c in df_master.columns if 'NAMA' in c]) > 0 else None
col_alamat = [c for c in df_master.columns if 'ALAMAT' in c][0] if len([c for c in df_master.columns if 'ALAMAT' in c]) > 0 else None
col_bumi = [c for c in df_master.columns if 'LUAS BUMI' in c or 'BUMI' in c][0] if len([c for c in df_master.columns if 'BUMI' in c]) > 0 else None
col_bng = [c for c in df_master.columns if 'LUAS BNG' in c or 'BNG' in c or 'BANGUNAN' in c][0] if len([c for c in df_master.columns if 'BNG' in c or 'BANGUNAN' in c]) > 0 else None

# Kunci khusus untuk kolom nilai bayar rupiah agar tidak tertukar dengan kolom rekap kanan
col_bayar = None
for c in df_master.columns:
    if 'HARUS DIBAYAR' in c or 'HARUS' in c or 'BAYAR' in c:
        # Hindari mengambil kolom rekap "NILAI" di sebelah kanan
        if 'NILAI' not in c:
            col_bayar = c
            break

# ==========================================
# SIDEBAR NAVIGATION
# ==========================================
st.sidebar.markdown("<h2 style='color:#00f5d4; text-align:center;'>🛸 CORE SYSTEM</h2>", unsafe_allow_html=True)
st.sidebar.write("---")
pilihan_login = st.sidebar.radio("Pilih Otoritas Akses:", ["Portal Warga (User)", "Pamong Desa (Admin)"])
st.sidebar.write("---")
st.sidebar.markdown("<div style='text-align: center; font-size: 0.8rem; color: #8d99ae;'><b>PBB GONDANGREJO v4.3</b><br>Desa Smart City © 2026</div>", unsafe_allow_html=True)

# ==========================================
# 1. PORTAL WARGA / USER INTERFACE
# ==========================================
if pilihan_login == "Portal Warga (User)":
    st.markdown("<h1>👁️ DIGITAL CEK PBB GONDANGREJO</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align:center; color:#8d99ae;'>Sistem Pencarian Cepat Objek Pajak Bumi & Bangunan</p>", unsafe_allow_html=True)
    st.write("")
    
    col1, col2 = st.columns(2)
    with col1:
        input_blok = st.text_input("📡 KODE BLOK / DUSUN", placeholder="Contoh: 5", key="user_blok")
    with col2:
        input_no = st.text_input("🔢 NOMOR URUT NOP", placeholder="Contoh: 164", key="user_no")
        
    st.write("")
    if st.button("PINDAI DATA (SCAN MASTER)"):
        if input_blok and input_no:
            with st.spinner("Sinkronisasi data satelit desa..."):
                blok_formatted = input_blok.zfill(3)
                no_formatted = input_no.zfill(4)
                pola_cari = f".{blok_formatted}.{no_formatted}."
                
                if col_nop:
                    hasil = df_master[df_master[col_nop].astype(str).str.contains(pola_cari, na=False, regex=False)]
                    
                    if not hasil.empty:
                        data = hasil.iloc[0]
                        
                        v_nop = data[col_nop]
                        v_nama = data[col_nama] if col_nama else "Tidak Ada Data"
                        v_alamat = data[col_alamat] if col_alamat else "Tidak Ada Data"
                        v_bumi = data[col_bumi] if col_bumi else "0"
                        v_bng = data[col_bng] if col_bng else "0"
                        v_bayar = data[col_bayar] if col_bayar else "0"
                        
                        # Kolom pertama (Kolom A) bertindak sebagai STATUS LAPANGAN KOLEKTOR
                        v_status = data.iloc[0] if not pd.isna(data.iloc[0]) else "Belum Diinput"
                        
                        st.markdown(f"""
                        <div class="futuristic-card">
                            <h3 style='margin-top:0; color:#00f5d4 !important;'>📊 DATA OBJEK PAJAK</h3>
                            <p><b>NOP:</b> <span style='color:#00f5d4;'>{v_nop}</span></p>
                            <p><b>NAMA WAJIB PAJAK:</b> <span style='font-size:1.2rem; color:#fff; font-weight:bold;'>{str(v_nama)}</span></p>
                            <p><b>ALAMAT OP:</b> {v_alamat}</p>
                            <hr style='border-color:rgba(255,255,255,0.1);'>
                            <p>📐 <b>Luas Bumi:</b> {v_bumi} m² | 🏢 <b>Luas Bangunan:</b> {v_bng} m²</p>
                            <p>📍 <b>Status Lapangan:</b> <span style='color:#9b5de5; font-weight:bold;'>{v_status}</span></p>
                            <div style='background:rgba(0, 245, 212, 0.1); padding:15px; border-radius:8px; margin-top:15px; border-left: 5px solid #00f5d4;'>
                                <span style='color:#8d99ae; font-size:0.9rem;'>TOTAL TAGIHAN PBB:</span><br>
                                <span style='font-size:1.8rem; color:#00f5d4; font-weight:bold;'>Rp {v_bayar}</span>
                            </div>
                        </div>
                        """, unsafe_allow_html=True)
                    else:
                        st.error("Gagal Menemukan Data! Kombinasi Kode Blok dan Nomor Urut tidak ditemukan.")
                else:
                    st.error("Sistem gagal melacak lokasi kolom NOP. Periksa baris ke-5 pada lembar kerja Anda.")
        else:
            st.warning("Sistem memerlukan Kode Blok dan Nomor Urut untuk melakukan pencarian.")

# ==========================================
# 2. PORTAL PAMONG / ADMIN INTERFACE
# ==========================================
elif pilihan_login == "Pamong Desa (Admin)":
    st.markdown("<h1>⚙️ CONTROL PANEL ADMIN</h1>", unsafe_allow_html=True)
    
    password = st.text_input("MASUKKAN KODE OTORISASI (PASSWORD):", type="password")
    if password == "gondangrejo2026":
        st.success("Akses Diterima. Selamat Bertugas, Pamong Desa!")
    elif password != "":
        st.error("Kode Otorisasi Salah! Akses Ditolak.")
