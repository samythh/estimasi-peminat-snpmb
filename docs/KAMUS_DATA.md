# Kamus Data

## Sumber

API publik SNPMB, format JSON, tanpa login. Diakses September 2026.

| | SNBP | SNBT |
|---|---|---|
| Daftar PTN | `https://snpmb.id/proxy-ptn-sn.php` | `https://snpmb.id/proxy-ptn-sb.php` |
| Prodi per PTN | `https://snpmb.id/proxy-prodi-sn.php?ptn={id_ptn}` | `https://snpmb.id/proxy-prodi-sb.php?ptn={id_ptn}` |
| Referer | `https://snpmb.id/snbp/daya-tampung-snbp` | `https://snpmb.id/utbk-snbt/daya-tampung-snbt` |
| Jumlah PTN | 146 | 145 (tanpa Universitas Terbuka) |

**Perhatian:** `{id_ptn}` yang salah atau tidak diganti tetap mengembalikan `200 OK` berisi `[]`. Kegagalannya senyap, jadi periksa panjang respons.

---

## `data/olahan/snpmb_panel.csv`

Satu baris = **satu prodi × satu tahun × satu jalur**. 43.449 baris, 24 kolom.

Prodi tanpa riwayat (`is_new == 1`) mendapat satu baris dengan `tahun` dan metrik historis kosong. Baris ini tidak punya target, sehingga otomatis tidak ikut pemodelan.

### Status fitur

| Status | Arti |
|---|---|
| **Target** | Yang diprediksi |
| **Fitur** | Boleh dipakai sebagai prediktor |
| **Dilarang** | Kebocoran data atau tidak setara antar jalur. Tidak boleh jadi fitur |
| **Identitas** | Pengenal baris. Bukan fitur |
| **Penyaring** | Dipakai untuk memilih baris, bukan fitur |
| **Tinjau** | Keputusannya belum final (lihat [KEPUTUSAN_METODOLOGI.md](KEPUTUSAN_METODOLOGI.md#hal-yang-masih-terbuka)) |

### Kolom

| Kolom | Tipe | Arti | Status |
|---|---|---|---|
| `id_ptn` | int | Kode PTN dari API | Identitas |
| `ptn_nama` | teks | Nama PTN | Identitas |
| `jalur` | teks | `SNBP` atau `SNBT` | Fitur |
| `id_prodi` | int | Kode prodi dari API; sama di kedua jalur | Identitas |
| `kode_prodi` | int | Kode prodi 8 digit | Identitas |
| `prodi` | teks | Nama prodi seperti tertulis di sumber | Identitas |
| `jenjang` | teks | S1, D3, D4, dst. | Fitur |
| `portofolio` | teks | Jenis portofolio yang disyaratkan (`Tidak Ada` bila tidak ada) | Fitur |
| `kelompok_bidang` | teks | Pengelompokan bidang buatan tim, diadaptasi dari ISCED-F 2013. 10 nilai: kesehatan, teknik, sains, pertanian, ekonomi, sosial_humaniora, pendidikan, seni, pariwisata, olahraga | Fitur |
| `is_fakultas` | 0/1 | 1 bila entri adalah fakultas/sekolah ITB, bukan prodi (21 entri) | Penyaring: dikeluarkan dari pemodelan |
| `is_new` | 0/1 | 1 bila prodi baru tanpa riwayat | Tinjau: selalu 0 pada baris bertarget |
| `daya_tampung_kini` | int | Daya tampung **tahun pendaftaran berjalan (2026)**. Sama untuk semua tahun dalam satu prodi-jalur | Tinjau: berisi nilai 2026 di baris 2021–2025 |
| `tahun` | int | Tahun seleksi (2021–2025) | Identitas, dan dasar pembagian latih/uji |
| `daya_tampung` | int | Daya tampung **tahun baris itu**, diumumkan sebelum pendaftaran | Tinjau: kandidat pengganti `daya_tampung_kini` |
| `peminat` | int | Jumlah pendaftar prodi pada jalur dan tahun itu | **Target** |
| `terima` | int | Jumlah diterima. **Kosong 100% di SNBT** | **Dilarang**: baru diketahui setelah seleksi |
| `peminat_lag1` | int | `peminat` tahun−1, prodi & jalur yang sama | Fitur |
| `peminat_lag2` | int | `peminat` tahun−2 | Fitur opsional; tidak dipakai secara bawaan karena banyak kosong |
| `daya_tampung_lag1` | int | `daya_tampung` tahun−1 | Fitur |
| `terima_lag1` | int | `terima` tahun−1 | **Dilarang**: kosong 100% di SNBT sehingga tidak setara antar jalur |
| `jumlah_prodi_ptn` | int | Jumlah prodi PTN itu pada jalur & tahun yang sama | Fitur |
| `total_peminat_ptn` | int | Jumlah peminat seluruh prodi PTN pada jalur & tahun yang sama | **Dilarang**: memuat target baris itu sendiri. Versi lag boleh dibuat |
| `proporsi_peminat_lokal` | float | Porsi peminat dari provinsi kedudukan PTN. Hanya SNBT | **Dilarang**: hasil pendaftaran tahun berjalan, dan tidak ada di SNBP |
| `jumlah_provinsi_asal` | int | Jumlah provinsi asal peminat. Hanya SNBT | **Dilarang**: alasan sama |

Kolom PTN yang direncanakan untuk fitur struktural di `fondasi.py` (belum ada di panel, diambil dari daftar PTN mentah): `is_ptnbh`, `is_akademik`, `is_vokasi`, `is_ptkin`, `provinsi`.

---

## `data/olahan/peminat_provinsi_snbt.csv`

Satu baris = **prodi × tahun × provinsi asal pendaftar**, khusus SNBT. 261.558 baris.

| Kolom | Arti |
|---|---|
| `id_ptn`, `ptn_nama`, `id_prodi`, `prodi`, `jenjang` | Identitas |
| `tahun` | Tahun seleksi |
| `kode_prov`, `nama_prov` | Provinsi asal pendaftar. Skema kodenya berbeda dari kode provinsi di daftar PTN |
| `jml_peminat` | Jumlah pendaftar dari provinsi tersebut |

---

## `data/mentah/`

| Berkas | Isi |
|---|---|
| `mentah_snbp.json` | `{jalur, diambil_pada, sumber, id_ptn_unand, ptn: [...], prodi_per_ptn: {id_ptn: [...]}, ptn_gagal: [...]}` |
| `mentah_snbt.json` | Struktur sama, ditambah field `history_peminat_provinsi` pada setiap prodi |

Field penting di setiap prodi: `daya_tampung_snbp` / `daya_tampung_snbt` (bertipe **string**), `is_new`, dan `history_daya_tampung` (array berisi `tahun`, `daya_tampung`, `peminat`, `terima`). Panjang riwayatnya bervariasi: 0–5 tahun.
