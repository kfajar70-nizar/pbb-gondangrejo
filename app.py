import streamlit as st
import pandas as pd

# 1. SETTING HALAMAN WEB
st.set_page_config(page_title="PBB Gondangrejo 2026", layout="centered")

# Fungsi untuk memuat data CSV
@st.cache_data
def load_data():
    # Membaca data master (melewati 4 baris pertama sesuai format file kamu)
    df = pd.read_csv("Data_Master.csv", skiprows=4)
    # Membersihkan nama kolom dari spasi yang tidak sengaja ketik
    df.columns = df.columns.str.strip()
    return df

try:
    df_master = load_data()
except Exception as e:
    st.error(f"Gagal membaca file 'Data_Master.csv'. Pastikan file sudah diupload ke GitHub. Error: {e}")
    st.stop()

# 2. SELEKSI LOGIN DI SIDEBAR
st.sidebar.title("Akses Sistem")
pilihan_login = st.sidebar.radio("Masuk Sebagai:", ["Warga / Kolektor (User)", "Pamong Desa (Admin)"])

# 3. LOGIKA UNTUK USER (HANYA CEK NOP)
if pilihan_login == "Warga / Kolektor (User)":
    st.title("🔍 Cek Pajak PBB Desa Gondangrejo 2026")
    st.write("Silakan masukkan nomor Blok dan nomor Urut NOP Anda.")
    
    # Kolom Input berdampingan
    col1, col2 = st.columns(2)
    with col1:
        input_blok = st.text_input("Masukkan Nomor Blok (Contoh: 5)", key="user_blok")
    with col2:
        input_no = st.text_input("Masukkan Nomor Urut (Contoh: 164)", key="user_no")
        
    if st.button("CARI DATA PBB", type="primary"):
        if input_blok and input_no:
            # Format angka agar pas dengan format NOP di data master (misal: '005' dan '0164')
            blok_formatted = input_blok.zfill(3)
            no_formatted = input_no.zfill(4)
            
            pola_cari = f".{blok_formatted}.{no_formatted}."
            
            # Mencari data berdasarkan potongan NOP
            hasil = df_master[df_master['NOP'].str.contains(pola_cari, na=False, regex=False)]
            
            if not hasil.empty:
                data = hasil.iloc[0]
                st.success(f"Data Ditemukan!")
                
                # Menampilkan data secara rapi
                st.write(f"**NOP Penuh:** {data['NOP']}")
                st.subheader(f"👤 {data['NAMA WP']}")
                st.write(f"🏠 **Alamat Objek Pajak:** {data['ALAMAT OP']}")
                st.write(f"📐 **Luas Bumi / Bangunan:** {data['LUAS BUMI']} m² / {data['LUAS BNG']} m²")
                st.markdown(f"### 💰 PBB Harus Dibayar: **Rp {data['PBB HARUS DIBAYAR (Rp)']}**")
            else:
                st.error("Data NOP tidak ditemukan! Periksa kembali nomor Blok dan Urut yang Anda masukkan.")
        else:
            st.warning("Mohon isi kedua kolom input di atas!")

# 4. LOGIKA UNTUK ADMIN
elif pilihan_login == "Pamong Desa (Admin)":
    st.title("⚙️ Panel Admin - PBB Desa Gondangrejo")
    
    password = st.text_input("Masukkan Password Admin:", type="password")
    if password == "gondangrejo2026": # Anda bisa mengganti password ini nanti
        st.success("Selamat Datang, Admin!")
        st.info("Fitur Admin untuk mengubah data (Dusun, Setor, Hapus) akan kita aktifkan setelah tampilan pencarian ini berhasil berjalan.")
    elif password != "":
        st.error("Password Salah!")
