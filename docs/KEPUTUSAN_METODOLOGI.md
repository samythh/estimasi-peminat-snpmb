# Keputusan Metodologi

Catatan setiap keputusan yang memengaruhi data, fitur, atau evaluasi, **beserta alasannya**. Tujuannya ganda: menjadi bahan Bab Metodologi, dan menjadi jawaban siap pakai saat penguji bertanya "kenapa begini?".

Format tiap entri: **Keputusan** · **Alasan** · *Alternatif yang ditolak*.

---

## Ruang lingkup dan target

### K-01 · Cakupan nasional, Unand hanya contoh
**Keputusan:** Model dilatih pada seluruh PTN peserta SNPMB. Universitas Andalas hanya dipakai sebagai ilustrasi di analisis deskriptif.
**Alasan:** Judul penelitian bertujuan membentuk *angka pembanding antar perguruan tinggi*, yang hanya mungkin bila modelnya belajar dari seluruh PTN.

### K-02 · Tugas regresi dengan target `peminat`
**Keputusan:** Target adalah jumlah pendaftar per prodi × jalur × tahun. Jenis tugasnya regresi.
**Alasan:** Yang diprediksi berupa angka, bukan kategori.
**Catatan:** `peminat` adalah data cacah yang sangat menceng. Lihat T-03.

### K-03 · SNBP dan SNBT tidak dijumlahkan
**Keputusan:** Kedua jalur diperlakukan sebagai dua deret terpisah. `jalur` menjadi fitur (model gabungan) atau penyaring (model per jalur).
**Alasan:** Satu pendaftar dapat melamar prodi yang sama di kedua jalur, sehingga penjumlahan menghitung orang yang sama dua kali. Tren kedua jalur juga bisa berlawanan arah; misalnya Hukum Unand 2021–2025 turun 34% di SNBP tetapi naik 6% di SNBT.
*Ditolak:* menjumlahkan jadi "total peminat prodi".

---

## Data dan fitur

### K-04 · Lag dihitung dari nilai tahun
**Keputusan:** Fitur lag dibuat dengan *self-merge* pada `(id_prodi, jalur, tahun−1)`. Tahun sebelumnya yang tidak ada menghasilkan NaN.
**Alasan:** Riwayat sebagian prodi bolong (SNBP 25 prodi, SNBT 8 prodi). `shift()` posisi akan mengambil tahun terdekat yang ada dan salah melabelinya sebagai "tahun lalu". Kebenaran implementasi diuji: 33.037 dari 33.037 nilai `peminat_lag1` cocok dengan peminat t−1.
*Ditolak:* `groupby().shift(1)`.

### K-05 · Tanpa imputasi
**Keputusan:** Nilai kosong tidak diisi. Baris tanpa target atau tanpa lag yang dibutuhkan dikeluarkan.
**Alasan:** Nilai isian adalah data yang tidak pernah diamati. Untuk Linear Regression, placeholder seperti −999 juga merusak koefisien.
*Ditolak:* placeholder bernilai di luar rentang seperti pada Yalaoui & Boukhedouma (2026, Rule 2.1–2.2), isian nol, isian rata-rata.

### K-06 · Pembagian data berdasarkan waktu
**Keputusan:** Latih 2021–2024, uji 2025.
**Alasan:** Tujuan model adalah meramal tahun yang belum terjadi. Pembagian acak akan memasukkan informasi masa depan ke data latih.
*Ditolak:* pembagian acak 70–90%.

### K-07 · Fitur yang dilarang
**Keputusan:** Kolom berikut tidak boleh menjadi fitur:

| Kolom | Alasan |
|---|---|
| `terima`, keketatan tahun berjalan | Baru diketahui setelah seleksi |
| `total_peminat_ptn` tahun berjalan | Memuat target baris itu sendiri. Versi lag diperbolehkan |
| `terima_lag1` | Kosong 100% di SNBT, sehingga fitur tidak setara antar jalur |
| `proporsi_peminat_lokal`, `jumlah_provinsi_asal` | Hasil pendaftaran tahun berjalan, dan hanya ada di SNBT |
| Kolom identitas (`id_ptn`, `ptn_nama`, `id_prodi`, `kode_prodi`, `prodi`, `tahun`) | Pengenal, bukan karakteristik |

