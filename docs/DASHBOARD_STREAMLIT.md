# Dashboard Streamlit — versi awal

Versi ini menyediakan Beranda, Cari Jurusan, Bandingkan Jurusan, Hasil Pengujian, dan Panduan. Hasil Pengujian menyediakan tiga keadaan jurusan sesuai fondasi versi 2 dan hanya membaca hasil dari versi fondasi terbaru. Perkiraan Peminat menampilkan keterangan bahwa perhitungan baru belum tersedia. Angka eksplorasi dan evaluasi berasal dari data kelompok, bukan contoh buatan.

## Menjalankan

Gunakan Python 3.13 dari akar repo:

```powershell
python -m pip install -r dashboard/requirements.txt
python -m streamlit run dashboard/streamlit_app.py
```

Jika panel belum tersedia, aplikasi menjalankan `src/ambil_data_snpmb.py` dengan snapshot mentah repo. Tidak ada unduhan ulang atau pelatihan model saat startup. Panel hasil tetap berada di `data/olahan/` dan tidak di-commit.

## Deployment awal

Pada Streamlit Community Cloud pilih Create app dan gunakan:

- Repository deployment mandiri: `duhaalul/estimasi-peminat-snpmb` (fork dari repo kelompok)
- Branch: `duha-fondasi-v2`
- Main file path: `dashboard/streamlit_app.py`
- Advanced settings → Python: `3.13`
- Secrets: tidak diperlukan.

Dependensi aplikasi berada di `dashboard/requirements.txt`, di sebelah entry point, sehingga deployment tidak memasang paket pelatihan notebook yang tidak digunakan aplikasi. Tema berada di `.streamlit/config.toml`.

Status dokumen ini: fork tersedia di https://github.com/duhaalul/estimasi-peminat-snpmb dan branch `duha-fondasi-v2` sudah tersinkron. Deployment berhasil diverifikasi pada 2026-11-14: https://snpmb-insight.streamlit.app/ . Beranda dan Hasil Pengujian memuat data fondasi versi 2 pada Python 3.13. Deployment mandiri memakai fork milik Duha. Hasil LR/RF terbaru menunggu integrasi Mikail di repo kelompok, lalu perlu disinkronkan ke fork. Setelah deployment berhasil, push perubahan ke branch yang terhubung akan memperbarui aplikasi.

## Pemeriksaan

- AppTest berhasil membuka keenam menu melalui tombol sidebar; tiga pilihan pada Hasil Pengujian fondasi versi 2 berjalan tanpa exception.
- Startup dari salinan bersih berhasil membangun panel melalui skrip resmi.
- Tampilan desktop diperiksa; bukti `docs/dashboard/beranda.png`.
- Data fakultas dan target kosong dikeluarkan dari tampilan; SNBP dan SNBT terpisah.
- Tahun tanpa observasi tidak diisi; rasio untuk kuota nol/kosong dibiarkan kosong.
- Hasil XGBoost yang belum mengalahkan patokan tahun lalu tetap ditampilkan.

## Batas versi awal

Prediksi baru, model anggota lain, serta rentang prediksi belum diintegrasikan. Uji perangkat seluler dan build Linux cloud masih perlu verifikasi pada deployment. Aplikasi bukan situs resmi SNPMB dan tidak menghitung peluang lolos pribadi.

## Akses publik dan tampilan (2026-11-16)

Bagikan https://snpmb-insight.streamlit.app/ kepada dosen. Opsi `Make this app public` sudah aktif saat pemeriksaan; permintaan sesi baru tanpa kredensial kembali ke alamat aplikasi dengan HTTP 200.

Sidebar navy memakai aksen biru dan teal; kartu ringkasan memakai biru, teal, dan amber. Tombol diperlebar agar label tidak terpotong. Keenam menu lolos AppTest dan susunan Beranda sudah diperiksa visual. Pemindahan deployment ke repo kelompok dilakukan setelah koordinasi dengan Mikail.
