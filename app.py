import streamlit as st
import pandas as pd
import requests

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

# URL Webhook/Script untuk menulis data (Akan diaktifkan pada tahap selanjutnya)
# Untuk saat ini kita fokus ke visual futuristik dan pembacaan real-time dulu.

# ==========================================
# CUSTOM CSS FOR FUTURISTIC UI (DARK & NEON)
# ==========================================
st.markdown("""
<style>
    /* Mengubah background utama aplikasi */
    .stApp {
        background: radial-gradient(circle, #0d1b2a 0%, #010811 100%);
        color: #e0e1dd;
    }
    
    /* Mengubah gaya teks judul */
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
    
    /* Mengubah tampilan Card / Kartu Informasi */
    .futuristic-card {
        background: rgba(255, 255, 255, 0.03);
        border: 1px solid rgba(0, 245, 212, 0.2);
        border-radius: 15px;
        padding: 20px;
        margin-bottom: 15px;
        box-shadow: 0 4px 30px rgba(0, 0, 0, 0.5);
        backdrop-filter: blur(5px);
        -webkit-backdrop-filter: blur(5px);
        transition: all 0.3s ease-in-out;
    }
    
    .futuristic-card:hover {
        border-color: #00f5d4;
        box-shadow: 0 0 15px rgba(0, 245, 212, 0.3);
    }
    
    /* Tombol Utama */
    .stButton>button {
        background: linear-gradient(45deg, #00f5d4, #7b2cbf) !important;
        color: white !important;
        border: none !important;
        border-radius: 8px !important;
        padding: 10px 24px !important;
        font-weight: bold !important;
        width: 100%;
        box-shadow: 0 4px 15px rgba(0, 245, 212, 0.2);
        transition: transform 0.2s;
    }
    
    .stButton>button:hover {
        transform: scale(1.02);
        box-shadow: 0 4px 20px rgba(0, 245, 212, 0.5);
    }
    
    /* Label Input */
    label {
        color: #00f5d4 !important;
        font-weight: 600 !important;
        letter-spacing: 0.5px;
    }
</style>
""", unsafe_allow_value=False)

# ==========================================
# DATA LOADING FUNCTION (REAL-TIME FROM GOOGLE SHEETS)
# ==========================================
def load_data_from_sheets():
    try:
        # Membaca data langsung dari awan (skip 4 baris pertama sesuai struktur file kamu)
        df = pd.read_csv(GOOGLE_SHEET_URL, skiprows=4)
        df.columns = df.columns.str.strip()
        return df
    except Exception as e:
        st.error(f"Gagal terhubung ke Google Sheets. Pastikan ID dan Hak Akses Link sudah Benar. Error: {e}")
        st.stop()

df_master = load_data_from_sheets()

# ==========================================
# SIDEBAR NAVIGATION
# ==========================================
st.sidebar.markdown("<h2 style='color:#00f5d4; text-align:center;'>🛸 CORE SYSTEM</h2>", unsafe_allow_value=False)
st.sidebar.write("---")
pilihan_login = st.sidebar.radio("Pilih Otoritas Akses:", ["Portal Warga (User)", "Pamong Desa (Admin)"])

st.sidebar.write("---")
st.sidebar.markdown("""
<div style='text-align: center; font-size: 0.8rem; color: #8d99ae;'>
    <b>PBB GONDANGREJO v4.0</b><br>
    Digitalisasi Sistem Desa Smart City © 2026
</div>
""", unsafe_allow_value=False)

