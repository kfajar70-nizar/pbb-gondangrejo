import streamlit as st

# ==========================================
# CONFIGURATION
# ==========================================
st.set_page_config(
    page_title="PBB Gondangrejo 2026", 
    page_icon="⚡",
    layout="centered"
)

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
# DATABASE INTERNAL (DATA PAJAK DESA MUTLAK)
# ==========================================
# Silakan tambah, kurangi, atau edit baris data di bawah ini sesuai kebutuhan desa
DATA_PBB = [
    {
        "blok": "001", "no_urut": "0001", 
        "nop": "18.10.080.003.001.0001.0", "nama": "TUGINO", 
        "alamat": "DS. 1 RT: 001 RW: 01", "luas_bumi": "500", "luas_bng": "45", 
        "tagihan": "Rp 75.000", "status": "OK-Dusun_1"
    },
    {
        "blok": "005", "no_urut": "0164", 
        "nop": "18.10.080.003.005.0164.0", "nama": "SAMINO", 
        "alamat": "DS 3 RT: 009 RW: 03", "luas_bumi": "800", "luas_bng": "0", 
        "tagihan": "Rp 107.80", "status": "Lunas (Kolektor 5)"
    },
    {
        "blok": "004", "no_urut": "0145", 
        "nop": "18.10.080.003.004.0145.0", "nama": "KATINO", 
        "alamat": "DS 02 RT: 006 RW: 03", "luas_bumi": "400", "luas_bng": "0", 
        "tagihan": "Rp 34.38", "status": "Lunas (Kolektor 4)"
    },
    {
        "blok": "005", "no_urut": "0071", 
        "nop": "18.10.080.003.005.0071.0", "nama": "WARDOYO", 
        "alamat": "DS 02 RT: 006 RW: 03", "luas_bumi": "765", "luas_bng": "31", 
        "tagihan": "Rp 39.02", "status": "Belum Bayar"
    },
    {
        "blok": "005", "no_urut": "0060", 
        "nop": "18.10.080.003.005.0060.0", "nama": "PONEN", 
        "alamat": "DS 4 RT: 000 RW: 00", "luas_bumi": "955", "luas_bng": "0", 
        "tagihan": "Rp 49.80", "status": "Belum Bayar"
    },
    {
        "blok": "005", "no_urut": "0055", 
        "nop": "18.10.080.003.005.0055.0", "nama": "KIJAN", 
        "alamat": "DSN II RT: 006 RW: 03", "luas_bumi": "1.8", "luas_bng": "0", 
        "tagihan": "Rp 53.13", "status": "Belum Bayar"
    }
]

# ==========================================
# SIDEBAR NAVIGATION
# ==========================================
st.sidebar.markdown("<h2 style='color:#00f5d4; text-align:center;'>🛸 CORE SYSTEM</h2>", unsafe_allow_html=True)
st.sidebar.write("---")
pilihan_login = st.sidebar.radio("Pilih Otoritas Akses:", ["Portal Warga (User)", "Pamong Desa (Admin)"])
st.sidebar.write("---")
st.sidebar.markdown("<div style='text-align: center; font-size: 0.8rem; color: #8d99ae;'><b>PBB GONDANGREJO v5.0</b><br>Database Internal Off-Grid © 2026</div>", unsafe_allow_html=True)

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
            with st.spinner("Memindai database lokal desa..."):
                # Format agar digit selalu pas (Blok = 3 digit, No Urut = 4 digit)
                blok_formatted = input_blok.zfill(3)
                no_formatted = input_no.zfill(4)
                
                # Proses pencarian di dalam database internal
                hasil = None
                for data in DATA_PBB:
                    if data["blok"] == blok_formatted and data["no_urut"] == no_formatted:
                        hasil = data
                        break
                
                if hasil:
                    st.markdown(f"""
                    <div class="futuristic-card">
                        <h3 style='margin-top:0; color:#00f5d4 !important;'>📊 DATA OBJEK PAJAK</h3>
                        <p><b>NOP:</b> <span style='color:#00f5d4;'>{hasil['nop']}</span></p>
                        <p><b>NAMA WAJIB PAJAK:</b> <span style='font-size:1.2rem; color:#fff; font-weight:bold;'>{hasil['nama']}</span></p>
                        <p><b>ALAMAT OP:</b> {hasil['alamat']}</p>
                        <hr style='border-color:rgba(255,255,255,0.1);'>
                        <p>📐 <b>Luas Bumi:</b> {hasil['luas_bumi']} m² | 🏢 <b>Luas Bangunan:</b> {hasil['luas_bng']} m²</p>
                        <p>📍 <b>Status Lapangan:</b> <span style='color:#9b5de5; font-weight:bold;'>{hasil['status']}</span></p>
                        <div style='background:rgba(0, 245, 212, 0.1); padding:15px; border-radius:8px; margin-top:15px; border-left: 5px solid #00f5d4;'>
                            <span style='color:#8d99ae; font-size:0.9rem;'>TOTAL TAGIHAN PBB:</span><br>
                            <span style='font-size:1.8rem; color:#00f5d4; font-weight:bold;'>{hasil['tagihan']}</span>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    st.error("Gagal Menemukan Data! Kombinasi Kode Blok dan Nomor Urut tersebut tidak terdaftar di database lokal.")
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
        st.info("Database saat ini terkunci secara internal di dalam sistem script app.py.")
    elif password != "":
        st.error("Kode Otorisasi Salah! Akses Ditolak.")
