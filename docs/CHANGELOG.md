# Riwayat Perubahan

Semua perubahan penting pada data, fitur, dan kode dicatat di sini, terbaru di atas. Setiap entri menyebut **apa** yang berubah dan **dampaknya** bagi anggota tim.

Format: `[versi] — tanggal`, lalu kelompok *Ditambahkan*, *Diubah*, *Diperbaiki*, *Dihapus*.

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
