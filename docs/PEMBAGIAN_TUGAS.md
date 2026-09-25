# Pembagian Tugas dan Status Pengerjaan

Dokumen ini adalah **sumber kebenaran bersama** untuk pembagian tugas, ketergantungan antarpekerjaan, keluaran yang wajib diserahkan, dan status pengerjaan kelompok.

Setiap anggota wajib membaca dokumen ini bersama [STANDAR_PENGERJAAN.md](STANDAR_PENGERJAAN.md) sebelum mulai bekerja. Perubahan tugas, status, tenggat, atau lokasi berkas harus langsung diperbarui di sini dan dicatat di [CHANGELOG.md](CHANGELOG.md).

Tutorial langkah demi langkah tersedia di [PANDUAN_ANGGOTA.md](PANDUAN_ANGGOTA.md) dan wajib diikuti sesuai penanggung jawab.

## Identitas proyek

- **Konteks:** Tugas Besar mata kuliah Machine Learning.
- **Judul:** *Estimasi Jumlah Peminat Program Studi Menggunakan Regresi pada Data SNPMB sebagai Dasar Pembentukan Angka Pembanding Antar Perguruan Tinggi*.
- **Anggota:** Mikail, Shiddiq, Duha, dan Ihsan.
- **Cakupan:** seluruh PTN peserta SNPMB; Universitas Andalas hanya contoh ilustrasi, bukan studi kasus.
- **Folder bersama:** belum dicantumkan—isi setelah tautan final disepakati.

## Arti status

| Status | Arti |
|---|---|
| **Selesai** | Artefak tersedia di repositori, dapat dibuka, dan sudah melewati pemeriksaan yang relevan |
| **Berjalan** | Sedang dikerjakan; artefak boleh belum final |
| **Menunggu** | Belum dapat dimulai karena bergantung pada pekerjaan lain |
| **Belum tersedia di repo** | Tidak ada artefak yang dapat diverifikasi di repositori; status di luar repo harus dikonfirmasi kepada penanggung jawab |

Status tidak boleh diubah menjadi **Selesai** hanya berdasarkan kabar lisan. Cantumkan berkas atau hasil yang dapat diperiksa.

## Tahap 1 — Fondasi, laporan awal, presentasi, dan eksplorasi

**Tenggat:** belum ditentukan.

| Penanggung jawab | Tugas | Keluaran wajib | Status dan bukti |
|---|---|---|---|
| Mikail | Pemetaan kelompok bidang, pemilihan fitur, pembagian data latih/uji, fungsi evaluasi, dan template notebook | `src/fitur_kelompok_bidang.py`, `src/fondasi.py`, `notebooks/template_model.ipynb`, serta dokumentasi metodologi | **Selesai.** Fondasi lolos pemeriksaan sintaks, kebocoran fitur, NaN, pembagian temporal, dan lipatan waktu |
| Ihsan | BAB I: latar belakang, rumusan masalah, batasan, tujuan, manfaat; BAB II: tinjauan pustaka; memeriksa tautan jurnal, nama penulis, dan judul | Dokumen BAB I–II dan daftar pustaka terverifikasi | **Belum tersedia di repo** |
| Shiddiq | Revisi PPT mengikuti judul yang disetujui; hapus “Universitas Andalas” dari rumusan masalah/tujuan 4–5; ubah manfaat menjadi “Manfaat bagi Perguruan Tinggi”; koreksi 216% menjadi 21,6% dan 473% menjadi 47,3%; hapus referensi ganda; ganti “Zub dkk.” menjadi “Raftopoulos dkk. (2024)” | PPT revisi | **Belum tersedia di repo** |
| Duha | Menu Eksplorasi Data di Streamlit: grafik tren peminat per prodi dengan filter PTN, jalur, dan tahun menggunakan CSV yang tersedia | Aplikasi atau modul Streamlit yang dapat dijalankan | **Belum tersedia di repo** |

## Tahap 2 — Pelatihan model

Tahap ini dimulai setelah fondasi dan template Mikail selesai. Semua model wajib memuat data melalui `src/fondasi.py`; bagian data dan evaluasi pada template tidak boleh diubah.

**Tenggat:** belum ditentukan.

