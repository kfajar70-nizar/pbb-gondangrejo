import streamlit as st
import pandas as pd
import os
import re
import urllib.parse
from datetime import datetime

# ==========================================
# CONFIGURATION
# ==========================================
st.set_page_config(
    page_title="PBB Gondangrejo 2026", 
    page_icon="⚡",
    layout="centered"
)

# ==========================================
# CUSTOM CSS FOR FUTURISTIC UI & PRINT LOGIC
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
    h2, h3, h4 {
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
    .wa-button {
        display: block;
        text-align: center;
        background: linear-gradient(45deg, #25D366, #128C7E);
        color: white !important;
        font-weight: bold;
        padding: 12px;
        border-radius: 8px;
        text-decoration: none;
        box-shadow: 0 4px 15px rgba(37, 211, 102, 0.3);
        transition: all 0.3s;
        margin-top: 15px;
    }
    .wa-button:hover {
        box-shadow: 0 4px 20px rgba(37, 211, 102, 0.6);
        transform: scale(1.01);
    }
    .kwitansi-box {
        background-color: #ffffff !important;
        color: #000000 !important;
        font-family: 'Courier New', Courier, monospace;
        padding: 20px;
        border-radius: 5px;
        border: 2px dashed #333;
        line-height: 1.2;
        margin-top: 15px;
        margin-bottom: 15px;
        white-space: pre-wrap;
    }
    label {
        color: #00f5d4 !important;
        font-weight: 600 !important;
    }

    @media print {
        body * {
            visibility: hidden;
        }
        #area-cetak-kwitansi, #area-cetak-kwitansi * {
            visibility: visible;
        }
        #area-cetak-kwitansi {
            position: absolute;
            left: 0;
            top: 0;
            width: 100%;
            background: white !important;
            color: black !important;
            padding: 0;
            margin: 0;
        }
    }
