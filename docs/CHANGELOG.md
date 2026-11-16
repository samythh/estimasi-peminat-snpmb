# Riwayat Perubahan

Semua perubahan penting pada data, fitur, dan kode dicatat di sini, terbaru di atas. Setiap entri menyebut **apa** yang berubah dan **dampaknya** bagi anggota tim.

Format: `[versi] — tanggal`, lalu kelompok *Ditambahkan*, *Diubah*, *Diperbaiki*, *Dihapus*.

---

## [0.8.6] — 2026-11-16

Random Forest dijalankan ulang pada fondasi versi 2 (tiga skenario × target asli/log), disetel ulang, dilengkapi feature importance dan rentang prediksi prodi baru (branch `random-forest-02-shiddiq`). Hasil versi 1 (entri 2026-10-29 di bawah) tidak setara dan tidak lagi ada di `hasil/evaluasi.csv`.

### Ditambahkan
- `notebooks/02_random_forest.ipynb` dibangun ulang dari template versi 2: `buat_model(target)` untuk Random Forest; sel *JANGAN DIUBAH* tidak disentuh (identik dengan template). Sel penyetelan, feature importance, dan rentang prediksi berada di luar sel terkunci.
- `hasil/tuning_random_forest.csv`: skor validasi 24 kandidat × 6 kombinasi dengan `lipatan_waktu()` (lipatan kelompok pada skenario prodi baru, K-24), 100 pohon saat pencarian. Satu konfigurasi bersama dipilih lewat rata-rata peringkat MAE (aturan ditetapkan sebelum melihat hasil): `max_depth=None`, `min_samples_leaf=2`, `max_features=0.33`, model akhir `n_estimators=300`. Peringkat rata-rata 3,5 vs bawaan 15,7; MAE validasi rata-rata 140,4 vs 144,2. Hasil sementara disimpan per kandidat agar penyetelan dapat dilanjutkan.
- `hasil/grafik/importance_random_forest_2021_2024.csv` dan `.png`: impurity dan permutasi grup pada lipatan validasi waktu untuk tiga skenario × dua target. Grafik utama memakai target log, dipilih dari skor validasi penyetelan.
- `hasil/rentang_prediksi_random_forest_cakupan_2024.csv` dan `..._contoh_2024.csv`: rentang empiris antarpohon (persentil ke-10 dan ke-90, dikembalikan ke skala orang sebelum persentil), cakupan pada validasi 2024, dan contoh baris validasi ([K-25](KEPUTUSAN_METODOLOGI.md#k-25)).
- Enam baris `random_forest` di `hasil/evaluasi.csv` (`versi_fondasi = 2`, jalur gabungan, uji 2025, tanpa prediksi negatif):

  | skenario | target | MAE | MAPE | R² | RMSLE |
  |---|---|---|---|---|---|
  | dengan_lag | asli | 68,06 | 27,26 | 0,9294 | 0,3385 |
  | dengan_lag | log | 72,74 | 24,25 | 0,9050 | 0,3505 |
  | tanpa_riwayat_sendiri | asli | 146,61 | 135,75 | 0,6778 | 0,7663 |
  | tanpa_riwayat_sendiri | log | 143,41 | 59,26 | 0,6293 | 0,6208 |
  | tanpa_lag | asli | 185,16 | 149,75 | 0,6067 | 0,8482 |
  | tanpa_lag | log | 178,92 | 79,50 | 0,5550 | 0,7469 |

### Diubah
- `hasil/evaluasi.csv`: konflik penggabungan dengan `main` diselesaikan dengan versi `main`; empat baris Random Forest versi 1 dihapus dari berkas (tetap ada di commit `14d44cc`).
- Entri Random Forest 2026-10-29 diberi label "fondasi versi 1".

### Catatan untuk tim
- `dengan_lag`: Random Forest belum mengalahkan `baseline_lag1` (MAE 66,11; MAPE 23,65; R² 0,9480). Selisih MAE 2,95 (sekitar 3%), tetapi RMSLE Random Forest lebih rendah (0,3385 vs 0,3633). Pada versi 2 target asli lebih baik daripada log, kebalikan versi 1. Satu tahun uji, tanpa uji signifikansi.
- Skenario prodi baru: Random Forest jauh di bawah baseline pembandingnya (`tanpa_riwayat_sendiri` 143,41 vs 254,52; `tanpa_lag` 178,92 vs 299,57). Skor `tanpa_lag` lebih tinggi dari versi 1 (151,29) karena penilaian kini menyembunyikan prodi uji (K-24), bukan karena model memburuk.
- Rentang prediksi terlalu sempit: cakupan validasi 2024 hanya 72,6% (`tanpa_riwayat_sendiri`) dan 57,0% (`tanpa_lag`) dari 80% nominal. Tidak dikalibrasi ulang; harus disebut "rentang empiris antarpohon" dan tidak boleh disebut interval kepercayaan.
- Feature importance (target log, permutasi): `dengan_lag` didominasi `peminat_lag1` (kenaikan MAE ±196 orang), lalu fitur prodi sejenis (±59 dan ±43); `tanpa_riwayat_sendiri` didominasi `rata_peminat_prodi_sejenis_lag1` (±135); `tanpa_lag` paling bergantung pada `daya_tampung` (±71) dan `kelompok_bidang` (±55). Importance bukan bukti sebab-akibat; keterbatasannya tertulis di notebook.
- Cara menjalankan: bangun panel dengan `python src/ambil_data_snpmb.py`, lalu *Restart & Run All* dari dalam folder repo (±35 menit di mesin dua core). Penyetelan, importance, dan rentang memakai berkas CSV tersimpan bila ada; atur `ULANG_TUNING` / `ULANG_IMPORTANCE` ke `True` untuk menghitung ulang. CSV versi lain ditolak lewat pemeriksaan `versi_fondasi`.
- Belum ada: contoh prodi baru dengan masukan kustom, menunggu fungsi masukan prodi baru dari Mikail agar melewati transformasi yang sama dengan data latih.

---

## [0.8.5] — 2026-11-16

Linear Regression dijalankan ulang pada fondasi versi 2 (Ihsan).

### Diubah
- `notebooks/01_linear_regression.ipynb` disalin ulang dari template terbaru, sehingga ketiga sel *JANGAN DIUBAH* identik dengan template. Hanya sel *ISI BAGIAN INI* yang diubah: `NAMA_MODEL = "linear_regression"` dan ketiga baris contoh Linear Regression (`log_fitur()` + `StandardScaler` + `LinearRegression` untuk target log; `StandardScaler` + `LinearRegression` untuk target asli). Tanpa penyetelan.
- Enam baris `linear_regression` dengan `versi_fondasi = 2` di `hasil/evaluasi.csv` (gabungan). Baris versi 1 hilang karena konflik `evaluasi.csv` diselesaikan dengan versi `main`; angka versi 1 tetap tercatat di [0.7.1].

  | skenario | target | MAE | MAPE | R² | RMSLE | prediksi negatif | baseline terkuat (MAE) |
  |---|---|---|---|---|---|---|---|
  | dengan_lag | asli | 84,02 | 125,80 | 0,9347 | – | 1.065 | `baseline_lag1` 66,11 |
  | dengan_lag | log | 90,01 | 26,99 | 0,7546 | 0,3774 | 0 | `baseline_lag1` 66,11 |
  | tanpa_lag | asli | 245,46 | 434,89 | 0,4377 | – | 1.160 | `baseline_rata_kelompok` 299,57 |
  | tanpa_lag | log | 204,78 | 94,66 | 0,4239 | 0,8073 | 0 | `baseline_rata_kelompok` 299,57 |
  | tanpa_riwayat_sendiri | asli | 209,32 | 436,58 | 0,5561 | – | 1.563 | `baseline_rata_sejenis` 254,52 |
  | tanpa_riwayat_sendiri | log | 163,33 | 64,19 | 0,5995 | 0,6726 | 0 | `baseline_rata_sejenis` 254,52 |

### Catatan untuk tim
- `dengan_lag`: Linear Regression belum mengalahkan `baseline_lag1` (MAE terbaik 84,02 vs 66,11).
- `tanpa_lag` dan `tanpa_riwayat_sendiri`: kedua target mengalahkan baseline terkuat di skenarionya. Terbaik adalah target log pada `tanpa_riwayat_sendiri`, MAE 163,33, atau 35,8% di bawah `baseline_rata_sejenis`.
- Target log tidak lagi meledak berkat `log_fitur()` (K-23): R² `dengan_lag` 0,7546, sama dengan uji template pada [0.8.0] (versi 1: −527,06).
- Target asli tetap menghasilkan prediksi negatif (1.065 / 1.160 / 1.563). Prediksi itu dilaporkan apa adanya tanpa dipotong, sehingga RMSLE kosong.
- Cara menjalankan: `python src/ambil_data_snpmb.py` bila `data/olahan/` belum ada, lalu *Restart & Run All*. Notebook ini dijalankan dengan `jupyter nbconvert --execute` pada Python 3.12.10, dengan 0 error.

---

## [0.8.4] — 2026-11-16

- Memperbaiki identitas sidebar menjadi simbol buku terbuka, wordmark SNPMB Insight, dan kepanjangan Seleksi Nasional Penerimaan Mahasiswa Baru.
- Mengganti tiga kartu berwarna menjadi satu baris statistik tanpa kotak, dengan pemisah tipis. Sidebar tetap hijau pinus.
- Tampilan Beranda diperiksa di browser lokal; perubahan hanya pada presentasi, tanpa perubahan data atau model.

---

## [0.8.3] — 2026-11-16

- Mengganti sidebar menjadi hijau pinus dengan aksen sage, menghapus ikon kotak S, dan memperbesar huruf S pada wordmark SNPMB.
- Menyederhanakan Beranda menjadi filter jalur/tahun, ringkasan angka, tren, dan lima prodi dengan peminat terbanyak.
- Mengganti radio SNBP/SNBT dengan tombol pilihan menyatu. Perbandingan memakai dua pasangan kampus–jurusan dan opsi jurusan ketiga; pilihan ganda yang sama ditolak dengan pesan.
- Pemeriksaan: enam menu, tiga pasang pilihan, dan pilihan kosong lolos AppTest; Beranda serta perbandingan diperiksa di browser lokal. Model dan data evaluasi tidak diubah.

---

## [0.8.2] — 2026-11-16

- Memeriksa Sharing: `Make this app public` sudah aktif. Permintaan dengan sesi cookie baru tanpa login berhasil HTTP 200 pada https://snpmb-insight.streamlit.app/ .
- Merapikan sidebar navy, aksen biru/teal/amber, tombol utama, label kartu angka, panel grafik dan panduan. Warna grafik evaluasi membedakan model dan baseline.
- Keenam menu lolos AppTest; Beranda diperiksa secara visual. Data dan hasil evaluasi model tetap menggunakan fondasi versi 2.
- Deployment masih memakai fork Duha; pemindahan ke repo kelompok menunggu koordinasi Mikail.

---

## [0.8.1] — 2026-11-14

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

---

## [0.7.2] — 2026-10-29

Hasil model Random Forest, penyetelan hyperparameter, dan feature importance pada **fondasi versi 1** (branch `random-forest-02-shiddiq`; rentang prediksi prodi baru belum dikerjakan). Hasil ini **tidak setara** dengan fondasi versi 2 (K-22) dan dijalankan ulang di versi 2; empat baris `random_forest` versi 1 tidak lagi ada di `hasil/evaluasi.csv` dan dapat dilihat di commit `14d44cc`.

### Ditambahkan
- `notebooks/02_random_forest.ipynb`, salinan template dengan `NAMA_MODEL = "random_forest"`; sel *JANGAN DIUBAH* tidak disentuh. Sel *ISI BAGIAN INI* diubah, dan ditambah sel penyetelan serta feature importance di luar sel terkunci.
- `hasil/tuning_random_forest.csv`: skor validasi seluruh kandidat. Penyetelan memakai `lipatan_waktu()` saja (data uji 2025 tidak disentuh), 24 kandidat (bawaan + acak, `random_state=42`), 100 pohon saat pencarian. Satu konfigurasi bersama dipilih lewat rata-rata peringkat MAE di keempat kombinasi: `max_depth=30`, `min_samples_leaf=1`, `max_features=0.5`, model akhir `n_estimators=300`.
- `hasil/grafik/importance_random_forest_2021_2024.csv` dan `.png`: impurity dan permutasi grup (pada lipatan validasi waktu), kolom one-hot digabung ke fitur asal. Grafik utama memakai target log, dipilih dari skor validasi.
- Empat baris `random_forest` di `hasil/evaluasi.csv` (jalur gabungan):

  | skenario | target | MAE | MAPE | R² | RMSLE | prediksi negatif |
  |---|---|---|---|---|---|---|
  | dengan_lag | asli | 104,13 | 38,07 | 0,7716 | 0,4213 | 0 |
  | dengan_lag | log | 82,03 | 29,06 | 0,8902 | 0,3894 | 0 |
  | tanpa_lag | asli | 149,08 | 104,04 | 0,7247 | 0,7207 | 0 |
  | tanpa_lag | log | 151,29 | 59,07 | 0,6553 | 0,6573 | 0 |

### Catatan untuk tim
- Random Forest belum mengalahkan `baseline_lag1` (MAE 67,54; R² 0,9465) pada `dengan_lag`; pada `tanpa_lag` kedua target lebih baik daripada `baseline_rata_kelompok` (MAE 299,17).
- Pengaturan bawaan (sebelum penyetelan) menghasilkan MAE 115,28 / 93,69 (`dengan_lag`, asli / log) dan 155,91 / 154,03 (`tanpa_lag`, asli / log). Perbaikan di validasi 2023–2024 hanya sekitar 2% (MAE rata-rata 128,16 menjadi 125,77) dengan 2–3 lipatan, sehingga skornya berisik.
- Pada `dengan_lag`, model hampir seluruhnya bersandar pada `peminat_lag1` (permutasi: MAE naik ±299 orang; fitur lain paling besar ±5). Feature importance bukan bukti sebab-akibat; keterbatasannya tertulis di notebook.
- Cara menjalankan: bangun panel dengan `python src/ambil_data_snpmb.py` (folder `data/olahan/` tidak di-commit), lalu *Restart & Run All* dari dalam folder repo. Penyetelan dan importance memakai berkas CSV tersimpan; atur `ULANG_TUNING` / `ULANG_IMPORTANCE` ke `True` untuk menghitung ulang (±20 dan ±10 menit).
- Untuk Mikail: sel pertama template mencari folder `src/` dengan loop tanpa kondisi berhenti, sehingga berputar tanpa akhir bila notebook dijalankan dari luar folder repo. Tidak diubah; dilaporkan saja.
- Belum ada: rentang prediksi prodi baru (persentil antarpohon) dan cakupannya pada 2024. Contoh prodi baru menunggu fungsi masukan prodi baru dari Mikail agar melewati transformasi yang sama dengan data latih.

---

## [Dashboard awal] — 2026-10-27

- Menambahkan dashboard berbahasa sederhana dengan sidebar tombol berikon.
- Menambahkan pencarian dan perbandingan jurusan, hasil evaluasi, serta panduan istilah.
- Menyiapkan entry point `dashboard/streamlit_app.py`, dependensi khusus cloud, dan tema.
- Startup memakai skrip resmi untuk membangun panel dari snapshot repo.
- Enam menu lolos AppTest. Perkiraan baru belum diintegrasikan; deployment menunggu verifikasi layanan.
- Petunjuk dan bukti tampilan tersedia di `docs/DASHBOARD_STREAMLIT.md`.

---

## [0.7.1] — 2026-10-17

Hasil model Linear Regression (Ihsan).

### Ditambahkan
- `notebooks/01_linear_regression.ipynb`, salinan template dengan `NAMA_MODEL = "linear_regression"` dan `make_pipeline(StandardScaler(), LinearRegression())`; sel *JANGAN DIUBAH* tidak disentuh.
- Empat baris `linear_regression` di `hasil/evaluasi.csv` (jalur gabungan):

  | skenario | target | MAE | MAPE | R² | RMSLE | prediksi negatif |
  |---|---|---|---|---|---|---|
  | dengan_lag | asli | 100,60 | 192,72 | 0,9032 | – | 769 |
  | dengan_lag | log | 630,51 | 91,28 | −527,06 | 0,7422 | 0 |
  | tanpa_lag | asli | 244,04 | 384,42 | 0,3792 | – | 1.163 |
  | tanpa_lag | log | 235,73 | 97,15 | −0,9178 | 0,9062 | 0 |

### Catatan untuk tim
- Linear Regression belum mengalahkan `baseline_lag1` (MAE 67,54) pada skenario `dengan_lag`; pada `tanpa_lag` kedua target (MAE 244,04 dan 235,73) lebih baik daripada `baseline_rata_kelompok` (MAE 299,17).
- Prediksi negatif dilaporkan apa adanya, tidak dipotong; RMSLE kosong untuk target asli karena itu.
- Target log `dengan_lag` tidak stabil: `log1p(peminat)` dimodelkan linear terhadap `peminat_lag1` yang berskala asli, sehingga prodi dengan lag besar (lag-1 uji hingga 6.371, maksimum latih 4.570) mendapat prediksi eksponensial setelah `dari_log()` (maks 994.387; 54 prediksi > 3× maksimum target latih). Perbaikan, misalnya log pada fitur lag, mengubah fitur/algoritma sehingga **menunggu keputusan tim** dan belum diterapkan.
- Cara menjalankan: bangun panel dengan `python src/ambil_data_snpmb.py` (folder `data/olahan/` tidak di-commit), lalu *Restart & Run All* pada notebook.

---

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