### K-08 · Pengelompokan bidang diadaptasi dari ISCED-F 2013
**Keputusan:** `kelompok_bidang` ditentukan dengan pencocokan kata kunci pada nama prodi yang dinormalisasi. Kelompoknya dipadankan dengan bidang besar ISCED-F 2013 (UNESCO).
**Alasan:** API SNPMB tidak menyediakan data rumpun. ISCED-F 2013 dipilih karena merupakan standar internasional yang dapat disitasi dan cukup rinci. Rumpun ilmu dalam UU No. 12/2012 Pasal 10 terlalu kasar: sebagian besar prodi menumpuk di rumpun "terapan".

**Padanan:**

| Kelompok | ISCED-F 2013 | Prodi |
|---|---|---|
| teknik | 06 ICT + 07 Engineering, manufacturing and construction | 1.303 |
| pendidikan | 01 Education | 954 |
| pertanian | 08 Agriculture, forestry, fisheries and veterinary | 673 |
| sosial_humaniora | 02 (humaniora) + 03 Social sciences, journalism and information + hukum | 642 |
| ekonomi | 04 Business, administration (tanpa hukum) | 582 |
| sains | 05 Natural sciences, mathematics and statistics | 411 |
| kesehatan | 09 Health and welfare | 333 |
| seni | 02 Arts and humanities (seni) | 164 |
| pariwisata | 10 Services (hospitality, travel, tourism, catering) | 63 |
| olahraga | 10 Services (sports) | 25 |

**Penyesuaian terhadap ISCED:**

| Penyesuaian | ISCED menempatkan di | Alasan |
|---|---|---|
| Hukum → sosial_humaniora | 04 bersama bisnis | Di Indonesia, ilmu hukum berdiri sebagai fakultas sosial, bukan bagian dari fakultas ekonomi/bisnis |
| Kedokteran hewan & veteriner → kesehatan | 08 pertanian | (1) Pendaftar mempersepsikannya sebagai kedokteran: bergelar dokter, ada pendidikan profesi. (2) Median peminat per kursi 2025 (SNBP 6,5; SNBT 8,3) berada di antara kesehatan (19,7; 17,2) dan pertanian (2,3; 2,1), dan di SNBT lebih dekat ke kesehatan. Model meramal perilaku pendaftar, sehingga persepsi pendaftar lebih relevan |
| Teknologi pangan → pertanian | 07 rekayasa (*food processing*) | Di Indonesia, prodi ini hampir selalu berada di fakultas pertanian atau teknologi pertanian |
| 10 Services dipecah menjadi pariwisata dan olahraga | satu bidang | Keduanya kluster yang homogen dan cukup besar, dengan pola peminat yang diduga berbeda |
| Pendidikan jasmani/olahraga → pendidikan | 01 Education | Sesuai ISCED: programnya mencetak guru |

**Aturan prioritas** (yang pertama cocok menang): pengecualian nama persis → *PENDIDIKAN DOKTER* ke kesehatan → pendidikan → pengecualian teknik sipil/infrastruktur → kesehatan → seni → pertanian → teknik → sains → pengecualian hukum/dakwah → ekonomi → sosial_humaniora → olahraga → pariwisata. Rinciannya ada di docstring `src/fitur_kelompok_bidang.py`.

**Pengecualian nama persis** (`PETA_KHUSUS`): *SAINS INFORMASI* → teknik (dugaan, belum diverifikasi), *PENGELOLAAN LINGKUNGAN* → pertanian, *SENI KULINER* → pariwisata.

**Validasi:** dua sumber kesalahan ditemukan dan diperbaiki. Kata kunci yang terlalu umum (`PERAWAT` cocok di *PERAWATAN* mesin, `PROFESI` di *PROFESIONAL*) salah menempatkan 31 prodi. Pencocokan di tengah kata (`IKAN` di *PERBAIKAN*, `LAHAN` di *PENGOLAHAN*, `TARI` di *SEKRETARI*) salah menempatkan 16 prodi lagi, sehingga kata kunci kini hanya dicocokkan di awal kata. Sisa `belum_terpetakan` = 0.

**Cara menyebut di laporan:** "pengelompokan bidang ilmu berbasis aturan, diadaptasi dari ISCED-F 2013", bukan "klasifikasi".

