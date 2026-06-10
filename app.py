import streamlit as st
import pandas as pd
import os
import re
import urllib.parse

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
    h2, h3 {
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
    label {
        color: #00f5d4 !important;
        font-weight: 600 !important;
    }
</style>
""", unsafe_allow_html=True)

# ==========================================
# AUTOMATIC DATA LOADING & MULTI-WA CONFIG
# ==========================================
CSV_FILE_NAME = "data_pbb.csv"

# 🟢 SILAKAN GANTI NOMOR DI BAWAH INI (Awali dengan 62, jangan pakai 0 atau +)
DAFTAR_WA_KOLEKTOR = {
    "Dusun 1": "6281279771829",
    "Dusun 2": "6285367665490",
    "Dusun 3": "62895615741400",
    "Dusun 4": "6282177680623",
    "Dusun 5": "6285269879548",
    "Dusun 6": "6285279366615",
    "Dusun 7": "6281324518763",
    "Dusun 8": "6285382657636",
    "Dusun 9": "6285381027147",
    "Dusun 10": "6281272359303",
    "PUSAT_ADMIN": "6285695557674" # <-- Nomor ke-11 untuk Belum Terinput, Hapus, BPN, dll.
}

def format_clean_luas(val):
    if pd.isna(val):
        return 0
    
    # Ubah ke string, bersihkan spasi, dan hilangkan koma jika ada
    val_str = str(val).strip().replace(',', '')
    
    # Jika data kosong atau berisi penanda khusus lapangan seperti 'XXX'
    if val_str.upper() == 'XXX' or val_str == '' or val_str == '0':
        return 0
    
    try:
        # LOGIKA PERBAIKAN FORMAT LUAS PBB INDONESIA
        if '.' in val_str:
            parts = val_str.split('.')
            depan = parts[0]
            belakang = parts[1]
            
            # Kasus 1: Jika belakangnya 1 digit (misal: 9.8 -> 980)
            if len(belakang) == 1:
                return int(depan + belakang + "0")
            
            # Kasus 2: Jika belakangnya 2 digit (misal: 2.05 -> 2050)
            elif len(belakang) == 2:
                return int(depan + belakang + "0")
            
            # Kasus 3: Jika belakangnya 3 digit, itu adalah ribuan murni (misal: 3.125 -> 3125)
            elif len(belakang) == 3:
                return int(depan + belakang)
                
        # Jika berupa angka bulat tanpa titik sama sekali
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
st.sidebar.markdown("<div style='text-align: center; font-size: 0.8rem; color: #8d99ae;'><b>PBB GONDANGREJO v7.6</b><br>Multi-Routing WA Kolektor © 2026</div>", unsafe_allow_html=True)

# ==========================================
# 1. PORTAL WARGA / USER INTERFACE
# ==========================================
if pilihan_login == "Portal Warga (User)":
    st.markdown("<h1> DIGITAL CEK PBB GONDANGREJO</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align:center; color:#8d99ae;'>Sistem Pencarian Cepat Objek Pajak Bumi & Bangunan</p>", unsafe_allow_html=True)
    st.write("")
    
    col1, col2 = st.columns(2)
    with col1:
        input_blok = st.text_input("📡 KODE BLOK / DUSUN", placeholder="Contoh: 8", key="user_blok")
    with col2:
        input_no = st.text_input("🔢 NOMOR URUT NOP", placeholder="Contoh: 11", key="user_no")
        
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
                    
                    # 🎯 LOGIKA FILTERING MULTI-NOMOR WHATSAPP
                    if v_status in DAFTAR_WA_KOLEKTOR:
                        nomor_wa_tujuan = DAFTAR_WA_KOLEKTOR[v_status]
                        label_kolektor = f"HUBUNGI KOLEKTOR {v_status.upper()}"
                    else:
                        nomor_wa_tujuan = DAFTAR_WA_KOLEKTOR["PUSAT_ADMIN"]
                        label_kolektor = f"HUBUNGI PUSAT DATA (STATUS: {v_status.upper()})"
                    
                    # Susun teks pesan otomatis khusus
                    pesan_wa = f"Halo Pamong Desa Gondangrejo, saya ingin mengonfirmasi/membayar PBB atas nama {v_nama}.\n\nBerikut data Objek Pajak saya:\n- NOP: {v_nop}\n- Alamat OP: {v_alamat}\n- Tagihan: Rp {v_bayar:,}\n- Status Lapangan: {v_status}\n\nMohon petunjuk pembayarannya, terima kasih!".replace(",", ".")
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
    
    password = st.text_input("MASUKKAN KODE OTORISASI (PASSWORD):", type="password")
    if password == "1234":
        st.success("🔒 Akses Diterima. Dashboard Rekap Terbuka.")
        
        # Perhitungan Data Global
        total_wp = len(df_master)
        total_target_pbb = df_master['TAGIHAN NUM'].sum()
        total_luas_bumi = df_master['LUAS BUMI NUM'].sum()
        total_luas_bng = df_master['LUAS BNG NUM'].sum()
        
        # Indikator Progress Input
        sudah_input_wp = len(df_master[~df_master['DUSUN_CLEAN'].isin(["BELUM TERINPUT", "HAPUS", "BPN"])])
        persentase_progres = (sudah_input_wp / total_wp) if total_wp > 0 else 0
        
        st.write("### ⚡ PROGRES VALIDASI WILAYAH DUSUN")
        st.progress(persentase_progres)
        st.markdown(f"<p style='color:#00f5d4; font-weight:bold;'>📈 {sudah_input_wp:,} dari {total_wp:,} WP ({persentase_progres*100:.1f}%) Data Warga Sudah Terdistribusi ke 10 Dusun.</p>".replace(",", "."), unsafe_allow_html=True)
        st.write("")

        # Ringkasan Global
        st.write("### 🌌 RINGKASAN GLOBAL DESA GONDANGREJO")
        m_col1, m_col2 = st.columns(2)
        with m_col1:
            st.markdown(f"""
            <div class="futuristic-card" style="text-align: center;">
                <span style="color:#8d99ae; font-size:0.9rem;">👥 TOTAL WAJIB PAJAK</span><br>
                <span style="font-size:1.8rem; color:#00f5d4; font-weight:bold;">{total_wp:,} WP</span>
            </div>
            """.replace(",", "."), unsafe_allow_html=True)
            st.markdown(f"""
            <div class="futuristic-card" style="text-align: center;">
                <span style="color:#8d99ae; font-size:0.9rem;">📐 TOTAL LUAS BUMI DESA</span><br>
                <span style="font-size:1.8rem; color:#fff; font-weight:bold;">{total_luas_bumi:,} m²</span>
            </div>
            """.replace(",", "."), unsafe_allow_html=True)
        with m_col2:
            st.markdown(f"""
            <div class="futuristic-card" style="text-align: center;">
                <span style="color:#8d99ae; font-size:0.9rem;">💰 TOTAL TARGET KETETAPAN PBB</span><br>
                <span style="font-size:1.8rem; color:#00f5d4; font-weight:bold;">Rp {total_target_pbb:,}</span>
            </div>
            """.replace(",", "."), unsafe_allow_html=True)
            st.markdown(f"""
            <div class="futuristic-card" style="text-align: center;">
                <span style="color:#8d99ae; font-size:0.9rem;">🏢 TOTAL LUAS BANGUNAN DESA</span><br>
                <span style="font-size:1.8rem; color:#fff; font-weight:bold;">{total_luas_bng:,} m²</span>
            </div>
            """.replace(",", "."), unsafe_allow_html=True)

        # Top 5 Ketetapan PBB
        st.write("### 👑 TOP 5 ASSET KETETAPAN PBB TERBESAR SE-DESA")
        df_top5 = df_master.nlargest(5, 'TAGIHAN NUM')[['NOP', 'NAMA WP', 'LUAS BUMI', 'PBB HARUS DIBAYAR (Rp)']]
        df_top5.columns = ['NOP', 'NAMA WAJIB PAJAK', 'LUAS BUMI', 'NILAI TAGIHAN']
        st.dataframe(df_top5, use_container_width=True, hide_index=True)

        # Rekap Per Wilayah Dusun
        st.write("### 📊 REKAPITULASI TARGET PER WILAYAH DUSUN")
        df_rekap_dusun = df_master.groupby('DUSUN_CLEAN').agg(
            Jumlah_WP=('NOP', 'count'),
            Total_Target_PBB=('TAGIHAN NUM', 'sum')
        ).reset_index()
        df_rekap_dusun = df_rekap_dusun.sort_values(by='DUSUN_CLEAN')
        st.bar_chart(data=df_rekap_dusun, x='DUSUN_CLEAN', y='Total_Target_PBB', color='#9b5de5')

        # Validator detail nama (By Name)
        st.write("---")
        st.write("### 🔍 VALIDATOR DATA LAPANGAN (BY NAME)")
        st.write("Pilih kategori di bawah untuk melihat rincian nama wajib pajak secara mendetail.")

        list_kategori = sorted(df_master['DUSUN_CLEAN'].unique())
        pilihan_kategori = st.selectbox("📁 PILIH KATEGORI VALIDASI STATUS:", list_kategori)
        
        df_filtered_admin = df_master[df_master['DUSUN_CLEAN'] == pilihan_kategori]
        sub_wp = len(df_filtered_admin)
        sub_uang = df_filtered_admin['TAGIHAN NUM'].sum()
        
        st.info(f"📊 Kategori **{pilihan_kategori}** memiliki **{sub_wp:,} Objek Pajak** dengan total ketetapan **Rp {sub_uang:,}**".replace(",", "."))
        
        if not df_filtered_admin.empty:
            df_tabel_admin = df_filtered_admin[['NOP', 'NAMA WP', 'ALAMAT OP', 'LUAS BUMI', 'PBB HARUS DIBAYAR (Rp)']].copy()
            df_tabel_admin.columns = ['NOP', 'NAMA WAJIB PAJAK', 'ALAMAT OBJEK', 'LUAS TANAH', 'TAGIHAN PBB']
            st.dataframe(df_tabel_admin, use_container_width=True, hide_index=True)
            
            csv_data = df_tabel_admin.to_csv(index=False).encode('utf-8')
            st.download_button(
                label=f"📥 DOWNLOAD DATA REKAP ({pilihan_kategori.upper()})",
                data=csv_data,
                file_name=f"rekap_pbb_{pilihan_kategori.lower().replace(' ', '_')}.csv",
                mime='text/csv'
            )
        else:
            st.write("Tidak ada data dalam kategori ini.")

    elif password != "":
        st.error("Kode Otorisasi Salah! Akses Panel Rekap Ditolak.")
