import streamlit as st
import pandas as pd
import os

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
    label {
        color: #00f5d4 !important;
        font-weight: 600 !important;
    }
</style>
""", unsafe_allow_html=True)

# ==========================================
# AUTOMATIC DATA LOADING FROM LOCAL CSV
# ==========================================
CSV_FILE_NAME = "data_pbb.csv"

def format_clean_luas(val):
    if pd.isna(val):
        return 0
    val_str = str(val).strip()
    if '.' in val_str:
        parts = val_str.split('.')
        if len(parts[1]) == 1:
            return int(parts[0] + parts[1] + "00")
        elif len(parts[1]) == 2:
            return int(parts[0] + parts[1] + "0")
        else:
            return int(parts[0] + parts[1])
    try:
        # Bersihkan titik ribuan bawaan excel jika ada
        val_str = val_str.replace('.', '')
        return int(val_str)
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

def load_local_data():
    if not os.path.exists(CSV_FILE_NAME):
        st.error(f"⚠️ File '{CSV_FILE_NAME}' tidak ditemukan di GitHub kamu!")
        st.stop()
    try:
        # Membaca data lokal
        df = pd.read_csv(CSV_FILE_NAME, skiprows=4)
        df.columns = df.columns.str.strip()
        
        # Bersihkan kolom-kolom penting ke tipe angka agar bisa dijumlahkan (rekap)
        df['LUAS BUMI NUM'] = df['LUAS BUMI'].apply(format_clean_luas)
        df['LUAS BNG NUM'] = df['LUAS BNG'].apply(format_clean_luas)
        df['TAGIHAN NUM'] = df['PBB HARUS DIBAYAR (Rp)'].apply(format_clean_rupiah)
        
        # Ekstrak Kode Blok otomatis dari string NOP (misal ke-5 setelah titik: 18.10.080.003.XXX)
        def ambil_blok(nop_val):
            try:
                parts = str(nop_val).split('.')
                return parts[4] if len(parts) > 4 else "Lainnya"
            except:
                return "Lainnya"
        df['BLOK_CODE'] = df['NOP'].apply(ambil_blok)
        
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
st.sidebar.markdown("<div style='text-align: center; font-size: 0.8rem; color: #8d99ae;'><b>PBB GONDANGREJO v7.0</b><br>Database Lokal CSV + Rekap © 2026</div>", unsafe_allow_html=True)

# ==========================================
# 1. PORTAL WARGA / USER INTERFACE
# ==========================================
if pilihan_login == "Portal Warga (User)":
    st.markdown("<h1> DIGITAL CEK PBB GONDANGREJO</h1>", unsafe_allow_html=True)
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
                    v_status = data.iloc[0] if not pd.isna(data.iloc[0]) else "Belum Diinput"
                    
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
                    </div>
                    """.replace(",", "."), unsafe_allow_html=True)
                else:
                    st.error("Gagal Menemukan Data! Kombinasi Kode Blok dan Nomor Urut tersebut tidak ditemukan.")
        else:
            st.warning("Sistem memerlukan Kode Blok dan Nomor Urut untuk melakukan pencarian.")

# ==========================================
# 2. PORTAL PAMONG / ADMIN INTERFACE (DASHBOARD REKAP)
# ==========================================
elif pilihan_login == "Pamong Desa (Admin)":
    st.markdown("<h1>⚙️ CONTROL PANEL & REKAP DESA</h1>", unsafe_allow_html=True)
    
    password = st.text_input("MASUKKAN KODE OTORISASI (PASSWORD):", type="password")
    if password == "gondangrejo2026":
        st.success("🔒 Akses Diterima. Dashboard Rekap Terbuka.")
        
        # --- LOGIKA HITUNG DATA REKAP ---
        total_wp = len(df_master)
        total_target_pbb = df_master['TAGIHAN NUM'].sum()
        total_luas_bumi = df_master['LUAS BUMI NUM'].sum()
        total_luas_bng = df_master['LUAS BNG NUM'].sum()
        
        # --- UI TAMPILAN KARTU RINGKASAN ---
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

        # --- REKAP PER BLOK / KODE BLOK ---
        st.write("### 📊 REKAPITULASI TARGET PER KODE BLOK")
        
        # Kelompokkan data berdasarkan Kode Blok dari NOP
        df_rekap_blok = df_master.groupby('BLOK_CODE').agg(
            Jumlah_WP=('NOP', 'count'),
            Total_Luas_Bumi=('LUAS BUMI NUM', 'sum'),
            Total_Target_PBB=('TAGIHAN NUM', 'sum')
        ).reset_index()
        
        # Urutkan berdasarkan Kode Blok biar rapi
        df_rekap_blok = df_rekap_blok.sort_values(by='BLOK_CODE')
        
        # Beri format tampilan ribuan pada tabel rekap agar enak dibaca Admin
        df_tampilan_rekap = df_rekap_blok.copy()
        df_tampilan_rekap['Jumlah_WP'] = df_tampilan_rekap['Jumlah_WP'].map('{:,}'.format).str.replace(',', '.')
        df_tampilan_rekap['Total_Luas_Bumi'] = df_tampilan_rekap['Total_Luas_Bumi'].map('{:,} m²'.format).str.replace(',', '.')
        df_tampilan_rekap['Total_Target_PBB'] = df_tampilan_rekap['Total_Target_PBB'].map('Rp {:,}'.format).str.replace(',', '.')
        df_tampilan_rekap.columns = ['KODE BLOK', 'JUMLAH WP', 'TOTAL LUAS BUMI', 'TOTAL TARGET TAGIHAN PBB']
        
        # Tampilkan tabel data interaktif
        st.dataframe(df_tampilan_rekap, use_container_width=True, hide_index=True)
        
        # Tambahan Fitur: Grafik Bar untuk Target Pajak per Blok
        st.write("📈 **Grafik Perbandingan Target PBB Antar Blok (Rp)**")
        st.bar_chart(data=df_rekap_blok, x='BLOK_CODE', y='Total_Target_PBB', color='#00f5d4')

    elif password != "":
        st.error("Kode Otorisasi Salah! Akses Panel Rekap Ditolak.")
