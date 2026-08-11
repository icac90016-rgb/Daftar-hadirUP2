import streamlit as st
import pandas as pd
from datetime import datetime, timedelta, timezone
import os
import base64

NAMA_FILE_DATA = "data_absen.csv"

# =========================================================================
# 🎨 PERBAIKAN STRUKTUR CSS: MEMAKSA LAYAR KAMERA HP SISWA AGAR TIDAK MIRROR
# =========================================================================
st.markdown(
    """
    <style>
    /* Menghilangkan efek cermin pada video pratinjau kamera depan HP/Laptop */
    div[data-testid="stCameraInput"] video {
        transform: scaleX(-1) !important;
        -webkit-transform: scaleX(-1) !important;
    }
    /* Membalikkan hasil jepretan foto setelah diambil agar tetap lurus & tidak mirror */
    div[data-testid="stCameraInput"] img {
        transform: scaleX(-1) !important;
        -webkit-transform: scaleX(-1) !important;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# --- CONFIG LOGO LOKAL ---
LINK_LOGO = "logo.png"
col_logo1, col_logo2, col_logo3 = st.columns(3)

with col_logo2:
    try:
        st.image(LINK_LOGO, width=130)
    except Exception:
        pass

# --- HEADER TAMPILAN WEB ---
st.title("📱 Presensi Digital Anggota UP")
st.markdown("Selamat datang di sistem absensi mandiri jurusan TJKT. Silakan isi data Anda dengan benar.")
st.markdown("---")

# =========================================================================
# 📋 DATA MASTER ASLI: KELAS -> DAFTAR NAMA ANGGOTA (X TJKT 1, 2, 3)
# =========================================================================
DATA_MASTER = {
    "X TJKT 1": [
        "Alvira Adzani", "Al Bargas Bihaqqi", "Anwar Hidayat", "Ayu Azkia",
        "Callysta Putri Azalia", "Cahyani Keyla Salsabila", "Gio Fadylan Praditya",
        "Jihan Hemilia F.", "Kukuh Bagus M.", "Muhammad Fatih Randri",
        "Muhammad Irfan Alfahrezi", "Najmi Al Kautsar", "Rafael Hermawan",
        "Reno Wahyu Anggito", "Rihel Olivia", "Saniyyatus Salwa",
        "Salsabiluna", "Syakira Naima P.", "Zia Rezky Anindya",
        "Za'iim Ahmad", "Vega Riyanti", "Zahra Indah Ningrum"
    ],
    "X TJKT 2": [
        "Agnes Humaira A.", "Airin Rahcmy Diany", "Alana Bahira Ramadhani",
        "Dea Ananda Putri", "Kia Sakila Putri Awazra", "Marvella Tiffany Wijaya",
        "Meshitah Zeny", "Muhammad Genta Antariska", "Muhammad Rizky Permana Putra",
        "Muhamad Rasya Fadilah", "Nasya Aliya", "Nur Asyifa Syabilla",
        "Princesse Morauli", "Syahirah Az-Zahra", "Samuel Lukman"
    ],
    "X TJKT 3": [
        "Adit Bima Saputra", "Aldi Apriliansyah", "Al Fattach Maulan Muslim",
        "Alif Dzaki Mubarok", "Anggara Safutra", "Ayra Maulida", "Balqis Adzra Sakhi",
        "Cornelius Armagan Adyatma KK", "Deby Natalia", "Dion Prayoga",
        "Dzulaikha Nur Alisya Ramadhani", "Harum Aryanti", "Jasyiyah Vania Ryandra",
        "Khafatunida Az-Zahra", "Muhammad Rizky Ramadhan", "Napila Nur Azizah",
        "Nikita Leonardi", "Rafly Prasetio", "Regata Katra Yuda",
        "Thoriq Adli Nugraha", "Aqila Nafisah Belva", "Rizky pangestu",
        "Alfirah Rinandra Dewy", "Syakila Khairunnisa"     
    ]
}

pilihan_kelas = st.selectbox("🏫 Pilih Kelas Anda: *", ["-- Pilih Kelas --"] + list(DATA_MASTER.keys()))

if pilihan_kelas != "-- Pilih Kelas --":
    pilihan_nama = st.selectbox("👤 Pilih Nama Lengkap Anda: *", ["-- Pilih Nama --"] + DATA_MASTER[pilihan_kelas])
else:
    pilihan_nama = st.selectbox("👤 Pilih Nama Lengkap Anda: *", ["-- Silakan Pilih Kelas Terlebih Dahulu --"], disabled=True)

no_telp = st.text_input(
    "📞 Masukkan Nomor WhatsApp/Telepon Aktif: *",
    placeholder="Contoh: 081234567890"
)
status = st.selectbox("📌 Status Kehadiran: *", ["Hadir", "Izin", "Sakit"])

# Peringatan tegas aturan foto terbaru
st.error(
    "🚨 **INFORMASI ATURAN FOTO:**\n"
    "*   Jika status **Hadir**, pastikan posisi wajah terlihat terang dan jelas.\n"
    "*   **Jika foto/data tidak sesuai otomatis alva!**"
)

foto_kamera = st.camera_input("📸 Ambil Foto Diri / Bukti Surat (Wajib Live): *")
st.write("")

# --- TOMBOL EXECUTE ABSENSI ---
if st.button("🚀 Kirim Kehadiran Anda", use_container_width=True):
    bersih_telp = no_telp.strip()
    zona_wib = timezone(timedelta(hours=7))
    waktu_objek = datetime.now(zona_wib)
    tanggal_hari_ini = waktu_objek.strftime("%Y-%m-%d")
    waktu_lengkap = waktu_objek.strftime("%Y-%m-%d %H:%M:%S")

    if (
        pilihan_kelas == "-- Pilih Kelas --"
        or pilihan_nama == "-- Pilih Nama --"
        or bersih_telp == ""
        or foto_kamera is None
    ):
        st.error("⚠️ Gagal mengirim! Mohon pastikan Kelas, Nama, Nomor Telepon, dan Foto Live Kamera sudah terisi.")
    elif not bersih_telp.isdigit() or len(bersih_telp) < 10 or len(bersih_telp) > 13:
        st.error("⚠️ Format Salah! Periksa kembali nomor telepon Anda (wajib 10-13 digit angka saja).")
    else:
        with st.spinner("⏳ Sistem sedang memproses data presensi Anda..."):
            try:
                data_gambar = foto_kamera.getvalue()

                # FILTER PIKSEL MANDIRI ANTI JARI / LANTAI GELAP
                rata_rata_warna = sum(data_gambar) / len(data_gambar)

                if status == "Hadir" and rata_rata_warna < 45.0:
                    st.error("🛑 Gagal Dikirim! Sistem mendeteksi foto Anda terlalu gelap, hitam polos, atau kamera sengaja ditutup jari/meja. Silakan posisikan wajah Anda di tempat terang lalu jepret ulang!")
                else:
                    base64_foto = base64.b64encode(data_gambar).decode("utf-8")
                    string_foto_excel = f"data:image/png;base64,{base64_foto}"

                    data_baru = pd.DataFrame({
                        "Waktu Absen": [waktu_lengkap],
                        "Kelas": [pilihan_kelas],
                        "Nama": [pilihan_nama],
                        "No Telepon": [bersih_telp],
                        "Data Foto Bukti (Base64)": [string_foto_excel],
                        "Status": [status]
                    })

                    if os.path.exists(NAMA_FILE_DATA):
                        df_total = pd.read_csv(NAMA_FILE_DATA)
                        if not df_total.empty:
                            df_total["Tanggal_Cek"] = df_total["Waktu Absen"].str.slice(0, 10)
                            indeks_lama = df_total[
                                (df_total["Tanggal_Cek"] == tanggal_hari_ini)
                                & (df_total["Kelas"] == pilihan_kelas)
                                & (df_total["Nama"] == pilihan_nama)
                            ].index
                            df_total = df_total.drop(columns=["Tanggal_Cek"], errors="ignore")

                            if not indeks_lama.empty:
                                df_total.loc[indeks_lama] = [waktu_lengkap, pilihan_kelas, pilihan_nama, bersih_telp, string_foto_excel, status]
                                st.success(f"🔄 Data absensi harian untuk '{pilihan_nama}' berhasil diperbarui ke yang terbaru!")
                            else:
                                df_total = pd.concat([df_total, data_baru], ignore_index=True)
                                st.success(f"✨ Berhasil mencatat kehadiran untuk: {pilihan_nama} ({pilihan_kelas})")
                        else:
                            df_total = data_baru
                            st.success(f"✨ Berhasil mencatat kehadiran untuk: {pilihan_nama} ({pilihan_kelas})")
                    else:
                        df_total = data_baru
                        st.success(f"✨ Berhasil mencatat kehadiran untuk: {pilihan_nama} ({pilihan_kelas})")

                    df_total.to_csv(NAMA_FILE_DATA, index=False)
                    st.balloons()
            except Exception as e:
                st.error(f"❌ Server gagal memproses gambar. Silakan jepret ulang! (Eror: {e})")

# --- MENU ADMIN RAHASIA ---
st.markdown("---")
st.subheader("🔒 Menu Khusus Admin")
password = st.text_input("Masukkan Password Admin untuk membuka rekap:", type="password")

if password == "rahasiaUP2026":
    st.success("🔓 Akses Diterima! Berikut rekap data kehadiran:")
    if os.path.exists(NAMA_FILE_DATA):
        df_cetak = pd.read_csv(NAMA_FILE_DATA)
        st.dataframe(df_cetak.drop(columns=["Data Foto Bukti (Base64)"], errors="ignore"), use_container_width=True)

        st.markdown("**🔍 Intip Foto Hasil Jepretan Siswa:**")
        nama_pilihan_foto = st.selectbox(
            "Pilih nama siswa untuk melihat fotonya:",
            ["-- Pilih Nama --"] + df_cetak["Nama"].unique().tolist()
        )

        if nama_pilihan_foto != "-- Pilih Nama --":
            baris_siswa = df_cetak[df_cetak["Nama"] == nama_pilihan_foto]
            if not baris_siswa.empty:
                raw_foto = baris_siswa["Data Foto Bukti (Base64)"].iloc[0]
                try:
                    st.image(raw_foto, caption=f"Foto Bukti Absen: {nama_pilihan_foto}", width=300)
                except Exception:
                    st.info("Foto siswa ini tidak dapat dimuat.")

        @st.cache_data
        def konversi_ke_excel(df):
            import io
            output = io.BytesIO()
            with pd.ExcelWriter(output, engine="openpyxl") as writer:
                df.to_excel(writer, index=False, sheet_name="Daftar Hadir")
            return output.getvalue()

        data_excel = konversi_ke_excel(df_cetak)
        st.download_button(
            label="📥 Unduh File Excel (Daftar Hadir)",
            data=data_excel,
            file_name="rekap_daftar_hadir.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True
        )

        st.markdown("---")
        st.markdown("**⚙️ Menu Edit/Hapus Data:**")
        daftar_nama_absen = df_cetak["Nama"].unique().tolist()
        nama_yang_dihapus = st.selectbox("Pilih nama yang ingin dihapus:", ["-- Pilih Nama --"] + daftar_nama_absen)

        if st.button("❌ Hapus Nama Ini", use_container_width=True):
            if nama_yang_dihapus != "-- Pilih Nama --":
                df_terupdate = df_cetak[df_cetak["Nama"] != nama_yang_dihapus]
                df_terupdate.to_csv(NAMA_FILE_DATA, index=False)
                st.warning(f"Nama '{nama_yang_dihapus}' telah berhasil dihapus dari server!")
                st.rerun()
elif password != "":
    st.error("🛑 Password Salah! Akses ditolak.")