</style>
""", unsafe_allow_html=True)

# ==========================================
# AUTOMATIC DATA LOADING & CONFIG
# ==========================================
CSV_FILE_NAME = "data_pbb.csv"

DAFTAR_WA_KOLEKTOR = {
    "Dusun 1": "6281111111111",
    "Dusun 2": "6282222222222",
    "Dusun 3": "6283333333333",
    "Dusun 4": "6284444444444",
    "Dusun 5": "6285555555555",
    "Dusun 6": "6286666666666",
    "Dusun 7": "6287777777777",
    "Dusun 8": "6288888888888",
    "Dusun 9": "6289999999999",
    "Dusun 10": "6281010101010",
    "PUSAT_ADMIN": "6289512345678"
}

def format_clean_luas(val):
    if pd.isna(val):
        return 0
    val_str = str(val).strip().replace(',', '')
    if val_str.upper() == 'XXX' or val_str == '' or val_str == '0':
        return 0
    try:
        if '.' in val_str and len(val_str.split('.')[-1]) == 3:
            val_str = val_str.replace('.', '')
        return int(float(val_str))
    except:
        return 0

def format_clean_rupiah(val):
    if pd.isna(val):
        return 0
    try:
        clean_val = ''.join(filter(str.isdigit, str(val)))
        return int(clean_val) if clean_val else 0
    except:
        return 0

def bersihkan_nama_dusun(val):
    if pd.isna(val) or str(val).strip() == "" or str(val).strip() == "0":
        return "BELUM TERINPUT"
    val_upper = str(val).upper().strip()
    if 'HAPUS' in val_upper:
        return "HAPUS"
    if 'BPN' in val_upper:
        return "BPN"
    angka_dusun = re.findall(r'\d+', val_upper)
    if 'DUSUN' in val_upper and angka_dusun:
        return f"Dusun {angka_dusun[0]}"
    return val_upper

def urutan_dusun_kunci(nama_dusun):
    angka = re.findall(r'\d+', nama_dusun)
    if angka:
        return int(angka[0])
    return 999 

def angka_ke_terbilang(n):
    bilang = ["", "Satu", "Dua", "Tiga", "Empat", "Lima", "Enam", "Tujuh", "Delapan", "Sembilan", "Sepuluh", "Sebelas"]
    if n < 12:
        return bilang[n]
    elif n < 20:
        return angka_ke_terbilang(n - 10) + " Belas"
    elif n < 100:
        return angka_ke_terbilang(n // 10) + " Puluh " + angka_ke_terbilang(n % 10)
    elif n < 200:
        return "Seratus " + angka_ke_terbilang(n - 100)
    elif n < 1000:
        return angka_ke_terbilang(n // 100) + " Ratus " + angka_ke_terbilang(n % 100)
    elif n < 2000:
        return "Seribu " + angka_ke_terbilang(n - 1000)
    elif n < 1000000:
        return angka_ke_terbilang(n // 1000) + " Ribu " + angka_ke_terbilang(n % 1000)
    elif n < 1000000000:
        return angka_ke_terbilang(n // 1000000) + " Juta " + angka_ke_terbilang(n % 1000000)
    return "Angka Terlalu Besar"

def ekstrak_tanggal(val_kolom_p):
    if pd.isna(val_kolom_p):
        return None
    val_str = str(val_kolom_p).strip()
    pencarian = re.search(r'(\d{1,2}[/\-]\d{1,2}([/\-]\d{2,4})?)', val_str)
    if pencarian:
        return pencarian.group(1)
    if 'setor' in val_str.lower():
        return datetime.now().strftime("%d/%m/%Y")
    return None

def load_local_data():
    if not os.path.exists(CSV_FILE_NAME):
        st.error(f"⚠️ File '{CSV_FILE_NAME}' tidak ditemukan!")
        st.stop()
    try:
        df = pd.read_csv(CSV_FILE_NAME, skiprows=4)
        df.columns = df.columns.str.strip()
        df = df.dropna(subset=['NOP', 'NAMA WP'], how='all')
        df = df[df['NOP'].astype(str).str.strip() != '']
        
        df['LUAS BUMI NUM'] = df['LUAS BUMI'].apply(format_clean_luas)
        df['LUAS BNG NUM'] = df['LUAS BNG'].apply(format_clean_luas)
        df['TAGIHAN NUM'] = df['PBB HARUS DIBAYAR (Rp)'].apply(format_clean_rupiah)
        
        kolom_status_asal = df.columns[0]
        df['STATUS_ASLI'] = df[kolom_status_asal]
        df['DUSUN_CLEAN'] = df['STATUS_ASLI'].apply(bersihkan_nama_dusun)
        
        if len(df.columns) >= 16:
            kolom_p = df.columns[15]
            df['RAW_P'] = df[kolom_p].astype(str)
            df['STATUS_BAYAR'] = df['RAW_P'].str.lower().str.contains('setor|\d', regex=True, na=False).map({True: 'LUNAS', False: 'BELUM LUNAS'})
            df['TANGGAL_BAYAR'] = df['RAW_P'].apply(ekstrak_tanggal)
        else:
            df['STATUS_BAYAR'] = 'BELUM LUNAS'
            df['TANGGAL_BAYAR'] = None
            
        return df
    except Exception as e:
        st.error(f"⚠️ Gagal membaca database CSV lokal. Error: {e}")
        st.stop()

df_master = load_local_data()

# ==========================================
# SIDEBAR NAVIGATION
# ==========================================
st.sidebar.markdown("<h2 style='color:#00f5d4; text-align:center;'>🛸 CORE SYSTEM</h2>", unsafe_allow_html=True)
st.sidebar.write("---")
pilihan_login = st.sidebar.radio("Pilih Otoritas Akses:", ["Portal Warga (User)", "Pamong Desa (Admin)"])
st.sidebar.write("---")
st.sidebar.markdown("<div style='text-align: center; font-size: 0.8rem; color: #8d99ae;'><b>PBB GONDANGREJO v8.3</b><br>Fixed Table View © 2026</div>", unsafe_allow_html=True)

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
                blok_formatted = input_blok.zfill(3)
                no_formatted = input_no.zfill(4)
                pola_cari = f".{blok_formatted}.{no_formatted}"
                
                hasil = df_master[df_master['NOP'].astype(str).str.contains(pola_cari, na=False, regex=False)]
                
                if not hasil.empty:
                    data = hasil.iloc[0]
                    v_nop = data.get('NOP', 'Tidak Ada Data')
                    v_nama = data.get('NAMA WP', 'Tidak Ada Data')
                    v_alamat = data.get('ALAMAT OP', 'Tidak Ada Data')
                    v_bumi = data['LUAS BUMI NUM']
                    v_bng = data['LUAS BNG NUM']
                    v_bayar = data['TAGIHAN NUM']
                    v_status = data['DUSUN_CLEAN']
                    v_lunas = data['STATUS_BAYAR']
                    
                    if v_lunas == "LUNAS":
                        status_html = f"<div style='background:rgba(37, 211, 102, 0.15); padding:10px; border-radius:8px; border:1px solid #25D366; color:#25D366; text-align:center; font-weight:bold; margin-top:10px;'>✅ STATUS PEMBAYARAN: LUNAS (TERCATAT TANGGAL: {data['TANGGAL_BAYAR']})</div>"
                    else:
                        status_html = "<div style='background:rgba(239, 71, 111, 0.15); padding:10px; border-radius:8px; border:1px solid #ef476f; color:#ef476f; text-align:center; font-weight:bold; margin-top:10px;'>⚠️ STATUS PEMBAYARAN: BELUM BAYAR</div>"
                    
                    if v_status in DAFTAR_WA_KOLEKTOR:
                        nomor_wa_tujuan = DAFTAR_WA_KOLEKTOR[v_status]
                        label_kolektor = f"HUBUNGI KOLEKTOR {v_status.upper()}"
                    else:
                        nomor_wa_tujuan = DAFTAR_WA_KOLEKTOR["PUSAT_ADMIN"]
                        label_kolektor = f"HUBUNGI PUSAT DATA (STATUS: {v_status.upper()})"
                    
                    pesan_wa = f"Halo Pamong Desa Gondangrejo, saya ingin mengonfirmasi PBB atas nama {v_nama}.\n\nBerikut data Objek Pajak saya:\n- NOP: {v_nop}\n- Alamat OP: {v_alamat}\n- Tagihan: Rp {v_bayar:,}\n- Status Lapangan: {v_status}\n- Status Bayar: {v_lunas}\n\nMohon dibantu, terima kasih!".replace(",", ".")
                    pesan_wa_encoded = urllib.parse.quote(pesan_wa)
                    link_wa = f"https://wa.me/{nomor_wa_tujuan}?text={pesan_wa_encoded}"
                    
                    st.markdown(f"""
                    <div class="futuristic-card">
                        <h3 style='margin-top:0; color:#00f5d4 !important;'>📊 DATA OBJEK PAJAK</h3>
                        <p><b>NOP:</b> <span style='color:#00f5d4;'>{v_nop}</span></p>
                        <p><b>NAMA WAJIB PAJAK:</b> <span style='font-size:1.2rem; color:#fff; font-weight:bold;'>{str(v_nama)}</span></p>
                        <p><b>ALAMAT OP:</b> {v_alamat}</p>
                        <hr style='border-color:rgba(255,255,255,0.1);'>
                        <p>📐 <b>Luas Bumi:</b> {v_bumi:,} m² | 🏢 <b>Luas Bangunan:</b> {v_bng:,} m²</p>
                        <p>📍 <b>Status Lapangan:</b> <span style='color:#9b5de5; font-weight:bold;'>{v_status}</span></p>
                        <div style='background:rgba(0, 245, 212, 0.1); padding:15px; border-radius:8px; margin-top:15px; border-left: 5px solid #00f5d4;'>
                            <span style='color:#8d99ae; font-size:0.9rem;'>TOTAL TAGIHAN PBB:</span><br>
                            <span style='font-size:1.8rem; color:#00f5d4; font-weight:bold;'>Rp {v_bayar:,}</span>
                        </div>
                        {status_html}
                        <a href="{link_wa}" target="_blank" class="wa-button">🟢 {label_kolektor}</a>
                    </div>
                    """.replace(",", "."), unsafe_allow_html=True)
                else:
                    st.error("Gagal Menemukan Data! Kombinasi Kode Blok dan Nomor Urut tersebut tidak ditemukan.")
        else:
            st.warning("Sistem memerlukan Kode Blok dan Nomor Urut untuk melakukan pencarian.")

# ==========================================
# 2. PORTAL PAMONG / ADMIN INTERFACE
# ==========================================
elif pilihan_login == "Pamong Desa (Admin)":
    st
