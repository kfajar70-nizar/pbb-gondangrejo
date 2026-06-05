import streamlit as st
import pandas as pd
import os

# 1. SETTING HALAMAN WEB
st.set_page_config(page_title="PBB Gondangrejo 2026", layout="centered")

# Nama file database lokal di server
FILE_DATA = "Data_Master.csv"

# Fungsi untuk memuat data
def load_data():
    if os.path.exists(FILE_DATA):
        # Membaca data master (melewati 4 baris pertama sesuai format file kamu)
        df = pd.read_csv(FILE_DATA, skiprows=4)
        df.columns = df.columns.str.strip()
        return df
    else:
        st.error("File 'Data_Master.csv' tidak ditemukan!")
        st.stop()

# Memuat data ke dalam session state agar perubahan data bisa tersimpan selama aplikasi berjalan
if 'df_master' not in st.session_state:
    st.session_state.df_master = load_data()

df_master = st.session_state.df_master

# 2. SELEKSI LOGIN DI SIDEBAR
st.sidebar.title("Akses Sistem")
pilihan_login = st.sidebar.radio("Masuk Sebagai:", ["Warga / Kolektor (User)", "Pamong Desa (Admin)"])

# 3. LOGIKA UNTUK USER (HANYA CEK NOP)
if pilihan_login == "Warga / Kolektor (User)":
    st.title("🔍 Cek Pajak PBB Desa Gondangrejo 2026")
    st.write("Silakan masukkan nomor Blok dan nomor Urut NOP Anda.")
    
    col1, col2 = st.columns(2)
    with col1:
        input_blok = st.text_input("Masukkan Nomor Blok (Contoh: 5)", key="user_blok")
    with col2:
        input_no = st.text_input("Masukkan Nomor Urut (Contoh: 164)", key="user_no")
        
    if st.button("CARI DATA PBB", type="primary"):
        if input_blok and input_no:
            blok_formatted = input_blok.zfill(3)
            no_formatted = input_no.zfill(4)
            pola_cari = f".{blok_formatted}.{no_formatted}."
            
            hasil = df_master[df_master['NOP'].str.contains(pola_cari, na=False, regex=False)]
            
            if not hasil.empty:
                data = hasil.iloc[0]
                st.success(f"Data Ditemukan!")
                
                # Menampilkan data secara rapi
                st.write(f"**NOP Penuh:** {data['NOP']}")
                st.subheader(f"👤 {data['NAMA WP']}")
                st.write(f"🏠 **Alamat Objek Pajak:** {data['ALAMAT OP']}")
                st.write(f"📐 **Luas Bumi / Bangunan:** {data['LUAS BUMI']} m² / {data['LUAS BNG']} m²")
                
                # Menampilkan Status dari Kolom Terkait (Mengikuti logika VBA)
                status_dusun = data.iloc[0] if not pd.isna(data.iloc[0]) else "Belum diinput kolektor"
                st.info(f"📍 **Status Kolektor:** {status_dusun}")
                
                # Menampilkan Nominal Pajak
                st.markdown(f"### 💰 PBB Harus Dibayar: **Rp {data['PBB HARUS DIBAYAR (Rp)']}**")
            else:
                st.error("Data NOP tidak ditemukan! Periksa kembali nomor Blok dan Urut.")
        else:
            st.warning("Mohon isi kedua kolom input di atas!")

# 4. LOGIKA UNTUK ADMIN
elif pilihan_login == "Pamong Desa (Admin)":
    st.title("⚙️ Panel Admin - PBB Desa Gondangrejo")
    
    password = st.text_input("Masukkan Password Admin:", type="password")
    if password == "gondangrejo2026":
        st.success("Selamat Datang, Admin!")
        
        st.write("---")
        st.subheader("📝 Update Status Pembayaran / Kolektor Dusun")
        
        # Input data NOP yang mau diupdate
        col1, col2 = st.columns(2)
        with col1:
            admin_blok = st.text_input("Nomor Blok Data target", key="adm_blok")
        with col2:
            admin_no = st.text_input("Nomor Urut Data target", key="adm_no")
            
        if admin_blok and admin_no:
            b_form = admin_blok.zfill(3)
            n_form = admin_no.zfill(4)
            pola_admin = f".{b_form}.{n_form}."
            
            idx_hasil = df_master[df_master['NOP'].str.contains(pola_admin, na=False, regex=False)].index
            
            if len(idx_hasil) > 0:
                idx = idx_hasil[0]
                data_target = df_master.loc[idx]
                
                st.write(f"**Data Ditemukan:** {data_target['NAMA WP']} ({data_target['ALAMAT OP']})")
                st.write(f"**Tagihan:** Rp {data_target['PBB HARUS DIBAYAR (Rp)']}")
                
                # Pilihan Aksi (Sama seperti logika ganti warna/status di VBA kamu)
                aksi = st.selectbox("Pilih Status Baru:", ["Pilih Aksi...", "Input Kolektor Dusun", "Setor Pembayaran", "Hapus/Batalkan Data"])
                
                if aksi == "Input Kolektor Dusun":
                    nomor_dusun = st.number_input("Dusun Ke- (1-10):", min_value=1, max_value=10, value=1)
                    if st.button("Simpan Status Dusun"):
                        # Mengubah nilai di kolom pertama (indeks 0) seperti logika VBA kamu (.Value = "OK-Dusun_X")
                        df_master.iloc[idx, 0] = f"OK-Dusun_{nomor_dusun}"
                        st.session_state.df_master = df_master
                        st.success(f"Berhasil mengupdate status menjadi OK-Dusun_{nomor_dusun}!")
                        
                elif aksi == "Setor Pembayaran":
                    if st.button("Tandai Sudah Setor"):
                        # Menambahkan status "SUDAH SETOR" di kolom status setoran (kolom P / indeks ke 15 di file kamu)
                        if len(df_master.columns) >= 16:
                            df_master.iloc[idx, 15] = "SUDAH SETOR"
                            st.session_state.df_master = df_master
                            st.success("Berhasil! Data ditandai SUDAH SETOR.")
                        else:
                            st.error("Kolom setoran tidak ditemukan pada struktur file CSV.")
                            
                elif aksi == "Hapus/Batalkan Data":
                    if st.button("Proses Hapus", type="secondary"):
                        df_master.iloc[idx, 0] = "HAPUS"
                        st.session_state.df_master = df_master
                        st.error("Data telah ditandai HAPUS.")
            else:
                st.warning("Data NOP tidak ditemukan untuk input tersebut.")
                
    elif password != "":
        st.error("Password Salah!")
