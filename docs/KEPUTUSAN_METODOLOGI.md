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
**Catatan:** `peminat` adalah data cacah yang sangat menceng. Lihat K-15.

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

### K-11 · Anomali dibiarkan, tidak dikoreksi
**Keputusan:** Nilai yang dicurigai tidak dikoreksi atau dipangkas.
**Kasus:** Administrasi Perkantoran (D3, Unand), SNBT: 166 → 2.273 → 2.252 peminat untuk ±26 kursi.
**Tafsiran (diperbarui 2026-11-12):** semula diduga artefak pencatatan satu prodi. Data nasional menunjukkan kasus ini adalah contoh ekstrem dari lonjakan peminat vokasi SNBT mulai 2024 yang terjadi di sebagian besar prodi D3/D4 (lihat [K-19](#k-19)). Penyebab lonjakan belum diketahui, sehingga dilaporkan sebagai pola yang teramati, bukan sebagai kesalahan data.
*Ditolak:* *outlier capping* (mengubah nilai asli).

### K-12 · Data mentah disimpan dan dipakai ulang
**Keputusan:** Respons API disimpan utuh sebelum diolah, dan dipakai ulang secara bawaan.
**Alasan:** Kesalahan di tahap pengolahan dapat diperbaiki tanpa pengambilan ulang, dan data yang dianalisis tetap sama meskipun sumbernya berubah.

---

## Keputusan fondasi pemodelan

### K-13 · Gunakan `daya_tampung` tahun baris
**Keputusan:** Fitur memakai `daya_tampung` pada tahun yang sedang diprediksi. `daya_tampung_kini` tidak boleh menjadi fitur historis karena berisi kuota 2026 yang ditempelkan ke semua baris 2021–2025.
**Alasan:** Kuota tahun berjalan tersedia sebelum pendaftaran, sedangkan kuota 2026 merupakan informasi masa depan bagi baris historis.
**Asumsi:** Angka `daya_tampung` historis dari API adalah kuota yang diumumkan sebelum pendaftaran, bukan angka hasil revisi setelah seleksi. Data yang tersedia tidak cukup untuk membuktikan asumsi ini, sehingga harus disebutkan sebagai keterbatasan laporan.
*Ditolak:* memakai `daya_tampung_kini` untuk baris historis.

### K-14 · `is_new` tidak menjadi fitur
**Keputusan:** `is_new` dikeluarkan dari matriks fitur.
**Alasan:** Prodi baru tidak memiliki target historis dan otomatis tidak masuk data pemodelan; akibatnya `is_new` selalu 0 pada baris bertarget dan tidak membawa informasi.

### K-15 · Setiap model memakai target asli dan log
**Keputusan:** Linear Regression, Random Forest, dan XGBoost masing-masing dilatih dalam dua varian: target asli dan `log1p(peminat)`. Prediksi varian log dikembalikan ke skala orang dengan `expm1` sebelum dinilai.
**Alasan:** Transformasi target harus seragam antarmodel agar perbedaan skor tetap dapat dibaca sebagai perbedaan algoritma. Pengaruh transformasi log sekaligus menjadi temuan yang dapat dibandingkan.
**Metrik:** MAE, MAPE, dan R² tetap menjadi metrik utama. RMSLE dicatat sebagai metrik pelengkap karena MAE cenderung didominasi prodi besar, sedangkan MAPE sangat sensitif pada prodi dengan peminat kecil. Baris dengan target nol dikecualikan dari MAPE dan jumlahnya dicatat.

### K-16 · Fitur `is_pendidikan` dan `is_psdku`
**Keputusan:** `is_pendidikan` menandai 12 PTN kependidikan (eks-IKIP) berdasarkan nama PTN. Program kependidikan sendiri sudah tercakup oleh `kelompok_bidang = pendidikan`. `is_psdku` diturunkan dari nama prodi yang memuat `PSDKU`, `KAMPUS`, singkatan `K. KAB`/`K, KAB`/`KAMP`, salah ketik `PDSKU`, atau penanda `FIKKIA BANYUWANGI`.
**Validasi:** Pemetaan `is_pendidikan` diperiksa satu per satu. Pola PSDKU menandai 188 prodi non-fakultas dalam katalog: 176 memiliki target historis dan masuk kandidat pemodelan, sedangkan 12 merupakan prodi baru tanpa target. Tiga bentuk singkatan kampus di Politeknik Negeri Pontianak tertangkap oleh pola `K. KAB`/`K, KAB`.
**Perbaikan (2026-11-12):** enam prodi kampus cabang semula lolos: salah ketik `PDSKU` (1 prodi, Universitas Syiah Kuala), singkatan `KAMP` (1, Universitas Negeri Makassar), dan `FIKKIA BANYUWANGI` (4, kampus Universitas Airlangga di Banyuwangi, di luar kampus utama Surabaya). Sebelumnya 182 prodi (170 bertarget).
**Keterbatasan:** Kampus cabang yang namanya sama sekali tidak menyebut lokasi tidak dapat dideteksi dari nama. Manfaat prediktif kedua fitur tetap perlu diuji melalui ablasi setelah model tersedia.

### K-17 · `peminat_lag2` tidak dipakai secara bawaan
**Keputusan:** Fondasi bawaan hanya memakai `peminat_lag1` dan `daya_tampung_lag1`; `peminat_lag2` tersedia sebagai opsi eksperimen.
**Alasan:** Pemakaian lag kedua menghilangkan seluruh baris 2022 dan baris lain yang riwayatnya tidak lengkap. Membiarkan nilai kosong hanya untuk model tertentu membuat data latih antarmodel tidak lagi setara, sedangkan imputasi dilarang oleh K-05.

### K-18 · Validasi silang berbasis waktu
**Keputusan:** Penyetelan hyperparameter wajib memakai `lipatan_waktu()` dengan skema *expanding window*. Data uji 2025 tidak disentuh sampai evaluasi akhir.

| Skenario | Lipatan validasi |
|---|---|
| Dengan lag | latih 2022 → validasi 2023; latih 2022–2023 → validasi 2024 (2 lipatan) |
| Tanpa riwayat sendiri | sama, tetapi setiap tahun validasi dipecah menjadi 5 lipatan kelompok prodi (10 lipatan; K-24) |
| Tanpa lag | latih 2021 → validasi 2022; latih 2021–2022 → validasi 2023; latih 2021–2023 → validasi 2024, masing-masing dipecah menjadi 5 lipatan kelompok prodi (15 lipatan; K-24) |

**Alasan:** K-fold biasa dapat membuat model belajar dari tahun yang lebih baru untuk menebak tahun yang lebih lama, sehingga skor validasi terlalu optimistis dan tidak mencerminkan penggunaan model untuk meramal masa depan.
*Ditolak:* `KFold` acak dan `cross_val_score` dengan pembagian bawaan.

### K-19 · Penanda lonjakan peminat vokasi SNBT
**Pola yang teramati:** rasio median peminat 2024/2023 per prodi adalah SNBT D3 5,0×, SNBT D4 2,4×, dan SNBT S1 0,96×, sedangkan SNBP stabil (D3 1,2×, D4 1,25×, S1 1,0×). Sebanyak 86% prodi D3 SNBT setidaknya naik dua kali lipat. Median peminat D3 SNBT naik dari 63 (2023) menjadi 354 (2024) dan 466 (2025). Prodi D3 baru tercatat sejak 2023. **Penyebabnya belum diketahui** dan tidak boleh disebut di laporan sebelum terverifikasi dari sumber resmi.
**Keputusan:** data tidak dibuang dan tidak dikoreksi (K-11). Diskontinuitasnya ditandai dengan penanda biner untuk baris SNBT jenjang D3/D4. Penanda tidak dibuat berdasarkan dugaan penyebab. Bentuk penanda berbeda per skenario:

| Penanda | Bernilai 1 bila | Skenario | Baris |
|---|---|---|---|
| `is_rezim_vokasi_snbt` | tahun ≥ 2024 | `tanpa_lag` | 2.486 |
| `is_lintas_rezim_vokasi_snbt` | tahun = 2024 | `dengan_lag`, `tanpa_riwayat_sendiri` | 1.208 |

**Alasan perbedaan:** di skenario berbasis t−1, baris vokasi SNBT 2024 adalah satu-satunya baris latih yang pembandingnya (lag-1 atau prodi sejenis t−1) berasal dari sebelum lonjakan. Rasio median peminat terhadap lag-1 pada baris itu 3,2×, sedangkan pada data uji 2025 hanya 1,3×. Penanda tahun ≥ 2024 akan bernilai 1 pada keduanya, sehingga model belajar "penanda → naik tiga kali" lalu menerapkannya ke 2025. Penanda lintas rezim hanya menandai baris yang pembandingnya melintasi diskontinuitas; pada data uji 2025 nilainya 0.
**Pengukuran** (`notebooks/00_baseline.ipynb`, `hasil/analisis_penanda_rezim.csv`; data uji SNBT vokasi 2025):

| Skenario, baseline | Tanpa penanda | Penanda dipakai | Penanda tahun ≥ 2024 |
|---|---|---|---|
| `tanpa_lag`, rata-rata kelompok | MAE 503,6; R² 0,08 | MAE 514,8; R² 0,17 | (sama dengan kolom sebelumnya) |
| `dengan_lag`, lag-1 | MAE 123,8 | MAE 134,0 | MAE 1.383,6 |
| `tanpa_riwayat_sendiri`, rata-rata prodi sejenis | MAE 520,7 | MAE 496,4 | MAE 1.265,2 |

**Dasar keputusan:** alasan struktural di atas, yang terlihat dari data latih saja (rasio 2024 terhadap 2023) dan dari fakta bahwa t−1 baris 2025 sudah berada di rezim baru. Angka pada tabel pengukuran memakai data uji 2025 atas permintaan, sehingga di laporan disajikan sebagai konfirmasi, bukan dasar pemilihan. Keputusan lain tidak boleh diambil dari data uji (K-06).
*Ditolak:* penanda tahun ≥ 2024 di semua skenario (galat sepuluh kali lipat di skenario berbasis t−1); tanpa penanda di skenario berbasis t−1 (model tetap dapat mempelajari lonjakan 2024 lewat kombinasi `jalur` × `jenjang`); membuang baris SNBT vokasi sebelum 2024 (membuang data asli).
**Keterbatasan:** pertumbuhan vokasi SNBT 2024 → 2025 (1,3×) tidak dapat dipelajari dari tahun latih mana pun, karena hanya ada satu tahun dalam rezim baru sebelum tahun uji.

### K-20 · Fitur prodi sejenis
**Keputusan:** prodi sejenis adalah prodi dengan `prodi_normal` dan `jenjang` yang sama, pada jalur yang sama. Tiga fitur dihitung oleh `src/fitur_prodi_sejenis.py` saat `muat_data()` dipanggil, tidak ditulis ke panel:

| Fitur | Arti |
|---|---|
| `rata_peminat_prodi_sejenis_lag1` | Rata-rata peminat prodi sejenis di PTN lain pada t−1 |
| `jumlah_ptn_punya_prodi_sejenis_lag1` | Jumlah PTN lain yang punya prodi sejenis pada t−1 |
| `rasio_peminat_vs_sejenis_lag1` | `peminat_lag1` / `rata_peminat_prodi_sejenis_lag1` |

**Aturan:** (1) hanya tahun t−1, diambil lewat penggabungan pada nilai tahun (K-04); (2) seluruh prodi dari PTN yang sama dikecualikan, sehingga kampus utama dan PSDKU satu PTN tidak saling menjadi pembanding; (3) dihitung per jalur (K-03); (4) tanpa prodi sejenis di PTN lain → NaN, tidak diisi (K-05); rasio juga NaN bila rata-ratanya 0 (5 baris).
**Normalisasi nama:** 1.420 nama mentah dari 5.129 prodi non-fakultas diseragamkan menjadi 755 `prodi_normal` (737 pada baris bertarget) lewat pembersihan mekanis (isi kurung, penanda kampus, singkatan, salah ketik) dan 148 entri sinonim eksplisit di `_SINONIM`. Prinsip pemadanan: (a) prodi digabung hanya bila memang prodi yang sama, bukan karena tanpa penggabungan prodi itu tidak punya pembanding; (b) rekayasa tidak digabung ke ilmu murni. Karena itu `GEOLOGI` **tidak** digabung ke `TEKNIK GEOLOGI` (sedangkan `REKAYASA GEOLOGI` digabung), dan `TEKNOLOGI REKAYASA KIMIA` menjadi `TEKNIK KIMIA`, bukan `KIMIA`; (c) jenjang masuk ke kunci, sehingga nama D3/D4 yang berbeda (mis. `KONSTRUKSI GEDUNG` D3 dan `KONSTRUKSI BANGUNAN GEDUNG` D4) tidak perlu digabung. `TEKNOLOGI DAN MANAJEMEN PEMBENIHAN IKAN` digabung ke `TEKNOLOGI PEMBENIHAN IKAN`. `METALURGI` (1 prodi S1) tetap digabung ke `TEKNIK METALURGI`: di Indonesia metalurgi diselenggarakan sebagai prodi rekayasa, tidak ada padanan ilmu murninya seperti pada geologi.
**Alasan kunci + jenjang:** peminat antarjenjang berbeda jauh pada nama yang sama. Median peminat SNBP 2024 untuk Akuntansi: D3 85, D4 282, S1 747,5.
**Validasi:** `python src/fitur_prodi_sejenis.py --uji` membandingkan hasil dengan hitungan manual baris per baris; 2.000 dari 2.000 baris sampel cocok, termasuk 518 baris NaN. `_periksa_peta()` menolak sinonim berantai, nama lama di dua kelompok, dan nama baku ganda.
**Skenario:** fitur dipakai di `dengan_lag` (ketiganya) dan di skenario baru `tanpa_riwayat_sendiri` (rata-rata dan jumlah PTN, tanpa `peminat_lag1`, `daya_tampung_lag1`, dan rasio). `tanpa_lag` tidak memakainya karena ditujukan untuk prodi tanpa riwayat apa pun.
**Catatan `tanpa_riwayat_sendiri`:** skenario ini meniru kasus prodi baru yang punya padanan di PTN lain dengan menyembunyikan riwayat prodi itu sendiri. Baris ujinya sebagian besar prodi lama, karena prodi yang benar-benar baru belum punya target untuk dinilai.
**Catatan nilai:** `rasio_peminat_vs_sejenis_lag1` berkisar 0–420 (median 0,87). Nilai ekstrem berasal dari prodi sejenis yang peminatnya sangat kecil dan tidak dipangkas (K-11).

### K-21 · Keterbatasan: skenario `dengan_lag` bias ke prodi umum
**Keputusan:** baris `dengan_lag` yang tidak punya prodi sejenis di PTN lain pada t−1 dikeluarkan, tidak diisi. Penyusutan ini diterima dan **dilaporkan sebagai keterbatasan penelitian**.
**Besarnya:** 2.846 dari 32.861 baris (8,7%) keluar; latih 23.445 → 21.507 dan uji 9.416 → 8.508 baris (gabungan).
**Sifat biasnya:** baris yang keluar sistematis, bukan acak. Sebanyak 60% di antaranya prodi vokasi (D4 46%, D3 14%), dibandingkan 15% pada baris yang tersisa, dan median peminatnya lebih kecil (152 dibandingkan 208). Hasil `dengan_lag` karenanya mewakili prodi yang umum ditemui di banyak PTN, terutama S1, dan tidak boleh digeneralisasi ke prodi unik. Prodi unik tetap tercakup oleh skenario `tanpa_lag`.
*Ditolak:* mengisi fitur prodi sejenis yang kosong dengan rata-rata kelompok bidang atau nol (K-05); memperlonggar pemadanan nama agar prodi unik mendapat pembanding (K-20 prinsip a).

### K-22 · Hasil antarversi fondasi tidak dibandingkan
**Keputusan:** setiap baris `hasil/evaluasi.csv` mencatat `versi_fondasi`. Versi 2 (2026-11-12) menambahkan fitur prodi sejenis, skenario `tanpa_riwayat_sendiri`, penanda vokasi SNBT, dan perbaikan `is_psdku`. Baris tanpa `versi_fondasi` berasal dari versi 1 (Progress Report 1).
**Alasan:** baris uji dan fitur `dengan_lag` berubah, sehingga skor versi 1 dan versi 2 tidak setara. Setiap model wajib dijalankan ulang pada versi 2 sebelum dibandingkan.

### K-23 · Transformasi skala fitur di dalam pipeline model
**Keputusan:** `muat_data()` tetap mengembalikan fitur berskala asli untuk semua model. Transformasi skala fitur adalah bagian dari pipeline model, sama seperti `StandardScaler`. Untuk model linear bertarget log, `log_fitur()` dari `fondasi.py` menerapkan `log1p` pada fitur yang sangat menceng (skew > 1,5): `daya_tampung`, `daya_tampung_lag1`, `peminat_lag1`, `rata_peminat_prodi_sejenis_lag1`, dan `rasio_peminat_vs_sejenis_lag1`. Template memanggil `buat_model(target)` sehingga model dapat memilih praproses per target.
**Alasan:** target log yang dimodelkan linear terhadap fitur berskala asli tidak stabil; prediksinya meledak setelah `expm1`. Pasangan yang konsisten adalah log–log untuk target log dan asli–asli untuk target asli. Model pohon tidak memerlukan transformasi ini karena log tidak mengubah urutan nilai, sehingga data antarmodel tetap setara (K-15).
**Pengukuran** (Linear Regression, gabungan, uji 2025; tidak disimpan ke `evaluasi.csv`):

| Skenario | Target log, fitur asli | Target log, `log_fitur()` | Target asli, `log_fitur()` |
|---|---|---|---|
| `dengan_lag` | MAE 602,56; R² −1.640,99 | MAE 90,01; R² 0,7546 | MAE 197,78 (lebih buruk dari fitur asli: 84,02) |
| `tanpa_lag` | MAE 223,07; R² −1,5169 | MAE 204,78; R² 0,4239 | MAE 251,89 (fitur asli: 245,46) |
| `tanpa_riwayat_sendiri` | MAE 425,97; R² −476,63 | MAE 163,33; R² 0,5995 | MAE 225,83 (fitur asli: 209,32) |

Dua skenario terakhir dinilai dengan lipatan kelompok prodi (K-24).

Random Forest `dengan_lag` dengan dan tanpa `log_fitur()`: MAE 71,97 dan 71,98, praktis sama.
*Ditolak:* transformasi log di `muat_data()` untuk semua model (mengubah fitur model pohon tanpa manfaat dan memaksa target asli LR memakai fitur log yang memperburuk hasilnya); tanpa transformasi (target log LR tetap meledak).

### K-24 · Skenario prodi baru dinilai tanpa prodi uji di data latih
**Masalah:** pembagian berbasis waktu saja membuat sekitar 96% baris uji 2025 `tanpa_lag` dan `tanpa_riwayat_sendiri` berasal dari prodi yang sudah ada di data latih 2021–2024. Model dapat mengenali prodi itu lewat kombinasi fitur struktural dan "mengingat" peminatnya, padahal prodi yang benar-benar baru tidak pernah ada di data latih. Uji dengan 20% prodi yang disembunyikan (Random Forest, gabungan): MAE `tanpa_lag` 155,7 → 200,1 (+29%) dan `tanpa_riwayat_sendiri` 120,7 → 145,0 (+20%). `dengan_lag` tidak terpengaruh (76,0 → 73,6) dan tidak diubah.
**Keputusan:** pembagian waktu sekaligus kelompok. Satu kelompok adalah satu program di satu PTN: `id_ptn` + `prodi_normal` + `jenjang` (`kelompok_prodi()`), mencakup baris SNBP, SNBT, dan kampus PSDKU-nya. Kelompok dibagi acak tetapi tetap (`random_state=42`) ke 5 lipatan.
- **Penilaian:** `latih_dan_prediksi()` melatih 5 model; model lipatan k tidak melihat kelompok di lipatan k dan hanya memprediksi baris uji 2025 kelompok itu. Setiap baris uji diprediksi tepat satu kali, sehingga jumlah baris uji tidak berkurang.
- **Penyetelan:** `lipatan_waktu()` memecah setiap tahun validasi menjadi 5 lipatan kelompok untuk kedua skenario ini.
- **Baseline:** `baseline_rata_kelompok` di kedua skenario dihitung per lipatan yang sama. `baseline_rata_sejenis` tidak berubah karena tidak memakai data latih dan sudah mengecualikan PTN prodi itu sendiri (K-20).
**Validasi:** pada 9 kombinasi skenario × jalur, setiap baris uji diprediksi tepat sekali, tidak ada kelompok yang sama di data latih dan uji suatu lipatan, lipatan waktu tidak melatih tahun setelah tahun validasinya, dan pembagiannya identik bila diulang.
**Konsekuensi:** waktu latih dua skenario ini sekitar lima kali lipat. Model akhir untuk aplikasi tetap dilatih pada seluruh data latih; lipatan kelompok hanya untuk penilaian dan penyetelan.
*Ditolak:* pembagian waktu saja (skor terlalu optimistis 20–29%); menyisihkan satu kelompok 20% tetap (baris uji berkurang menjadi seperlima).

### K-25 · Rentang prediksi prodi baru: persentil antarpohon
**Keputusan:** Untuk Random Forest bertarget log, setiap pohon memberi satu prediksi pada skala log; prediksi tiap pohon dikembalikan ke skala orang dengan `dari_log()` lebih dulu, baru persentil ke-10 dan ke-90 dihitung. Titik prediksi tetap prediksi model biasa (`dari_log` dari rata-rata log seluruh pohon). Rentang ini disebut **rentang empiris antarpohon**, bukan confidence interval atau prediction interval. Skenario: `tanpa_riwayat_sendiri` bila prodi punya prodi sejenis di PTN lain pada tahun sebelumnya, `tanpa_lag` bila tidak (K-20).
**Validasi:** cakupan (persen nilai aktual di dalam rentang) diukur pada validasi 2024 lewat `lipatan_waktu()`, sehingga prodi yang divalidasi tidak ikut dilatih (K-24). Data uji 2025 tidak dipakai dan rentang tidak dikalibrasi ulang.
**Hasil (fondasi versi 2):** cakupan 72,6% (`tanpa_riwayat_sendiri`, n = 8.487) dan 57,0% (`tanpa_lag`, n = 9.442), di bawah 80% nominal. Rentang cenderung terlalu sempit karena pohon dilatih pada data yang sama; ia hanya menunjukkan sebaran prediksi antarpohon.
**Keterbatasan:** satu tahun validasi, dan lonjakan vokasi SNBT 2024 (K-19) dapat memengaruhi hasil. Masukan prodi baru kustom belum ada; menunggu fungsi masukan yang melewati transformasi fondasi yang sama dengan data latih.
*Ditolak:* menyebut rentang ini confidence interval formal; kalibrasi lebar rentang memakai data uji 2025.

---

## Hal yang masih terbuka

Belum ada. Temuan yang belum menjadi keputusan dicatat di sini dan tidak boleh dikutip sebagai keputusan sebelum dipindahkan ke bagian di atas.

---

## Rujukan

- UNESCO Institute for Statistics (2014). *ISCED Fields of Education and Training 2013 (ISCED-F 2013).*
- Undang-Undang Republik Indonesia Nomor 12 Tahun 2012 tentang Pendidikan Tinggi, Pasal 10.
- Yalaoui, M., & Boukhedouma, S. (2026). A structured machine learning based framework for multidimensional data quality assessment. *Journal of Big Data* (in press). https://doi.org/10.1186/s40537-026-01520-7. Dirujuk untuk tahap validasi pasca-prapemrosesan (§3.3); praktik imputasi dan pembagian acaknya **tidak** diadopsi.