# ==========================================
# 1. PORTAL WARGA / USER INTERFACE
# ==========================================
if pilihan_login == "Portal Warga (User)":
    st.markdown("<h1>👁️ DIGITAL CEK PBB GONDANGREJO</h1>", unsafe_allow_value=False)
    st.markdown("<p style='text-align:center; color:#8d99ae;'>Sistem Pencarian Cepat Objek Pajak Bumi & Bangunan</p>", unsafe_allow_value=False)
    st.write("")
    
    # Grid Input bergandengan yang estetik
    col1, col2 = st.columns(2)
    with col1:
        input_blok = st.text_input("📡 KODE BLOK / DUSUN", placeholder="Contoh: 5", key="user_blok")
    with col2:
        input_no = st.text_input("🔢 NOMOR URUT NOP", placeholder="Contoh: 164", key="user_no")
        
    st.write("")
    if st.button("PINDAS DATA (SCAN MASTER)"):
        if input_blok and input_no:
            with st.spinner("Sinkronisasi data satelit desa..."):
                blok_formatted = input_blok.zfill(3)
                no_formatted = input_no.zfill(4)
                pola_cari = f".{blok_formatted}.{no_formatted}."
                
                hasil = df_master[df_master['NOP'].str.contains(pola_cari, na=False, regex=False)]
                
                if not hasil.empty:
                    data = hasil.iloc[0]
                    
                    # Tampilan Kartu Hasil yang Sangat Futuristik
                    st.markdown(f"""
                    <div class="futuristic-card">
                        <h3 style='margin-top:0; color:#00f5d4 !important;'>📊 DATA OBJEK PAJAK</h3>
                        <p><b>NOP:</b> <span style='color:#00f5d4;'>{data['NOP']}</span></p>
                        <p><b>NAMA WAJIB PAJAK:</b> <span style='font-size:1.2rem; color:#fff; font-weight:bold;'>{str(data['NAMA WP'])}</span></p>
                        <p><b>ALAMAT OP:</b> {data['ALAMAT OP']}</p>
                        <hr style='border-color:rgba(255,255,255,0.1);'>
                        <p>📐 <b>Luas Bumi:</b> {data['LUAS BUMI']} m² | 🏢 <b>Luas Bangunan:</b> {data['LUAS BNG']} m²</p>
                        <p>📍 <b>Status Lapangan:</b> <span style='color:#9b5de5; font-weight:bold;'>{data.iloc[0] if not pd.isna(data.iloc[0]) else 'Belum Diinput'}</span></p>
                        <div style='background:rgba(0, 245, 212, 0.1); padding:15px; border-radius:8px; margin-top:15px; border-left: 5px solid #00f5d4;'>
                            <span style='color:#8d99ae; font-size:0.9rem;'>TOTAL TAGIHAN PBB:</span><br>
                            <span style='font-size:1.8rem; color:#00f5d4; font-weight:bold;'>Rp {data['PBB HARUS DIBAYAR (Rp)']}</span>
                        </div>
                    </div>
                    """, unsafe_allow_value=False)
                else:
                    st.error("Gagal Menemukan Data! Kombinasi Kode Blok dan Nomor Urut tidak terdaftar di server pusat.")
        else:
            st.warning("Sistem memerlukan Kode Blok dan Nomor Urut untuk melakukan pencarian.")

# ==========================================
# 2. PORTAL PAMONG / ADMIN INTERFACE
# ==========================================
elif pilihan_login == "Pamong Desa (Admin)":
    st.markdown("<h1>⚙️ CONTROL PANEL ADMIN</h1>", unsafe_allow_value=False)
    
    password = st.text_input("MASUKKAN KODE OTORISASI (PASSWORD):", type="password")
    if password == "gondangrejo2026":
        st.success("Akses Diterima. Selamat Bertugas, Pamong Desa!")
        
        st.write("---")
        st.subheader("🛠️ Modifikasi Status & Validasi Setoran")
        
        col1, col2 = st.columns(2)
        with col1:
            admin_blok = st.text_input("Blok Target", placeholder="Misal: 5", key="adm_blok")
        with col2:
            admin_no = st.text_input("Nomor Urut Target", placeholder="Misal: 164", key="adm_no")
            
        if admin_blok and admin_no:
            b_form = admin_blok.zfill(3)
            n_form = admin_no.zfill(4)
            pola_admin = f".{b_form}.{n_form}."
            
            idx_hasil = df_master[df_master['NOP'].str.contains(pola_admin, na=False, regex=False)].index
            
            if len(idx_hasil) > 0:
                idx = idx_hasil[0]
                data_target = df_master.loc[idx]
                
                st.markdown(f"""
                <div class="futuristic-card" style='border-color:#9b5de5;'>
                    <span style='color:#9b5de5;'>Target Terkunci:</span><br>
                    <b>WP:</b> {data_target['NAMA WP']} <br>
                    <b>Tagihan:</b> Rp {data_target['PBB HARUS DIBAYAR (Rp)']}
                </div>
                """, unsafe_allow_value=False)
                
                aksi = st.selectbox("Pilih Tindakan Modifikasi:", ["Pilih...", "Validasi Kolektor Dusun", "Konfirmasi Sudah Setor", "Tandai Hapus/Batal"])
                
                if aksi == "Validasi Kolektor Dusun":
                    nomor_dusun = st.number_input("Tugaskan ke Dusun (1-10):", min_value=1, max_value=10, value=1)
                    if st.button("Suntik Data Kolektor"):
                        st.info("💡 Data lokal berhasil dimodifikasi secara visual! Untuk menyimpan permanen ke Google Sheets, kita akan pasang fitur Webhook Script di langkah berikutnya.")
                        
                elif aksi == "Konfirmasi Sudah Setor":
                    if st.button("Kunci Status Lunas (SUDAH SETOR)"):
                        st.info("💡 Status Lunas disiapkan! Siap dikirim ke server cloud Google Sheets.")
            else:
                st.warning("NOP Target tidak ditemukan.")
    elif password != "":
        st.error("Kode Otorisasi Salah! Akses Ditolak.")
