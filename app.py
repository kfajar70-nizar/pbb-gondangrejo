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
    val_str = str(val).strip().replace(',', '') # Hapus koma pemisah ribuan jika ada
    if val_str.upper() == 'XXX' or val_str == '':
        return 0
    try:
        # Jika ada titik tunggal yang mendefinisikan ribuan (misal 3.125), kita bersihkan titiknya
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

# ✨ Perbaikan Fungsi Terbilang agar support hingga Ratusan Juta/Milyar
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
        # Penyesuaian pembacaan header agar pas dengan struktur CSV PBB
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
        
        # Deteksi status bayar dari kolom ke-16 (Kolom P)
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
st.sidebar.markdown("<div style='text-align: center; font-size: 0.8rem; color: #8d99ae;'><b>PBB GONDANGREJO v8.1</b><br>Fixed Calculation & Terbilang © 2026</div>", unsafe_allow_html=True)

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
    st.markdown("<h1>⚙️ CONTROL PANEL & REKAP DESA</h1>", unsafe_allow_html=True)
    
    # Tips Keamanan: Pakai st.secrets untuk deployment production nyata di GitHub!
    password = st.text_input("MASUKKAN KODE OTORISASI (PASSWORD):", type="password")
    if password == "gondangrejo2026":
        st.success("🔒 Akses Diterima. Dashboard Rekap Terbuka.")
        
        total_wp = len(df_master)
        total_target_pbb = df_master['TAGIHAN NUM'].sum()
        
        df_lunas = df_master[df_master['STATUS_BAYAR'] == 'LUNAS']
        df_belum = df_master[df_master['STATUS_BAYAR'] != 'LUNAS']
        
        total_dana_masuk = df_lunas['TAGIHAN NUM'].sum()
        total_tunggakan = df_belum['TAGIHAN NUM'].sum()
        wp_lunas = len(df_lunas)
        persen_realisasi_dana = (total_dana_masuk / total_target_pbb) if total_target_pbb > 0 else 0
        
        st.write("### 💰 PROGRESS REALISASI PENERIMAAN PBB DESA")
        st.progress(persen_realisasi_dana)
        st.markdown(f"<p style='color:#25D366; font-weight:bold;'>📈 Realisasi Kas: Rp {total_dana_masuk:,} Berhasil Disetor dari Total Target Rp {total_target_pbb:,} ({persen_realisasi_dana*100:.2f}%)</p>".replace(",", "."), unsafe_allow_html=True)
        st.write("")

        st.write("### 📊 TABEL REKAPITULASI REALISASI PER WILAYAH DUSUN")
        
        rekap_dusun = df_master.groupby('DUSUN_CLEAN').agg(
            Total_WP=('NOP', 'count'),
            Total_Target=('TAGIHAN NUM', 'sum'),
            Sudah_Setor=('TAGIHAN NUM', lambda x: x[df_master.loc[x.index, 'STATUS_BAYAR'] == 'LUNAS'].sum()),
            Belum_Setor=('TAGIHAN NUM', lambda x: x[df_master.loc[x.index, 'STATUS_BAYAR'] != 'LUNAS'].sum())
        ).reset_index()
        
        rekap_dusun['Capaian_%'] = (rekap_dusun['Sudah_Setor'] / rekap_dusun['Total_Target'] * 100).round(2)
        rekap_dusun['sort_key'] = rekap_dusun['DUSUN_CLEAN'].apply(urutan_dusun_kunci)
        rekap_dusun = rekap_dusun.sort_values(by='sort_key').drop(columns=['sort_key'])
        
        rekap_tampilan = rekap_dusun.copy()
        rekap_tampilan.columns = ['WILAYAH / DUSUN', 'TOTAL WP', 'TOTAL TARGET (Rp)', 'KAS MASUK (Rp)', 'SISA TUNGGAKAN (Rp)', 'CAPAIAN (%)']
        st.dataframe(rekap_tampilan, use_container_width=True, hide_index=True)
        
        st.write("### 📈 GRAFIK TREN SETORAN KAS HARIAN DESA")
        df_tren_hari = df_lunas.dropna(subset=['TANGGAL_BAYAR']).groupby('TANGGAL_BAYAR')['TAGIHAN NUM'].sum().reset_index()
        if not df_tren_hari.empty:
            df_tren_hari = df_tren_hari.sort_values(by='TANGGAL_BAYAR')
            st.line_chart(data=df_tren_hari, x='TANGGAL_BAYAR', y='TAGIHAN NUM', color='#25D366')
        else:
            st.info("💡 Belum ada data tren harian. Ketik tanggal di Kolom P untuk menyalakan grafik.")

        st.write("### 🌌 RINGKASAN GLOBAL & MONITORING KAS DESA")
        m_col1, m_col2 = st.columns(2)
        with m_col1:
            st.markdown(f"""
            <div class="futuristic-card" style="text-align: center; border-color:#25D366;">
                <span style="color:#8d99ae; font-size:0.9rem;">🟢 TOTAL KAS MASUK (SUDAH SETOR)</span><br>
                <span style="font-size:1.8rem; color:#25D366; font-weight:bold;">Rp {total_dana_masuk:,}</span><br>
                <span style="font-size:0.9rem; color:#8d99ae;">Dari {wp_lunas:,} Wajib Pajak</span>
            </div>
            """.replace(",", "."), unsafe_allow_html=True)
        with m_col2:
            st.markdown(f"""
            <div class="futuristic-card" style="text-align: center; border-color:#ef476f;">
                <span style="color:#8d99ae; font-size:0.9rem;">🔴 SISA TUNGGAKAN PBB (BELUM SETOR)</span><br>
                <span style="font-size:1.8rem; color:#ef476f; font-weight:bold;">Rp {total_tunggakan:,}</span><br>
                <span style="font-size:0.9rem; color:#8d99ae;">Dari {total_wp - wp_lunas:,} Wajib Pajak</span>
            </div>
            """.replace(",", "."), unsafe_allow_html=True)

        st.write("---")
        st.write("### 🔍 VALIDATOR DATA LAPANGAN & GENERATOR KWITANSI")
        
        list_kategori = sorted(df_master['DUSUN_CLEAN'].unique(), key=urutan_dusun_kunci)
        pilihan_kategori = st.selectbox("📁 PILIH KATEGORI VALIDASI STATUS:", list_kategori)
        filter_bayar_opsi = st.radio("Saring Status Warga:", ["Semua Warga", "Hanya yang Sudah Setor (LUNAS)", "Hanya yang Belum Setor"], horizontal=True)
        
        df_filtered_admin = df_master[df_master['DUSUN_CLEAN'] == pilihan_kategori]
        if filter_bayar_opsi == "Hanya yang Sudah Setor (LUNAS)":
            df_filtered_admin = df_filtered_admin[df_filtered_admin['STATUS_BAYAR'] == 'LUNAS']
        elif filter_bayar_opsi == "Hanya yang Belum Setor":
            df_filtered_admin = df_filtered_admin[df_filtered_admin['STATUS_BAYAR'] != 'LUNAS']
            
        sub_wp = len(df_filtered_admin)
        sub_uang = df_filtered_admin['TAGIHAN NUM'].sum()
        
        st.info(f"📊 Menampilkan **{sub_wp:,} Objek Pajak** pada **{pilihan_kategori}** ({filter_bayar_opsi}) | Sub-Total Nilai: **Rp {sub_uang:,}**".replace(",", "."))
        
        if not df_filtered_admin.empty:
            df_tabel_admin = df_filtered_admin[['NOP', 'NAMA WP', 'ALAMAT OP', 'PBB HARUS DIBAYAR (Rp)', 'STATUS_BAYAR']].copy()
            df_tabel_admin.columns = ['NOP', 'NAMA WAJIB PAJAK', 'ALAMAT OBJEK', 'TAGIHAN PBB', 'STATUS PEMBAYARAN']
            st.dataframe(df_tabel_admin, use_container_width=True, hide_index=True)
            
            st.write("#### 🖨️ Panel Cetak Kwitansi Otomatis")
            warga_lunas_opsi = df_filtered_admin[df_filtered_admin['STATUS_BAYAR'] == 'LUNAS']['NAMA WP'].unique()
            
            if len(warga_lunas_opsi) > 0:
                pilih_warga_cetak = st.selectbox("Pilih Nama Wajib Pajak yang Sudah Lunas:", warga_lunas_opsi)
                data_cetak = df_filtered_admin[df_filtered_admin['NAMA WP'] == pilih_warga_cetak].iloc[0]
                
                nomor_kwitansi = f"KW-2026/{datetime.now().strftime('%m%d')}/{data_cetak['No']:04d}"
                terbilang_kalimat = angka_ke_terbilang(int(data_cetak['TAGIHAN NUM'])) + " Rupiah"
                tgl_setor_print = data_cetak['TANGGAL_BAYAR'] if data_cetak['TANGGAL_BAYAR'] else datetime.now().strftime("%d/%m/%Y")
                
                teks_kwitansi_full = f"""============================================================
              PEMERINTAH KABUPATEN LAMPUNG TIMUR
                     KECAMATAN PEKALONGAN
               KANTOR KEPALA DESA GONDANGREJO
============================================================
                     BUKTI TANDA TERIMA
             PAJAK BUMI DAN BANGUNAN (PBB) - 2026
------------------------------------------------------------
No. Kwitansi  : {nomor_kwitansi}
Tanggal Cetak : {datetime.now().strftime('%d %B %Y')}

Telah terima pembayaran PBB dari Wajib Pajak:
 Nama WP      : {data_cetak['NAMA WP']}
 NOP          : {data_cetak['NOP']}
 Alamat OP    : {data_cetak['ALAMAT OP']}
 Wilayah      : {data_cetak['DUSUN_CLEAN']}

Rincian Objek Pajak:
 - Luas Bumi   : {data_cetak['LUAS BUMI NUM']:,} m²
 - Luas Bng    : {data_cetak['LUAS BNG NUM']:,} m²
------------------------------------------------------------
TOTAL PEMBAYARAN : Rp {data_cetak['TAGIHAN NUM']:,}
Terbilang        : {terbilang_kalimat}
------------------------------------------------------------
Status Pembayaran: [ L U N A S / S A H ]
Setoran Tanggal  : {tgl_setor_print}

                               Gondangrejo, {datetime.now().strftime('%d %B %Y')}
                               Kolektor/Pamong Desa,


                               ( _____________________ )
============================================================
*Bukti ini merupakan tanda terima sah tingkat desa*""".replace(",", ".")

                st.markdown(f"""
                <div id="area-cetak-kwitansi">
                    <pre class='kwitansi-box'>{teks_kwitansi_full}</pre>
                </div>
                """, unsafe_allow_html=True)
                
                st.components.v1.html("""
                    <button onclick="window.print()" style="
                        width: 100%; 
                        background: linear-gradient(45deg, #00f5d4, #7b2cbf); 
                        color: white; 
                        border: none; 
                        padding: 12px; 
                        font-weight: bold; 
                        border-radius: 8px; 
                        cursor: pointer;
                        box-shadow: 0 4px 15px rgba(0, 245, 212, 0.3);
                    ">🖨️ LINK KE PRINTER (CETAK INSTAN)</button>
                """, height=55)
                
                st.write("---")
                st.text_area("Salin teks kwitansi jika ingin di-share lewat WhatsApp saja:", teks_kwitansi_full, height=120)
            else:
                st.warning("Pilih opsi 'Semua Warga' atau 'Hanya yang Sudah Setor' di atas untuk menampilkan daftar nama wajib pajak.")
            
            csv_data = df_tabel_admin.to_csv(index=False).encode('utf-8')
            st.download_button(
                label=f"📥 DOWNLOAD DATA REKAP {filter_bayar_opsi.upper()}",
                data=csv_data,
                file_name=f"rekap_pbb_{pilihan_kategori.lower().replace(' ', '_')}.csv",
                mime='text/csv'
            )
        else:
            st.write("Tidak ada data warga dalam kategori filter ini.")

    elif password != "":
        st.error("Kode Otorisasi Salah! Akses Panel Rekap Ditolak.")
