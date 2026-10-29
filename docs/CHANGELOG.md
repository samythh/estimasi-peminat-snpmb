# Riwayat Perubahan

Semua perubahan penting pada data, fitur, dan kode dicatat di sini, terbaru di atas. Setiap entri menyebut **apa** yang berubah dan **dampaknya** bagi anggota tim.

Format: `[versi] — tanggal`, lalu kelompok *Ditambahkan*, *Diubah*, *Diperbaiki*, *Dihapus*.

---

## [Shiddiq — Random Forest] — 2026-10-29

Hasil model Random Forest, penyetelan hyperparameter, dan feature importance (branch `random-forest-02-shiddiq`; rentang prediksi prodi baru belum dikerjakan).

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