### K-09 · Entri fakultas ITB dikeluarkan dari pemodelan
**Keputusan:** 21 entri ITB yang diterima per fakultas/sekolah ditandai `is_fakultas = 1` dan dikeluarkan dari data pemodelan. Datanya tidak dihapus.
**Alasan:** Peminatnya gabungan beberapa prodi, sehingga bukan pembanding yang setara dengan satu prodi di PTN lain. Porsinya 0,4%.

### K-10 · Pemetaan provinsi PTN
**Keputusan:** `Jakarta Raya` → `DKI Jakarta`, `Yogyakarta` → `DI Yogyakarta`. `Papua Selatan` **tidak** dipetakan.
**Alasan:** Daftar PTN dan data peminat memakai penamaan berbeda. Papua Selatan baru dimekarkan pada 2022, sementara data peminat masih memakai "Papua" gabungan; memetakannya akan menggelembungkan proporsi peminat lokal.

### K-11 · Anomali dibiarkan, tidak dikutip
**Keputusan:** Nilai yang dicurigai tidak dikoreksi atau dipangkas, tetapi juga tidak dikutip sebagai temuan.
**Kasus:** Administrasi Perkantoran (D3, Unand), SNBT: 166 → 2.273 → 2.252 peminat untuk ±26 kursi. Lonjakan 13× dalam setahun kemungkinan artefak pencatatan sumber.
*Ditolak:* *outlier capping* (mengubah nilai asli).

### K-12 · Data mentah disimpan dan dipakai ulang
**Keputusan:** Respons API disimpan utuh sebelum diolah, dan dipakai ulang secara bawaan.
**Alasan:** Kesalahan di tahap pengolahan dapat diperbaiki tanpa pengambilan ulang, dan data yang dianalisis tetap sama meskipun sumbernya berubah.

---

## Hal yang masih terbuka

Diputuskan sebelum atau saat pembuatan `fondasi.py`.

### T-01 · `daya_tampung_kini` atau `daya_tampung` tahun berjalan?
`daya_tampung_kini` berisi daya tampung **2026** yang ditempelkan ke semua baris 2021–2025. Contoh: Sistem Informasi Unand baris 2021 berisi 30, padahal daya tampung 2021 adalah 26. Memakainya sebagai fitur untuk baris historis berarti memakai informasi dari masa depan.
Kandidat pengganti: `daya_tampung` tahun baris itu, yang diumumkan sebelum pendaftaran dan karenanya sah. `daya_tampung_kini` baru relevan saat meramal 2026.

### T-02 · `is_new` tidak berguna sebagai fitur
Bernilai 0 di seluruh 42.930 baris bertarget. Prodi baru tidak punya riwayat, jadi tidak pernah masuk data latih.

### T-03 · Transformasi log pada target?
`peminat` menceng kuat (kebanyakan puluhan–ratusan, sedikit ribuan). MAE akan didominasi prodi besar. Pertimbangkan `log1p(peminat)` saat melatih, dengan prediksi dikembalikan ke skala asli sebelum evaluasi.

### T-04 · Definisi `is_pendidikan` dan `is_psdku`
Perlu dipastikan: apakah `is_pendidikan` berarti PTN pendidikan (UNP, UPI, UNY, dst.) atau prodi kependidikan? Yang kedua sudah tercakup `kelompok_bidang = pendidikan`. `is_psdku` kemungkinan dideteksi dari nama prodi yang memuat "PSDKU" atau "KAMPUS ...".

### T-05 · `peminat_lag2` tidak dipakai secara bawaan
Menyertakannya menghilangkan banyak baris. Jumlah pastinya dilaporkan oleh `muat_data()`.

---

## Rujukan

- UNESCO Institute for Statistics (2014). *ISCED Fields of Education and Training 2013 (ISCED-F 2013).*
- Undang-Undang Republik Indonesia Nomor 12 Tahun 2012 tentang Pendidikan Tinggi, Pasal 10.
- Yalaoui, M., & Boukhedouma, S. (2026). A structured machine learning based framework for multidimensional data quality assessment. *Journal of Big Data* (in press). https://doi.org/10.1186/s40537-026-01520-7. Dirujuk untuk tahap validasi pasca-prapemrosesan (§3.3); praktik imputasi dan pembagian acaknya **tidak** diadopsi.
