# Riwayat Perubahan

Semua perubahan penting pada data, fitur, dan kode dicatat di sini, terbaru di atas. Setiap entri menyebut **apa** yang berubah dan **dampaknya** bagi anggota tim.

Format: `[versi] — tanggal`, lalu kelompok *Ditambahkan*, *Diubah*, *Diperbaiki*, *Dihapus*.

---

## [Duha — sidebar hijau dan perbandingan jurusan] — 2026-11-16

- Mengganti sidebar menjadi hijau pinus dengan aksen sage, menghapus ikon kotak S, dan memperbesar huruf S pada wordmark SNPMB.
- Menyederhanakan Beranda menjadi filter jalur/tahun, ringkasan angka, tren, dan lima prodi dengan peminat terbanyak.
- Mengganti radio SNBP/SNBT dengan tombol pilihan menyatu. Perbandingan memakai dua pasangan kampus–jurusan dan opsi jurusan ketiga; pilihan ganda yang sama ditolak dengan pesan.
- Pemeriksaan: enam menu, tiga pasang pilihan, dan pilihan kosong lolos AppTest; Beranda serta perbandingan diperiksa di browser lokal. Model dan data evaluasi tidak diubah.

---

## [Duha — perapian dashboard dan akses publik] — 2026-11-16

- Memeriksa Sharing: `Make this app public` sudah aktif. Permintaan dengan sesi cookie baru tanpa login berhasil HTTP 200 pada https://snpmb-insight.streamlit.app/ .
- Merapikan sidebar navy, aksen biru/teal/amber, tombol utama, label kartu angka, panel grafik dan panduan. Warna grafik evaluasi membedakan model dan baseline.
- Keenam menu lolos AppTest; Beranda diperiksa secara visual. Data dan hasil evaluasi model tetap menggunakan fondasi versi 2.
- Deployment masih memakai fork Duha; pemindahan ke repo kelompok menunggu koordinasi Mikail.

---

## [Duha — XGBoost dan dashboard fondasi 2] — 2026-11-14

- Menyiapkan fork `duhaalul/estimasi-peminat-snpmb` beserta branch `duha-fondasi-v2` untuk deployment mandiri; Cloud berhasil terbit dan diverifikasi di https://snpmb-insight.streamlit.app/ pada Python 3.13.
- Menggabungkan fondasi versi 2 dari `main` ke branch Duha. Konflik `hasil/evaluasi.csv` diselesaikan dengan versi `main`; catatan changelog kedua branch digabung.
- Mengganti nama notebook menjadi `notebooks/03_xgboost.ipynb`, menyalin ulang tiga sel `JANGAN DIUBAH` dari template versi 2, dan mengubah antarmuka menjadi `buat_model(target)`.
- Menjalankan ulang XGBoost pada tiga skenario × dua target lewat `latih_dan_prediksi()` dan menyimpan enam baris `versi_fondasi = 2` melalui `evaluasi()`.
- Menyesuaikan skrip validasi dan halaman Hasil Pengujian Streamlit untuk tiga skenario. Dashboard hanya menampilkan hasil dari versi fondasi terbaru.
- Memperbarui `docs/HASIL_XGBOOST.md`, `docs/DASHBOARD_STREAMLIT.md`, dan status tugas. Deployment Streamlit Cloud masih memerlukan izin admin repo atau fork yang dimiliki akun Duha.

---

## [0.8.0] — 2026-11-12

Fondasi versi 2: fitur prodi sejenis, skenario ketiga, dan penanda vokasi SNBT. **Semua model wajib dijalankan ulang**; hasil versi 1 tidak setara dengan versi 2.

