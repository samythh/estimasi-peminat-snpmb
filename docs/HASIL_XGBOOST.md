# Hasil XGBoost Duha — fondasi versi 2

## Berkas dan cara menjalankan

- `notebooks/03_xgboost.ipynb`: enam eksperimen dengan output eksekusi.
- `hasil/evaluasi.csv`: enam baris XGBoost versi fondasi 2; 15 baris baseline dari `main` dipertahankan.
- `scripts/jalankan_xgboost.py`: menjalankan notebook dengan interpreter aktif.
- `scripts/validasi_xgboost.py` dan `hasil/hasil_validasi_xgboost.json`: pemeriksaan tanpa melatih ulang.

Dari akar repo dengan Python 3.13:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements-xgboost.txt
.\.venv\Scripts\python.exe src/ambil_data_snpmb.py
.\.venv\Scripts\python.exe scripts/jalankan_xgboost.py
.\.venv\Scripts\python.exe scripts/validasi_xgboost.py
```

Notebook memuat data melalui `muat_data()`. Sel evaluasi template memanggil `latih_dan_prediksi()` sehingga prodi uji tidak ikut dilatih pada dua skenario prodi baru. Hasil ditulis oleh `evaluasi()`; menjalankan ulang konfigurasi yang sama mengganti enam baris XGBoost dengan kunci yang sama. Data 2025 tidak dipakai untuk memilih parameter.

## Konfigurasi

XGBoost 3.4.1; `n_estimators=500`, `learning_rate=0.05`, `max_depth=6`, `random_state=42`, dan `n_jobs=-1`. Konfigurasi mengikuti panduan Duha sebelum evaluasi, tanpa penyetelan atau early stopping. `buat_model(target)` menerima jenis target sesuai template, tetapi XGBoost memakai konfigurasi sama untuk target asli dan log. Jalur gabungan berarti SNBP dan SNBT menjadi observasi terpisah dengan fitur jalur; jumlah peminat kedua jalur tidak dijumlahkan.

| Skenario | Target | Latih | Uji | Fitur | MAE (orang) | MAPE (%) | R² | RMSLE | Prediksi negatif |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|
| Dengan lag | Asli | 21.507 | 8.508 | 76 | 70,23 | 33,61 | 0,9312 | Tidak tersedia | 124 |
| Dengan lag | Log | 21.507 | 8.508 | 76 | 68,67 | 24,59 | 0,9371 | 0,3615 | 0 |
| Tanpa lag | Asli | 32.959 | 9.799 | 71 | 185,86 | 146,25 | 0,6279 | Tidak tersedia | 491 |
| Tanpa lag | Log | 32.959 | 9.799 | 71 | 171,16 | 71,56 | 0,6165 | 0,7130 | 0 |
| Tanpa riwayat sendiri | Asli | 22.453 | 8.834 | 73 | 137,54 | 104,25 | 0,7153 | Tidak tersedia | 414 |
| Tanpa riwayat sendiri | Log | 22.453 | 8.834 | 73 | 129,35 | 49,78 | 0,7190 | 0,5763 | 0 |

MAE terendah XGBoost pada tiap skenario berasal dari target log. Pembanding yang sepadan pada versi fondasi 2: `baseline_lag1` dengan lag MAE 66,11; `baseline_rata_kelompok` tanpa lag MAE 299,57; `baseline_rata_sejenis` tanpa riwayat sendiri MAE 254,52. XGBoost belum mengalahkan baseline dengan lag, tetapi mengalahkan baseline pada dua skenario prodi baru. Perbandingan lintas skenario tidak langsung setara karena baris uji berbeda.

Tidak ada target nol yang dikecualikan dari MAPE. RMSLE target asli tidak tersedia karena ada prediksi negatif; angka negatif itu tidak dapat ditafsirkan sebagai jumlah peminat. Prediksi tidak dipangkas setelah melihat data uji.

## Pemeriksaan dan keterbatasan

Tiga sel `JANGAN DIUBAH` dan semua sel di luar `ISI BAGIAN INI` identik dengan template versi 2. Seluruh sel notebook dieksekusi tanpa error. `scripts/validasi_xgboost.py` memeriksa tiga skenario, urutan waktu pada validasi, enam kombinasi evaluasi, versi fondasi, dan ukuran data. Dashboard Hasil Pengujian untuk ketiga skenario juga lolos AppTest tanpa exception.

Asumsi kuota historis, pengelompokan bidang berbasis aturan, dan deteksi PSDKU mengikuti keputusan metodologi bersama. Model akhir untuk aplikasi dan pemilihan model terbaik masih menjadi tahap integrasi Mikail setelah hasil semua anggota tersedia.
