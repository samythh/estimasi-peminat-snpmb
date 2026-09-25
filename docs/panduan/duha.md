# Panduan Duha

## Tanggung jawab

Duha mengerjakan menu Eksplorasi Data di Streamlit, model XGBoost, dan BAB III.

## Tahap 1 — Eksplorasi Data di Streamlit

Bagian eksplorasi dapat dibuat tanpa menunggu model.

### Data

Gunakan `data/olahan/snpmb_panel.csv` sebagai sumber utama. Untuk tampilan prodi:

- keluarkan baris `is_fakultas == 1`;
- tampilkan hanya baris yang memiliki `tahun` dan `peminat`;
- perlakukan SNBP dan SNBT sebagai jalur terpisah;
- jangan menjumlahkan peminat SNBP dan SNBT;
- jangan mengubah CSV secara manual.

### Tampilan minimum

Menu Eksplorasi Data minimal memiliki:

1. filter PTN;
2. filter jalur (`SNBP`/`SNBT`);
3. filter rentang atau pilihan tahun;
4. filter satu atau beberapa program studi;
5. grafik tren `tahun` terhadap `peminat`;
6. tabel data yang sesuai dengan grafik;
7. keterangan sumber dan tanggal akses data.

Tambahkan pesan yang jelas bila kombinasi filter tidak menghasilkan data. Pastikan label grafik memuat satuan jumlah peminat dan jalur yang dipilih.

### Struktur dan cara menjalankan

Sepakati nama entry point dengan tim; rekomendasi awal adalah `app.py` di akar proyek dengan modul pendukung di folder aplikasi bila diperlukan. Setelah Streamlit benar-benar digunakan, tambahkan versinya ke `requirements.txt`.

Perintah menjalankan yang harus didokumentasikan:

```bash
streamlit run app.py
```

Gunakan jalur relatif terhadap akar proyek dan cache pembacaan data dengan mekanisme Streamlit yang sesuai. Jangan menyalin data ke lokasi baru hanya untuk aplikasi.

### Pemeriksaan selesai

- Aplikasi dapat dijalankan dari lingkungan bersih setelah memasang `requirements.txt`.
- Semua filter bekerja sendiri-sendiri dan bersama-sama.
- Pergantian jalur tidak mencampurkan SNBP dan SNBT.
- Grafik dan tabel menunjukkan baris yang sama.
- Kondisi kosong atau berkas tidak ditemukan tidak menyebabkan layar error mentah.
- Tangkapan layar dan cara menjalankan dicantumkan pada serah terima.

## Tahap 2 — XGBoost

### Membuat notebook

```powershell
Copy-Item notebooks/template_model.ipynb notebooks/03_xgboost.ipynb
```

Pada sel `# === ISI BAGIAN INI ===`:

1. Ubah `NAMA_MODEL` menjadi `"xgboost"`.
2. Biarkan `JALUR_DIPAKAI = [None]` kecuali tim menyepakati evaluasi tambahan per jalur.
3. Aktifkan model awal:

```python
return XGBRegressor(
    n_estimators=500,
    learning_rate=0.05,
    max_depth=6,
    random_state=RANDOM_STATE,
    n_jobs=-1,
)
```

4. Hapus atau nonaktifkan `DummyRegressor` sementara.
5. Jangan mengubah sel `# === JANGAN DIUBAH ===`.
6. Jalankan seluruh notebook dari atas.

### Penyetelan hyperparameter

Jika melakukan penyetelan, gunakan `lipatan_waktu(X_train)`. Parameter yang dapat diperiksa antara lain `n_estimators`, `learning_rate`, `max_depth`, `min_child_weight`, `subsample`, dan `colsample_bytree`.

Aturan:

- mulai dari ruang pencarian kecil dan catat seluruh kandidat;
- jangan menggunakan data 2025 untuk early stopping atau memilih parameter;
- jika memakai early stopping, ambil validasi terakhir dari data latih sesuai urutan waktu;
- jangan mengandalkan kemampuan XGBoost menangani nilai kosong karena fondasi bersama sengaja memberi data tanpa NaN agar setara dengan model lain;
- target log harus dikembalikan ke skala orang sebelum evaluasi.

### Pemeriksaan selesai

- Skenario `dengan_lag` dan `tanpa_lag` tersedia.
- Target asli dan log tersedia.
- Konfigurasi final serta alasan pemilihan tercatat.
- `random_state=42` digunakan.
- Hasil disimpan melalui `evaluasi()` dan dibandingkan dengan baseline.
- Tidak ada data uji yang digunakan selama penyetelan.

## Tahap 3 — BAB III

BAB III harus menjelaskan implementasi yang benar-benar digunakan, bukan rencana awal yang sudah berubah.

### Struktur yang disarankan

1. **Sumber dan pengumpulan data:** endpoint SNPMB, jalur, periode, tanggal akses, penyimpanan mentah.
2. **Pembentukan panel:** satu baris per prodi × jalur × tahun dan pembuatan lag berdasarkan nilai tahun.
3. **Penyaringan:** target tersedia, entri fakultas dikeluarkan, tanpa imputasi.
4. **Fitur:** numerik, kategorik, biner, lag, pengelompokan bidang, serta fitur yang dilarang.
5. **Pembagian data:** latih 2021–2024 dan uji 2025.
6. **Algoritma:** baseline, Linear Regression, Random Forest, dan XGBoost beserta konfigurasi final.
7. **Skenario eksperimen:** dengan/tanpa lag dan target asli/log.
8. **Validasi:** expanding window melalui `lipatan_waktu()`.
9. **Evaluasi:** MAE, MAPE, R², RMSLE, termasuk perlakuan target nol pada MAPE.
10. **Implementasi aplikasi:** alur eksplorasi dan, setelah terintegrasi, alur estimasi.

Gunakan `docs/KEPUTUSAN_METODOLOGI.md` sebagai dasar alasan dan `docs/KAMUS_DATA.md` untuk definisi kolom. Jangan menyalin angka jumlah baris sebelum memeriksa keluaran final karena jumlahnya berbeda menurut skenario.

### Pemeriksaan BAB III

- Seluruh istilah cocok dengan kode dan kamus data.
- Tidak menyatakan split acak, imputasi, atau K-fold biasa.
- Tidak menyebut Unand sebagai studi kasus.
- Diagram alur, bila ada, sesuai urutan kode aktual.
- Konfigurasi model sama dengan notebook final.
- Keterbatasan asumsi daya tampung dan deteksi berbasis nama disebutkan.

## Serah terima Duha

Laporkan lokasi kode Streamlit, cara menjalankan, tangkapan layar, notebook XGBoost, konfigurasi final, hasil evaluasi, serta lokasi BAB III. Sebutkan bagian aplikasi atau metodologi yang masih menunggu integrasi Mikail.
