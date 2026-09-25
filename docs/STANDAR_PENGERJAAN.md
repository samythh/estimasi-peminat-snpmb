# Standar Pengerjaan

Aturan kerja bersama untuk seluruh anggota tim. Tujuannya satu: **hasil ketiga model harus bisa dibandingkan secara adil dan dipertanggungjawabkan di depan penguji.** Kalau satu anggota melanggar aturan data, hasil semua model ikut tidak bisa dibandingkan.

Setelah membaca standar ini, setiap anggota wajib mengikuti tutorial pribadinya melalui [PANDUAN_ANGGOTA.md](PANDUAN_ANGGOTA.md).

Kalau ada aturan yang menurutmu keliru, jangan dilanggar diam-diam. Bahas dulu dengan tim, lalu catat perubahannya di [KEPUTUSAN_METODOLOGI.md](KEPUTUSAN_METODOLOGI.md).

---

## 1. Struktur folder

| Folder | Isi | Boleh diubah? |
|---|---|---|
| `data/mentah/` | Respons asli API SNPMB | **Tidak.** Hanya ditulis oleh `ambil_data_snpmb.py --paksa-unduh` |
| `data/olahan/` | Panel hasil olahan | Hanya lewat skrip di `src/`, tidak diedit manual |
| `data/contoh_unand/` | Subset dan ringkasan contoh Unand | Lewat skrip di `analisis/` |
| `src/` | Kode bersama: pengambilan data, fitur, fondasi | Hanya setelah disepakati tim |
| `analisis/` | Analisis deskriptif dan grafik | Bebas, asal tidak mengubah `data/olahan/` |
| `notebooks/` | Baseline dan notebook model tiap anggota | Notebook milikmu sendiri |
| `hasil/` | Grafik, `evaluasi.csv` | Ditulis oleh kode, tidak diedit manual |
| `docs/` | Dokumentasi | Perbarui bila ada perubahan |

**Penamaan berkas:**
- Skrip: `kata_kerja_objek.py`, huruf kecil dan garis bawah (`ambil_data_snpmb.py`).
- Notebook: diberi nomor urut dan nama model (`01_linear_regression.ipynb`, `02_random_forest.ipynb`, `03_xgboost.ipynb`).
- Grafik: `topik_cakupan_periode.png` (`tren_peminat_unand_2021_2025.png`), selalu disertai CSV nilai dengan nama yang sama.

---

## 2. Aturan data (wajib)

1. **Tidak ada kebocoran data.** Informasi yang baru diketahui *setelah* pendaftaran atau seleksi tahun berjalan tidak boleh menjadi fitur. Daftar lengkapnya ada di [KAMUS_DATA.md](KAMUS_DATA.md), kolom *Status fitur*.
2. **Peminat SNBP dan SNBT tidak pernah dijumlahkan.** Satu pendaftar bisa melamar prodi yang sama di kedua jalur, jadi penjumlahan menghitung orang yang sama dua kali.
3. **Fitur lag dihitung dari nilai tahun, bukan urutan baris.** Kalau tahun sebelumnya tidak ada, lag dibiarkan kosong (NaN).
4. **Tidak ada data sintetis, pengisian nol, rata-rata, atau imputasi dalam bentuk apa pun.** Nilai kosong tetap kosong. Baris yang tidak bisa dipakai dikeluarkan, bukan diisi.
5. **Pembagian data berdasarkan waktu:** latih 2021–2024, uji 2025. Tidak boleh acak.
6. **Data uji hanya disentuh sekali, di akhir.** Penyetelan hyperparameter memakai data latih saja, misalnya validasi silang berbasis waktu di dalam 2021–2024.
7. **`random_state=42`** di setiap tempat yang relevan.
8. **Data mentah tidak diubah.** Semua koreksi dilakukan di kode pengolahan, supaya jejaknya terlihat.

---

## 3. Alur kerja

```
tinjau  →  diskusikan/konfirmasi  →  simpan  →  catat
```

- **Tinjau dulu.** Skrip yang mengubah data tetap (pemetaan, penyimpanan CSV) punya mode tinjau yang hanya mencetak hasil. Periksa distribusi dan contoh acaknya sebelum menyimpan.
- **Satu sumber kebenaran.** Setiap logika hanya ditulis di satu tempat. Contoh: pemetaan bidang hanya ada di `src/fitur_kelompok_bidang.py` dan dipanggil dari tempat lain, bukan disalin.
- **Setiap perubahan dicatat:**
  - seluruh perubahan penting pada data, kode, model, hasil, laporan, presentasi, tugas, atau jalur berkas → [CHANGELOG.md](CHANGELOG.md)
  - keputusan metodologis beserta alasannya → [KEPUTUSAN_METODOLOGI.md](KEPUTUSAN_METODOLOGI.md)
  - kolom baru atau perubahan arti/status fitur → [KAMUS_DATA.md](KAMUS_DATA.md)
  - perubahan pemilik, status, tenggat, dependensi, keluaran, atau lokasi artefak → [PEMBAGIAN_TUGAS.md](PEMBAGIAN_TUGAS.md)
