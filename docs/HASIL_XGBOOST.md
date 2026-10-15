# Hasil XGBoost

Pekerjaan ini hanya mencakup notebook XGBoost, hasil evaluasi, dan bukti pemeriksaannya. Tidak mencakup aplikasi atau BAB laporan.

## Berkas dan cara menjalankan

- `notebooks/04_xgboost.ipynb`: empat eksperimen lengkap dengan output eksekusi.
- `hasil/evaluasi.csv`: empat baris XGBoost, sembilan baseline tetap utuh.
- `scripts/jalankan_xgboost.py`: menjalankan notebook dengan interpreter aktif.
- `scripts/validasi_xgboost.py` dan `hasil/hasil_validasi_xgboost.json`: pemeriksaan tanpa pelatihan ulang.
- `requirements-xgboost.txt`: versi dependensi langsung yang dipakai saat eksekusi.

Dari akar proyek, gunakan Python 3.13:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements-xgboost.txt
.\.venv\Scripts\python.exe src/ambil_data_snpmb.py
.\.venv\Scripts\python.exe scripts/validasi_xgboost.py
```

Hasil dapat dibaca langsung di notebook tanpa pelatihan ulang. Untuk mereproduksi konfigurasi yang sama:

```powershell
.\.venv\Scripts\python.exe scripts/jalankan_xgboost.py
```

Perintah tersebut menimpa empat baris evaluasi dengan kunci yang sama. Tidak ada tuning atau early stopping menggunakan 2025. Jangan mengubah parameter berdasarkan skor uji yang sudah diketahui.

## Konfigurasi dan hasil

XGBoost 3.4.1; scikit-learn 1.9.1; pandas 3.0.5; NumPy 2.5.3. Semua eksperimen menggunakan `n_estimators=500`, `learning_rate=0.05`, `max_depth=6`, `random_state=42`, `n_jobs=-1`. Konfigurasi mengikuti panduan sebelum penilaian, tanpa tuning atau early stopping. Jalur gabungan digunakan sebagai kumpulan observasi terpisah dengan fitur jalur, bukan jumlah peminat lintas jalur.

| Skenario | Target | Latih | Uji | Fitur | MAE (orang) | MAPE (%) | R² | RMSLE | Prediksi negatif |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|
| Dengan lag | Asli | 23.445 | 9.416 | 72 | 114,15 | 50,59 | 0,6501 | Tidak tersedia | 288 |
| Dengan lag | Log | 23.445 | 9.416 | 72 | 102,75 | 32,29 | 0,7247 | 0,4130 | 0 |
| Tanpa lag | Asli | 32.959 | 9.799 | 70 | 173,69 | 125,20 | 0,6488 | Tidak tersedia | 396 |
| Tanpa lag | Log | 32.959 | 9.799 | 70 | 175,57 | 63,72 | 0,5219 | 0,7009 | 0 |

Tidak ada target nol yang dikecualikan dari MAPE pada empat eksperimen ini. RMSLE target asli tidak tersedia karena prediksi negatif; ini perilaku evaluasi bersama, bukan error eksekusi. Prediksi tidak dipangkas setelah melihat data uji.

Pada skenario dengan lag, baseline lag-1 memiliki MAE 67,54, MAPE 24,33%, R² 0,9465, dan RMSLE 0,3746. **XGBoost belum mengalahkan baseline lag-1.** Terhadap baseline rata-rata kelompok pada skenario yang sama (MAE 304,55), kedua varian XGBoost memiliki MAE lebih rendah.

Pada skenario tanpa lag, MAE kedua varian lebih rendah daripada baseline rata-rata kelompok (299,17). Target asli lebih baik pada MAE/R², sedangkan target log lebih baik pada MAPE dan menyediakan prediksi nonnegatif. Tidak disimpulkan ada satu varian yang unggul pada seluruh metrik. Perbandingan dengan baseline lag-1 lintas skenario tidak setara karena fitur dan baris uji berbeda.

## Pemeriksaan dan keterbatasan

Seluruh sel kode selain ISI BAGIAN INI identik dengan template. Contoh nama notebook pada petunjuk markdown disesuaikan menjadi 04_xgboost.ipynb atas permintaan Duha. Semua sel kode memiliki output eksekusi tanpa error. Fondasi, pembagian temporal, dan urutan lipatan waktu diperiksa. Jumlah baris/fitur evaluasi sesuai fondasi. Data mentah, template, dan kode fondasi tidak diubah.

Asumsi kuota historis, pengelompokan bidang berbasis aturan, dan deteksi PSDKU mengikuti K-08, K-13, dan K-16. Konfigurasi berasal dari panduan Duha sebelum evaluasi; bukan hasil pencarian parameter optimal. Model belum mengalahkan baseline lag-1. Pengembangan berikutnya perlu protokol validasi latih yang disepakati tim karena hasil 2025 sudah diketahui.
