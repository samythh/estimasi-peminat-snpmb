# Panduan Shiddiq

## Tanggung jawab

Shiddiq mengerjakan revisi PPT, model Random Forest, feature importance, rentang prediksi untuk prodi baru, dan BAB IV.

## Tahap 1 — Revisi PPT

Gunakan judul persis berikut:

> Estimasi Jumlah Peminat Program Studi Menggunakan Regresi pada Data SNPMB sebagai Dasar Pembentukan Angka Pembanding Antar Perguruan Tinggi

### Daftar revisi wajib

- Ganti slide judul.
- Pada rumusan masalah dan tujuan nomor 4–5, hapus kata “Universitas Andalas”.
- Ubah judul/bagian manfaat menjadi “Manfaat bagi Perguruan Tinggi”.
- Koreksi `216%` menjadi `21,6%`.
- Koreksi `473%` menjadi `47,3%`.
- Hapus entri daftar pustaka yang ganda.
- Ganti “Zub dkk.” pada latar belakang menjadi “Raftopoulos dkk. (2024)”.
- Pastikan Unand disebut hanya sebagai contoh ilustrasi, bukan studi kasus.

### Pemeriksaan PPT

1. Cari seluruh kemunculan `Universitas Andalas`, `Unand`, `216%`, `473%`, `Zub`, dan entri referensi yang berulang.
2. Cocokkan judul, rumusan masalah, dan tujuan dengan dokumen laporan.
3. Pastikan grafik memiliki sumber, periode, satuan, dan label terbaca.
4. Buka PPT dalam mode presentasi untuk memeriksa teks terpotong atau elemen bergeser.
5. Simpan lokasi/tautan PPT final di `docs/PEMBAGIAN_TUGAS.md`.

## Tahap 2 — Random Forest

### Membuat notebook

```powershell
Copy-Item notebooks/template_model.ipynb notebooks/02_random_forest.ipynb
```

Pada sel `# === ISI BAGIAN INI ===`:

1. Ubah `NAMA_MODEL` menjadi `"random_forest"`.
2. Biarkan `JALUR_DIPAKAI = [None]` kecuali tim menyepakati evaluasi tambahan per jalur.
3. Aktifkan model awal:

```python
return RandomForestRegressor(
    n_estimators=300,
    random_state=RANDOM_STATE,
    n_jobs=-1,
)
```

4. Hapus atau nonaktifkan `DummyRegressor` sementara.
5. Jangan mengubah sel `# === JANGAN DIUBAH ===`.

### Penyetelan hyperparameter

Jika menyetel parameter, gunakan data latih dan `lipatan_waktu(X_train)` saja. Parameter yang wajar diuji antara lain `n_estimators`, `max_depth`, `min_samples_leaf`, dan `max_features`.

Jangan memakai `cv=5`, K-fold acak, atau skor data 2025 untuk memilih parameter. Simpan ruang pencarian, skor validasi, parameter terpilih, dan alasan pemilihannya di notebook.

### Feature importance

Sediakan dua keluaran bila waktu memungkinkan:

- `feature_importances_` sebagai ringkasan internal model;
- permutation importance pada lipatan validasi waktu sebagai pemeriksaan yang lebih mudah dipertanggungjawabkan.

Aturan:

1. Jangan memakai feature importance dari data uji untuk memilih fitur atau hyperparameter.
2. One-hot menghasilkan banyak kolom; untuk grafik utama, agregasikan kolom turunan ke fitur asal, misalnya seluruh `provinsi_*` menjadi `provinsi`.
3. Jelaskan bahwa impurity importance dapat bias pada fitur dengan banyak kemungkinan pemisahan.
4. Simpan tabel angka pendamping grafik agar hasil dapat diperiksa.

### Rentang prediksi prodi baru

Prodi baru tidak memiliki lag, sehingga gunakan model/configurasi `tanpa_lag`.

Metode awal yang diperbolehkan untuk Random Forest adalah persentil prediksi seluruh pohon, misalnya persentil ke-10 dan ke-90. Rentang ini harus disebut **rentang empiris antarpohon**, bukan confidence interval formal.

Jika model dilatih pada target log:

1. ambil prediksi setiap pohon pada skala log;
2. kembalikan setiap prediksi pohon dengan `dari_log()`;
3. baru hitung persentil pada skala jumlah orang.

Jangan menyusun sendiri urutan kolom untuk input prodi baru. Koordinasikan dengan Mikail agar input baru melewati transformasi yang sama dengan data latih. Minimal masukan yang perlu disepakati meliputi PTN, jalur, jenjang, portofolio, kelompok bidang, daya tampung, jumlah prodi PTN, provinsi, dan atribut struktural PTN.

Validasi rentang pada data validasi 2024 bila memungkinkan: laporkan berapa persen nilai aktual yang berada di dalam rentang. Jangan melakukan kalibrasi memakai data uji 2025.

### Pemeriksaan selesai

- Dua skenario dan dua target selesai dijalankan.
- `random_state=42` dan konfigurasi final tercatat.
- Hasil tersimpan melalui `evaluasi()`.
- Feature importance memiliki tabel dan penjelasan keterbatasan.
- Rentang prediksi hanya memakai skenario tanpa lag untuk prodi baru dan diberi nama yang tepat.
- Tidak ada pemilihan model berdasarkan data uji.

## Tahap 3 — BAB IV

BAB IV ditulis setelah hasil semua model tersedia.

### Struktur yang disarankan

1. Deskripsi data setelah penyaringan.
2. Hasil baseline.
3. Hasil Linear Regression, Random Forest, dan XGBoost.
4. Perbandingan skenario dengan/tanpa lag.
5. Perbandingan target asli/log.
6. Pemilihan model terbaik berdasarkan aturan yang sudah disepakati.
7. Feature importance Random Forest.
8. Contoh estimasi dan rentang prediksi prodi baru.
9. Analisis galat, keterbatasan, dan implikasi angka pembanding antar-PTN.

Gunakan tabel dari `hasil/evaluasi.csv`, bukan angka yang diketik ulang dari ingatan. Bahas hasil yang buruk dan anomali secara terbuka. Jangan menyatakan hubungan sebab-akibat dari feature importance.

## Serah terima Shiddiq

Laporkan tautan PPT final, notebook Random Forest, konfigurasi final, tabel evaluasi, tabel/grafik feature importance, metode rentang prediksi, validasi cakupan rentang, serta lokasi BAB IV.