- **Artefak di luar repositori tetap dilacak.** PPT, laporan, atau berkas di folder bersama harus memiliki tautan/lokasi dan status yang dicatat di `PEMBAGIAN_TUGAS.md`.
- **Selesai berarti dapat diverifikasi.** Status selesai membutuhkan artefak, cara membuka/menjalankan, serta hasil pemeriksaan. Kabar lisan saja belum cukup.

### Catatan minimum saat menyerahkan pekerjaan

Setiap penyerahan harus menjelaskan:

1. penanggung jawab dan tujuan pekerjaan;
2. nama/lokasi berkas yang dibuat atau diubah;
3. input, output, dan cara menjalankan atau membukanya;
4. asumsi dan keputusan yang digunakan;
5. pemeriksaan yang sudah dijalankan beserta hasilnya;
6. keterbatasan, masalah yang masih terbuka, dan ketergantungan berikutnya.

---

## 4. Konvensi kode

- **Bahasa Indonesia** untuk nama variabel, fungsi, dan komentar, mengikuti kode yang sudah ada.
- **Jalur relatif terhadap akar proyek**, jangan jalur absolut seperti `D:\...`:
  ```python
  AKAR = Path(__file__).resolve().parents[1]
  FILE_PANEL = AKAR / "data" / "olahan" / "snpmb_panel.csv"
  ```
- **CSV ditulis dengan `encoding="utf-8-sig"`** agar terbaca benar di Excel.
- **Keluaran konsol di Windows:** tambahkan `sys.stdout.reconfigure(encoding="utf-8")` di awal `main()`.
- **Pengambilan data:** jeda `time.sleep(1)` antar permintaan, `try/except` per PTN, dan catat yang gagal. Jangan dihilangkan.
- **Komentar menjelaskan *mengapa*, bukan *apa*.** Contoh yang baik: *"Dicocokkan lewat tahun, bukan shift(), supaya prodi dengan riwayat bolong tidak salah label."*

---

## 5. Untuk anggota yang melatih model

- **Selalu muat data lewat `muat_data()` dari `src/fondasi.py`.** Jangan membaca CSV sendiri dan menyusun fitur sendiri, supaya ketiga model memakai data yang persis sama.
- **Jangan ubah sel bertanda `# === JANGAN DIUBAH ===`** di template.
- **Catat hasil lewat `evaluasi()`**, jangan menyalin angka ke Excel secara manual.
- **Laporkan kedua skenario** (`dengan_lag` dan `tanpa_lag`) dan bandingkan dengan baseline. Model yang tidak mengalahkan baseline `prediksi = peminat_lag1` belum berguna.
- **Latih setiap model pada dua versi target:** skala asli dan `log1p`. Prediksi dari target log wajib dikembalikan ke skala orang sebelum evaluasi.
- **Penyetelan hyperparameter wajib memakai `lipatan_waktu()`** dari `fondasi.py`, bukan K-fold acak atau `cv=5`.
- **Linear Regression** biasanya perlu penskalaan fitur (`StandardScaler`). Lakukan di dalam bagianmu sendiri, dengan `fit` hanya pada data latih.
- **Metrik utama:** MAE (dalam satuan orang), MAPE, dan R². RMSLE dicatat sebagai metrik pelengkap.

---

## 6. Pelaporan dan sitasi

- **Kelompok bidang adalah pengelompokan buatan tim**, diadaptasi dari ISCED-F 2013, bukan data dari SNPMB. Tulis demikian, dan sebut "pengelompokan bidang ilmu berbasis aturan", bukan "klasifikasi", agar tidak dikira model klasifikasi.
- **Jangan klaim melebihi data.** Pola dari lima prodi pilihan bukan pola rumpun. Kalau mau mengklaim pola rumpun, uji dulu pada seluruh prodi.
- **Jangan mengutip anomali yang dicurigai** sebagai temuan (lihat [KEPUTUSAN_METODOLOGI.md](KEPUTUSAN_METODOLOGI.md#k-11)).
- **Sebut sumber dan tanggal akses:** *API publik SNPMB (snpmb.id), diakses September 2026.*
- **Grafik:** sumbu Y dimulai dari nol, skala dikunci sama saat membandingkan panel, satu warna per entitas yang konsisten, dan label teks tidak memakai warna garis.

---

## 7. Daftar periksa sebelum menyerahkan pekerjaan

- [ ] Kode berjalan dari atas sampai bawah tanpa error di komputer orang lain (jalur relatif, tidak ada `D:\...`).
- [ ] Tidak ada fitur berstatus *Dilarang* di [KAMUS_DATA.md](KAMUS_DATA.md).
- [ ] Tidak ada imputasi, `fillna`, atau baris sintetis.
- [ ] Data uji tidak dipakai untuk memilih model atau hyperparameter.
- [ ] `random_state=42`.
- [ ] Hasil tercatat di `hasil/evaluasi.csv` lewat `evaluasi()`.
- [ ] Perubahan penting tercatat di `docs/`.
- [ ] Status, bukti, dependensi, dan lokasi artefak sudah diperbarui di `docs/PEMBAGIAN_TUGAS.md`.
- [ ] Anggota berikutnya dapat memahami input, output, cara menjalankan, asumsi, dan keterbatasan tanpa penjelasan lisan tambahan.