### Ditambahkan
- `src/fitur_prodi_sejenis.py`: normalisasi nama prodi menjadi `prodi_normal` (1.420 nama mentah → 755 nama baku, 148 entri sinonim) dan `tambah_fitur_sejenis()` untuk tiga fitur t−1 dari prodi sejenis (`prodi_normal` + `jenjang`, per jalur, PTN lain saja): `rata_peminat_prodi_sejenis_lag1`, `jumlah_ptn_punya_prodi_sejenis_lag1`, `rasio_peminat_vs_sejenis_lag1` ([K-20](KEPUTUSAN_METODOLOGI.md#k-20)). Uji `--uji`: 2.000/2.000 baris cocok dengan hitungan manual.
- Skenario `tanpa_riwayat_sendiri` untuk prodi baru yang punya padanan di PTN lain: latih 22.453, uji 8.834 baris (gabungan).
- Penanda `is_rezim_vokasi_snbt` (tahun ≥ 2024, skenario `tanpa_lag`) dan `is_lintas_rezim_vokasi_snbt` (tahun = 2024, skenario berbasis t−1) untuk lonjakan peminat vokasi SNBT; penyebab lonjakan belum diketahui ([K-19](KEPUTUSAN_METODOLOGI.md#k-19)).
- Baseline `baseline_rata_sejenis` dan pengukuran pengaruh penanda di `hasil/analisis_penanda_rezim.csv`.
- Kolom `versi_fondasi` di `hasil/evaluasi.csv` ([K-22](KEPUTUSAN_METODOLOGI.md#k-22)).
- `kelompok_prodi()`, `lipatan_uji()`, dan `latih_dan_prediksi()`: `tanpa_lag` dan `tanpa_riwayat_sendiri` dinilai dengan 5 lipatan kelompok prodi (PTN + nama baku + jenjang), sehingga prodi uji tidak pernah ikut dilatih. `lipatan_waktu()` ikut berkelompok untuk kedua skenario itu ([K-24](KEPUTUSAN_METODOLOGI.md#k-24)). Tanpa ini, skor kedua skenario 20–29% terlalu optimistis.
- K-21: keterbatasan `dengan_lag` yang bias ke prodi umum.
- `log_fitur()` di `fondasi.py`: `log1p` pada lima fitur yang sangat menceng, dipasang di pipeline model linear bertarget log ([K-23](KEPUTUSAN_METODOLOGI.md#k-23)). Pada Linear Regression `dengan_lag` target log, R² naik dari −1.640,99 menjadi 0,7546. `X` dari `muat_data()` tidak berubah; model pohon tidak memerlukannya.

### Diubah
- Skenario `dengan_lag` memakai ketiga fitur prodi sejenis dan kehilangan 8,7% baris yang tidak punya pembanding: latih 23.445 → 21.507, uji 9.416 → 8.508 (gabungan). Baris yang keluar didominasi prodi vokasi ([K-21](KEPUTUSAN_METODOLOGI.md#k-21)).
- `notebooks/00_baseline.ipynb` dijalankan ulang: 15 baris baseline untuk tiga skenario × tiga jalur. Baseline lag-1 gabungan kini MAE 66,11 (sebelumnya 67,54 pada baris uji versi 1).
- Template menilai 6 konfigurasi (3 skenario × 2 target) lewat `latih_dan_prediksi()`, menampilkan `baseline_rata_sejenis`, dan memanggil `buat_model(target)` sehingga praproses dapat berbeda per target. **Notebook salinan template lama harus menyalin ulang ketiga sel `JANGAN DIUBAH`.**
- Tafsiran K-11: Administrasi Perkantoran D3 Unand adalah contoh ekstrem lonjakan vokasi SNBT, bukan artefak satu prodi.
- Panduan anggota, standar pengerjaan, pembagian tugas, kamus data, dan CLAUDE.md diselaraskan dengan tiga skenario.

### Diperbaiki
- `is_psdku` kini menangkap `PDSKU`, `KAMP`, dan `FIKKIA BANYUWANGI`: 182 → 188 prodi (170 → 176 bertarget) ([K-16](KEPUTUSAN_METODOLOGI.md#k-16)).
- `GEOLOGI` tidak lagi digabung ke `TEKNIK GEOLOGI`; `TEKNOLOGI DAN MANAJEMEN PEMBENIHAN IKAN` digabung ke `TEKNOLOGI PEMBENIHAN IKAN`.

## [Dashboard awal] — 2026-10-27

- Menambahkan dashboard berbahasa sederhana dengan sidebar tombol berikon.
- Menambahkan pencarian dan perbandingan jurusan, hasil evaluasi, serta panduan istilah.
- Menyiapkan entry point `dashboard/streamlit_app.py`, dependensi khusus cloud, dan tema.
- Startup memakai skrip resmi untuk membangun panel dari snapshot repo.
- Enam menu lolos AppTest. Perkiraan baru belum diintegrasikan; deployment menunggu verifikasi layanan.
- Petunjuk dan bukti tampilan tersedia di `docs/DASHBOARD_STREAMLIT.md`.


## [Duha — penomoran XGBoost] — 2026-10-15

- Menggunakan `notebooks/04_xgboost.ipynb` sesuai permintaan Duha sebagai anggota keempat.
- Menyesuaikan rujukan nama notebook pada skrip, dokumentasi hasil, panduan Duha, standar penamaan, dan pembagian tugas.
- Memperbarui contoh nama pada markdown notebook salinan; kode fondasi, template bersama, dan sel kode terkunci tetap utuh.
- Validasi dijalankan ulang tanpa melatih ulang atau mengubah hasil evaluasi.

---

## [Duha — XGBoost] — 2026-10-11

- Menambahkan notebook XGBoost dengan empat eksperimen sesuai panduan, tanpa tuning pada data uji.
- Menambahkan empat baris evaluasi melalui fondasi; hasil baseline dipertahankan.
- Menambahkan cara menjalankan, dependensi XGBoost, pemeriksaan, dan catatan serah terima.
- Memperbarui status XGBoost Duha; pekerjaan anggota lain dan tahap lain tidak diubah.
- Model belum mengalahkan baseline lag-1. RMSLE target asli tidak tersedia karena prediksi negatif, sesuai fondasi.
- Tidak mengubah data mentah, fondasi, atau template bersama.

---

## [0.7.0] — 2026-09-25

Panduan kerja terpisah untuk setiap anggota kelompok.

### Ditambahkan
- `docs/PANDUAN_ANGGOTA.md` sebagai indeks, urutan baca wajib, aturan penggunaan, dan format laporan progres.
- `docs/panduan/mikail.md`: fondasi, baseline, perbandingan model, dan integrasi.
- `docs/panduan/ihsan.md`: BAB I–II, verifikasi pustaka, Linear Regression, dan BAB V.
- `docs/panduan/shiddiq.md`: revisi PPT, Random Forest, feature importance, rentang prediksi, dan BAB IV.
- `docs/panduan/duha.md`: eksplorasi Streamlit, XGBoost, dan BAB III.

### Diubah
- README, panduan Claude, standar pengerjaan, dan pembagian tugas kini menautkan indeks tutorial anggota.

---
## [0.6.1] — 2026-09-25

Penyelarasan pembagian tugas dan tata kelola dokumentasi kelompok.

### Ditambahkan
- `docs/PEMBAGIAN_TUGAS.md` sebagai sumber kebenaran untuk penanggung jawab, status, keluaran wajib, dependensi, tenggat, bukti, dan aturan serah terima.
- Peta sumber dokumentasi dan catatan minimum yang harus menyertai setiap penyerahan pekerjaan.

### Diubah
- `README.md` kini menautkan pembagian tugas dan menjelaskan kewajiban memperbarui dokumentasi.
- `CLAUDE.md` kini mewajibkan pemeriksaan pembagian tugas, membatasi pengerjaan pada bagian yang diminta, dan merutekan setiap jenis perubahan ke dokumen yang sesuai.
- `STANDAR_PENGERJAAN.md` kini mensyaratkan artefak yang dapat diverifikasi, pelacakan berkas di luar repositori, serta pembaruan status dan bukti pekerjaan.

---
## [0.6.0] — 2026-09-25

Fondasi pemodelan bersama dan baseline.

### Ditambahkan
- `src/fondasi.py`: pemuatan fitur bersama, pembagian temporal 2021–2024/2025, validasi kebocoran, `lipatan_waktu()`, transformasi target log, dan evaluasi MAE/MAPE/R²/RMSLE.
- `notebooks/00_baseline.ipynb` dan `notebooks/template_model.ipynb`.
- `hasil/evaluasi.csv` berisi hasil baseline rata-rata kelompok bidang dan baseline lag-1.
- Informasi bahwa proyek merupakan Tugas Besar mata kuliah Machine Learning dengan anggota Mikail, Shiddiq, Duha, dan Ihsan.

### Diubah
- T-01–T-05 diputuskan menjadi K-13–K-17; K-18 menambahkan validasi silang berbasis waktu.
- Setiap model wajib diuji pada target asli dan log; RMSLE ditambahkan sebagai metrik pelengkap.
- Kamus data dan standar pengerjaan diselaraskan dengan fondasi yang sudah tersedia.

### Diperbaiki
- Mode `--tinjau-psdku` kini memeriksa seluruh katalog non-fakultas, termasuk prodi baru, sehingga melaporkan 182 prodi sesuai K-16 (170 bertarget dan 12 prodi baru).

---

## [0.5.0] — 2026-09-21

Reorganisasi proyek dan finalisasi fitur `kelompok_bidang`.

### Ditambahkan
- Kolom `kelompok_bidang` dan `is_fakultas` di `snpmb_panel.csv` (panel kini 24 kolom, jumlah baris tetap 43.449).
- Pemetaan kelompok bidang diadaptasi dari **ISCED-F 2013** (UNESCO); padanan dan penyesuaiannya dicatat di [KEPUTUSAN_METODOLOGI.md](KEPUTUSAN_METODOLOGI.md#k-08).
- Kelompok `pariwisata` (63 prodi) dan `olahraga` (25 prodi), pecahan dari kelompok `lainnya` yang dihapus.
- `PETA_KHUSUS` untuk tiga nama ambigu yang diputuskan manual.
- Folder `docs/` beserta `STANDAR_PENGERJAAN.md`, `KAMUS_DATA.md`, `KEPUTUSAN_METODOLOGI.md`, dan berkas ini; `README.md`, `requirements.txt`, `CLAUDE.md`.

### Diubah
- **Struktur folder** (lihat README). Jalur berkas yang berpindah:

  | Lama | Baru |
  |---|---|
  | `ambil_data_snpmb.py`, `fitur_kelompok_bidang.py` | `src/` |
  | `analisa_*.py`, `grafik_*.py` | `analisis/` |
  | `data/snpmb_mentah.json` | `data/mentah/mentah_snbp.json` *(diganti nama)* |
  | `data/mentah_snbt.json` | `data/mentah/mentah_snbt.json` |
  | `data/snpmb_panel.csv`, `data/peminat_provinsi_snbt.csv` | `data/olahan/` |
  | `data/unand_*.csv` | `data/contoh_unand/` |
  | `grafik/` | `hasil/grafik/` |

- `ambil_data_snpmb.py` memanggil pemetaan kelompok bidang secara otomatis, sehingga panel yang dibangun ulang tidak kehilangan kolom tersebut.
- Nama kelompok `sosial-humaniora` → `sosial_humaniora`.
- Pencocokan kata kunci hanya di **awal kata**.

### Diperbaiki
- 31 prodi salah masuk `kesehatan` karena `PERAWAT` cocok di *PERAWATAN* (mesin) dan `PROFESI` cocok di *PROFESIONAL*.
- 16 prodi (11 nama) salah kelompok karena kata kunci cocok di tengah kata: `IKAN` di *PERBAIKAN*/*KELISTRIKAN*, `LAHAN` di *PENGOLAHAN*, `TARI` di *SEKRETARI*. Dua belas masuk pertanian dan empat masuk seni; semuanya kini di kelompok yang benar.
- `belum_terpetakan` turun dari 170 prodi (3,3%) menjadi 0.

### Dihapus
- Aturan singkatan `TI → TEKNIK INDUSTRI` (tidak terpakai; "TI" lebih sering berarti Teknologi Informasi).

---

## [0.4.0] — 2026-09-07

### Ditambahkan
- `analisis/analisa_rumpun_unand.py`: uji klaim pola rumpun pada seluruh 48 prodi Unand berriwayat penuh.
- `analisis/grafik_banding_jalur.py`: grafik SNBP vs SNBT berdampingan dengan skala sumbu Y dikunci sama.

### Diubah
- Grafik tren: subjudul diganti deskriptif ("Lima program studi dengan perubahan paling kontras"), label ujung garis dipisah dengan garis penunjuk, catatan pembanding lintas-PTN ditambahkan.

---

## [0.3.0] — 2026-09-07

Penambahan jalur SNBT.

### Ditambahkan
- Pengambilan data SNBT (`proxy-*-sb.php`), 145 PTN, 0 gagal.
- Kolom `jalur`, `jumlah_prodi_ptn`, `total_peminat_ptn`, `proporsi_peminat_lokal`, `jumlah_provinsi_asal`.
- `data/olahan/peminat_provinsi_snbt.csv` (261.558 baris).
- Alias provinsi: `Jakarta Raya` → `DKI Jakarta`, `Yogyakarta` → `DI Yogyakarta`.
- Pemakaian ulang file mentah; argumen `--paksa-unduh`.

### Diubah
- **Kolom `daya_tampung_snbp` → `daya_tampung_kini`**, berlaku untuk kedua jalur.
- Fitur lag dihitung per `(id_prodi, jalur, tahun)`.
- Panel menjadi 43.449 baris (SNBP 21.668 + SNBT 21.781).

---

## [0.2.0] — 2026-09-07

### Ditambahkan
- Analisis tren peminat Unand dan grafik lima prodi (PNG 300 dpi).

---

## [0.1.0] — 2026-09-07

### Ditambahkan
- `ambil_data_snpmb.py`: pengambilan data SNBP dari API SNPMB, 146 PTN, 0 gagal.
- Panel format panjang, 21.668 baris; fitur lag berbasis nilai tahun.
- Penyimpanan respons mentah sebelum pengolahan.
