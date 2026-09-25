# Panduan Ihsan

## Tanggung jawab

Ihsan mengerjakan BAB I, BAB II, verifikasi daftar pustaka, model Linear Regression, serta BAB V setelah hasil akhir tersedia.

## Tahap 1 — BAB I dan BAB II

### Sumber yang harus dibaca

- Judul dan ruang lingkup di `README.md`.
- Keputusan K-01–K-18 di `docs/KEPUTUSAN_METODOLOGI.md`.
- Definisi data di `docs/KAMUS_DATA.md`.
- Grafik/deskripsi yang sudah tersedia di `analisis/` dan `hasil/grafik/`.
- PPT dan daftar pustaka kelompok di folder bersama setelah tautannya dicantumkan.

### BAB I

Susun dengan urutan berikut:

1. **Latar belakang:** kebutuhan memperkirakan jumlah peminat prodi dan membentuk angka pembanding antar-PTN.
2. **Rumusan masalah:** fokus pada estimasi, perbandingan model, pengaruh fitur lag, dan pemanfaatan hasil; jangan menjadikan Universitas Andalas sebagai studi kasus.
3. **Batasan:** data SNPMB 2021–2025, jalur SNBP/SNBT terpisah, target `peminat`, model yang disepakati, serta keterbatasan data.
4. **Tujuan:** selaras satu per satu dengan rumusan masalah.
5. **Manfaat:** untuk perguruan tinggi, calon mahasiswa/pengguna informasi, dan pengembangan akademik tanpa klaim yang melampaui data.

### BAB II

Minimal mencakup:

- SNPMB, SNBP, dan SNBT;
- regresi dan karakter target berupa data cacah;
- Linear Regression, Random Forest, dan XGBoost;
- fitur lag dan validasi berbasis waktu;
- MAE, MAPE, R², dan RMSLE;
- pengelompokan bidang berbasis aturan yang diadaptasi dari ISCED-F 2013;
- penelitian terdahulu yang benar-benar relevan.

Jangan menyebut `kelompok_bidang` sebagai klasifikasi dari SNPMB. Gunakan istilah “pengelompokan bidang ilmu berbasis aturan, diadaptasi dari ISCED-F 2013”.

### Verifikasi jurnal satu per satu

Untuk setiap referensi:

1. Buka tautan penerbit atau DOI, bukan hanya hasil mesin pencari.
2. Cocokkan judul, seluruh nama penulis, tahun, nama jurnal/prosiding, volume, nomor, halaman, dan DOI.
3. Pastikan isi sumber mendukung klaim yang diberi sitasi.
4. Tandai sumber yang tidak dapat dibuka atau metadata-nya berbeda; jangan menebak.
5. Hapus entri ganda dan seragamkan format sitasi.
6. Simpan tabel pemeriksaan berisi `sitasi`, `tautan`, `metadata cocok`, `relevansi`, dan `catatan`.

### Pemeriksaan BAB I–II

- Judul penelitian sama persis dengan README.
- Unand hanya contoh ilustrasi.
- Rumusan masalah, tujuan, metode, dan manfaat memakai istilah yang konsisten.
- Semua angka memiliki sumber atau ditandai sebagai hasil pengolahan tim.
- Tidak ada referensi yang belum diperiksa tetapi ditulis seolah sudah valid.

## Tahap 2 — Linear Regression

### Membuat notebook

Dari akar proyek:

```powershell
Copy-Item notebooks/template_model.ipynb notebooks/01_linear_regression.ipynb
```

Buka salinan tersebut. Pada sel `# === ISI BAGIAN INI ===`:

1. Ubah `NAMA_MODEL` menjadi `"linear_regression"`.
2. Biarkan `JALUR_DIPAKAI = [None]` kecuali tim menyepakati evaluasi per jalur.
3. Aktifkan model berikut:

```python
return make_pipeline(StandardScaler(), LinearRegression())
```

4. Hapus atau nonaktifkan `DummyRegressor` sementara.
5. Jangan mengubah sel `# === JANGAN DIUBAH ===`.
6. Jalankan semua sel dari atas.

Template otomatis menjalankan skenario `dengan_lag` dan `tanpa_lag`, masing-masing pada target asli dan log.

### Penyetelan dan interpretasi

Linear Regression dasar tidak memerlukan pencarian hyperparameter besar. Jika menambah varian seperti regularisasi, minta persetujuan tim karena algoritmanya berubah. Jangan memilih pengaturan memakai data 2025.

Perhatikan:

- penskalaan harus berada di dalam pipeline agar hanya dipelajari dari data latih;
- prediksi negatif harus dilaporkan, bukan diam-diam dibuang, kecuali fondasi bersama menetapkan perlakuan yang sama untuk semua model;
- koefisien setelah standardisasi dan one-hot perlu ditafsirkan dengan hati-hati;
- target log wajib dikembalikan dengan `dari_log()` sebelum evaluasi.

### Pemeriksaan selesai

- Notebook berjalan tanpa error dari atas ke bawah.
- Tidak membaca CSV dan membuat split sendiri.
- Tidak mengubah fitur, indeks uji, atau fungsi evaluasi bersama.
- Empat konfigurasi utama tercatat di `hasil/evaluasi.csv`.
- Hasil dibandingkan dengan baseline yang sesuai.
- Catatan menjelaskan prediksi negatif atau anomali bila ada.

## Tahap 3 — BAB V

Mulai setelah tabel perbandingan dan model terbaik disepakati.

### Kesimpulan

Jawab rumusan masalah secara langsung berdasarkan hasil, mencakup:

- model dan konfigurasi terpilih;
- perbandingan dengan baseline;
- perbedaan skenario dengan/tanpa lag dan target asli/log;
- batas penggunaan hasil sebagai angka pembanding.

### Saran

Bedakan saran teknis dan saran penelitian lanjutan. Hubungkan saran dengan keterbatasan nyata, misalnya panjang riwayat, kualitas nama prodi, asumsi daya tampung historis, PSDKU yang tidak terdeteksi dari nama, dan perubahan kebijakan penerimaan.

Jangan memasukkan hasil baru yang belum dibahas pada BAB IV.

## Serah terima Ihsan

Laporkan lokasi BAB I–II, tabel verifikasi pustaka, notebook Linear Regression, baris hasil evaluasi, dan BAB V. Cantumkan bagian yang masih menunggu keputusan atau hasil anggota lain.