| Penanggung jawab | Model/tugas | Keluaran wajib | Status dan bukti |
|---|---|---|---|
| Mikail | Baseline rata-rata per kelompok bidang; baseline lag-1 sebagai pembanding tambahan | `notebooks/00_baseline.ipynb` dan hasil baseline di `hasil/evaluasi.csv` | **Selesai.** Terdapat 9 baris hasil baseline tanpa hasil model anggota lain |
| Ihsan | Linear Regression | `notebooks/01_linear_regression.ipynb` dan baris evaluasi model | **Belum tersedia di repo** |
| Shiddiq | Random Forest, feature importance, dan rentang prediksi untuk prodi baru | `notebooks/02_random_forest.ipynb`, hasil evaluasi, feature importance, dan metode rentang prediksi yang terdokumentasi | **Belum tersedia di repo** |
| Duha | XGBoost | `notebooks/03_xgboost.ipynb` dan baris evaluasi model | **Belum tersedia di repo** |

Setiap model wajib menjalankan:

1. Skenario `dengan_lag` dan `tanpa_lag`.
2. Target skala asli dan target `log1p` sesuai K-15.
3. Evaluasi MAE, MAPE, R², serta RMSLE sebagai metrik pelengkap.
4. Penyetelan hyperparameter hanya dengan `lipatan_waktu()` bila penyetelan dilakukan.
5. Penyimpanan hasil melalui `evaluasi()` ke `hasil/evaluasi.csv`.

## Tahap 3 — Integrasi dan pelaporan akhir

Tahap ini dimulai setelah hasil ketiga model tersedia dan dapat dibandingkan.

**Tenggat:** belum ditentukan.

| Penanggung jawab | Tugas | Keluaran wajib | Status dan ketergantungan |
|---|---|---|---|
| Mikail | Menggabungkan hasil, membuat tabel perbandingan, memilih model terbaik, dan menghubungkannya ke Streamlit untuk menu estimasi prodi baru, pemetaan prodi, dan perbandingan model | Tabel perbandingan final, dasar pemilihan model, dan integrasi Streamlit | **Menunggu** hasil Linear Regression, Random Forest, XGBoost, serta aplikasi Streamlit |
| Ihsan | BAB V: kesimpulan dan saran | Dokumen BAB V yang konsisten dengan hasil final | **Menunggu** hasil dan pembahasan final |
| Shiddiq | BAB IV: hasil dan pembahasan | Dokumen BAB IV beserta tabel/grafik hasil | **Menunggu** seluruh hasil model |
| Duha | BAB III: metodologi pengumpulan data, fitur, algoritma, dan evaluasi | Dokumen BAB III yang mengikuti keputusan K-01–K-18 | **Menunggu** rincian implementasi final |

## Aturan serah terima

Sebuah tugas baru dapat dinyatakan selesai bila:

- berkas keluaran disimpan pada folder yang disepakati dan memakai jalur relatif;
- berkas dapat dibuka atau dijalankan tanpa error yang belum dijelaskan;
- angka, metode, dan istilah konsisten dengan dokumentasi proyek;
- perubahan penting dicatat di `docs/CHANGELOG.md`;
- status dan bukti pada dokumen ini diperbarui;
- penanggung jawab berikutnya diberi tahu mengenai nama berkas, cara menjalankan, asumsi, dan keterbatasannya.

Jika pekerjaan dilakukan di luar repositori, misalnya PPT atau dokumen laporan di folder bersama, tautan atau salinan finalnya tetap harus dicantumkan di bagian tugas terkait.

## Peta dokumentasi

| Informasi | Sumber kebenaran |
|---|---|
| Orientasi proyek, anggota, dan cara mulai | `README.md` |
| Pembagian tugas, status, tenggat, dependensi, dan serah terima | `docs/PEMBAGIAN_TUGAS.md` |
| Aturan teknis kerja bersama | `docs/STANDAR_PENGERJAAN.md` |
| Keputusan metodologi dan alasannya | `docs/KEPUTUSAN_METODOLOGI.md` |
| Arti kolom dan status fitur | `docs/KAMUS_DATA.md` |
| Riwayat perubahan | `docs/CHANGELOG.md` |

Jika dua dokumen bertentangan, hentikan pekerjaan yang terdampak, selaraskan dokumennya melalui diskusi tim, lalu catat keputusan di changelog sebelum melanjutkan.
