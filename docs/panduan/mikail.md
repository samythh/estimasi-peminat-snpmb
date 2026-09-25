# Panduan Mikail

## Tanggung jawab

Mikail menjaga fondasi bersama, baseline, konsistensi hasil, pemilihan model akhir, dan integrasi hasil model ke Streamlit. Mikail tidak mengerjakan implementasi Linear Regression, Random Forest, atau XGBoost milik anggota lain kecuali pembagian tugas diubah secara eksplisit.

## Tahap 1 — Fondasi bersama

Status saat ini: **selesai dan sudah diverifikasi**.

### Artefak yang dijaga

- `src/fitur_kelompok_bidang.py` — pemetaan kelompok bidang berbasis aturan.
- `src/fondasi.py` — pemuatan fitur, split temporal, validasi, transformasi target, lipatan waktu, dan evaluasi.
- `notebooks/template_model.ipynb` — template yang dipakai anggota pelatih model.
- `docs/KAMUS_DATA.md` dan `docs/KEPUTUSAN_METODOLOGI.md` — definisi fitur serta alasan keputusan.

### Cara memeriksa fondasi

Dari akar proyek:

```bash
python -m py_compile src/fondasi.py src/fitur_kelompok_bidang.py
python src/fitur_kelompok_bidang.py
python src/fondasi.py
python src/fondasi.py --tinjau-psdku
```

Hasil yang diharapkan:

- skenario `dengan_lag`: latih 2022–2024 dan uji 2025;
- skenario `tanpa_lag`: latih 2021–2024 dan uji 2025;
- tidak ada fitur terlarang atau NaN pada matriks model;
- `lipatan_waktu()` menghasilkan dua lipatan untuk `dengan_lag` dan tiga untuk `tanpa_lag`;
- tinjauan PSDKU melaporkan 182 prodi non-fakultas dalam katalog.

### Bila fondasi perlu diubah

1. Pastikan perubahan diperlukan untuk semua model, bukan hanya satu algoritma.
2. Bahas dampaknya terhadap kesetaraan data dengan tim.
3. Perbarui keputusan metodologi atau kamus data terlebih dahulu bila definisi berubah.
4. Uji kedua skenario dan seluruh jalur.
5. Beri tahu Ihsan, Shiddiq, dan Duha bahwa notebook mereka harus dijalankan ulang.
6. Catat perubahan di `docs/CHANGELOG.md` dan statusnya di `docs/PEMBAGIAN_TUGAS.md`.

Jangan mengubah `data/mentah/` secara manual dan jangan memasukkan kolom berstatus **Dilarang**.

## Tahap 2 — Baseline

Status saat ini: **selesai**.

### Menjalankan baseline

```bash
python -m jupyter nbconvert --to notebook --execute --inplace notebooks/00_baseline.ipynb
```

Notebook menghasilkan:

- baseline rata-rata peminat per `kelompok_bidang` untuk dua skenario;
- baseline `peminat_lag1` untuk skenario dengan lag;
- hasil gabungan, SNBP, dan SNBT di `hasil/evaluasi.csv`.

Setelah menjalankan, periksa bahwa tabel resmi hanya berisi hasil yang memang siap diserahkan. Jangan memakai pengujian sementara dengan nama model resmi. Untuk pengujian fungsi, gunakan `evaluasi(..., simpan=False)` atau arahkan `FONDASI_FILE_EVALUASI` ke berkas uji.

### Pemeriksaan selesai

- Notebook berjalan dari atas ke bawah tanpa error.
- Rata-rata kelompok dihitung hanya dari data latih.
- Baseline lag-1 hanya dijalankan pada skenario `dengan_lag`.
- `hasil/evaluasi.csv` tidak berisi hasil percobaan atau model milik anggota lain yang belum final.

## Tahap 3 — Perbandingan dan pemilihan model

Status saat ini: **menunggu** hasil tiga model.

### Prasyarat

Jangan mulai pemilihan model sebelum tersedia:

- hasil Linear Regression dari Ihsan;
- hasil Random Forest, feature importance, dan rentang prediksi dari Shiddiq;
- hasil XGBoost dari Duha;
- kedua skenario dan kedua versi target untuk setiap model;
- konfirmasi bahwa semuanya memakai fondasi dan data uji yang sama.

### Langkah perbandingan

1. Validasi skema `hasil/evaluasi.csv`: nama model, skenario, jalur, target, jumlah baris, jumlah fitur, MAE, MAPE, R², RMSLE, dan catatan.
2. Tolak hasil yang mengubah data/evaluasi bersama atau memakai data uji untuk penyetelan.
3. Susun tabel perbandingan untuk konfigurasi yang setara.
4. Bandingkan semua model dengan baseline yang relevan, terutama baseline lag-1 pada skenario dengan lag.
5. Sebelum menyatakan model terbaik, sepakati aturan pemilihan bersama tim/dosen dan catat di `KEPUTUSAN_METODOLOGI.md`.
6. Gunakan metrik utama secara bersama; jangan memilih hanya karena unggul pada satu angka tanpa membahas metrik lain, prediksi negatif, dan kestabilan antarskenario.
7. Simpan tabel dan grafik final di `hasil/` serta catat cara pembuatannya.

## Integrasi ke Streamlit

Koordinasikan struktur aplikasi dengan Duha. Mikail menangani bagian model berikut:

- **Estimasi prodi baru:** gunakan konfigurasi `tanpa_lag`, karena prodi baru tidak memiliki riwayat.
- **Pemetaan prodi:** gunakan fungsi pemetaan yang sama dari `src/fitur_kelompok_bidang.py`; jangan menyalin aturan ke aplikasi.
- **Perbandingan model:** baca tabel hasil final, bukan angka yang diketik manual.

Saat menyimpan model final, dokumentasikan versi pustaka, daftar fitur, urutan kolom, skenario, transformasi target, dan cara memuat artefak. Pastikan masukan aplikasi divalidasi dan kesalahan pengguna ditampilkan dengan bahasa yang jelas.

## Serah terima Mikail

Sebelum menandai tahap selesai, kirim ke grup:

- nama dan lokasi artefak;
- perintah menjalankan atau membuka;
- hasil pemeriksaan;
- keputusan metodologi yang berubah;
- model/berkas yang masih ditunggu;
- keterbatasan yang harus disebutkan di laporan.
