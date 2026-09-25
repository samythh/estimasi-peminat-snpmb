# CLAUDE.md

Panduan untuk Claude Code. Detail lengkap ada di `docs/`; berkas ini memuat hal yang wajib diketahui sebelum menyentuh kode atau data.

## Penelitian

**Judul (disetujui dosen):** *Estimasi Jumlah Peminat Program Studi Menggunakan Regresi pada Data SNPMB sebagai Dasar Pembentukan Angka Pembanding Antar Perguruan Tinggi*

- **Tugas:** regresi. Target `peminat` = jumlah pendaftar per prodi × jalur × tahun.
- **Cakupan:** seluruh PTN peserta SNPMB. Universitas Andalas hanya contoh ilustrasi, **bukan** studi kasus.
- **Model:** Linear Regression, Random Forest, XGBoost, masing-masing dilatih satu anggota tim di atas fondasi bersama. Claude membangun fondasi dan baseline, bukan ketiga model itu.

## Dokumen rujukan

| Berkas | Baca ketika |
|---|---|
| `docs/STANDAR_PENGERJAAN.md` | Sebelum mengubah apa pun |
| `docs/KAMUS_DATA.md` | Memilih fitur; kolom *Status fitur* menentukan yang boleh dan dilarang |
| `docs/KEPUTUSAN_METODOLOGI.md` | Sebelum mengubah keputusan metodologis; bagian *Hal yang masih terbuka* (T-01…T-05) harus diselesaikan saat membuat `fondasi.py` |
| `docs/CHANGELOG.md` | Setiap perubahan data, kolom, kode, atau jalur **wajib** dicatat di sini |

## Struktur

```
src/             ambil_data_snpmb.py, fitur_kelompok_bidang.py   (fondasi.py direncanakan)
analisis/        analisis & grafik contoh Unand
notebooks/       00_baseline.ipynb, template_model.ipynb          (direncanakan)
data/mentah/     mentah_snbp.json, mentah_snbt.json   — JANGAN DIUBAH
data/olahan/     snpmb_panel.csv (43.449 baris, 24 kolom), peminat_provinsi_snbt.csv
data/contoh_unand/
hasil/grafik/    (hasil/evaluasi.csv direncanakan)
```

Jalur di kode selalu relatif terhadap akar proyek: `AKAR = Path(__file__).resolve().parents[1]`.

## Menjalankan

```bash
python src/ambil_data_snpmb.py                       # bangun panel dari mentah (tanpa jaringan)
python src/ambil_data_snpmb.py --paksa-unduh semua   # unduh ulang ±10 menit
python src/fitur_kelompok_bidang.py                  # mode tinjau pemetaan bidang
python analisis/analisa_tren_unand.py SNBT
```

`ambil_data_snpmb.py` memanggil `fitur_kelompok_bidang.bangun()`, jadi `kelompok_bidang` dan `is_fakultas` selalu ikut terbangun.

## Lingkungan

Windows 11, Python 3.13. Terpasang: `requests`, `pandas` 3.0.5, `numpy`, `matplotlib`. **Belum terpasang:** `scikit-learn`, `xgboost`, `notebook` (lihat `requirements.txt`). Konsol memerlukan `sys.stdout.reconfigure(encoding="utf-8")`; CSV ditulis `utf-8-sig`.

## Aturan yang tidak boleh dilanggar

1. **Tanpa kebocoran data:** `terima`, keketatan tahun berjalan, `total_peminat_ptn` tahun berjalan, `proporsi_peminat_lokal`, `jumlah_provinsi_asal`, dan `terima_lag1` tidak boleh jadi fitur.
2. **Peminat SNBP dan SNBT tidak pernah dijumlahkan.** Agregat dan lag dihitung per `(id_prodi, jalur)`.
3. **Lag lewat self-merge pada nilai tahun**, bukan `shift()`. Tahun yang tidak ada → NaN.
4. **Tanpa imputasi, isian nol, rata-rata, atau data sintetis.**
5. **Data mentah disimpan sebelum diolah dan tidak diubah.**
6. **Pembagian temporal:** latih 2021–2024, uji 2025.
7. **`random_state=42`.**
8. **Tahap yang mengubah data tetap harus lewat mode tinjau dan menunggu konfirmasi pengguna** bila diminta demikian.
9. **Jangan klaim melebihi data.** `kelompok_bidang` adalah pengelompokan buatan tim, diadaptasi dari ISCED-F 2013. Sebut "pengelompokan berbasis aturan", bukan "klasifikasi".

## Jebakan yang sudah diketahui

- `daya_tampung_kini` berisi nilai **2026** di semua baris 2021–2025; jangan dipakai sebagai fitur baris historis tanpa keputusan T-01.
- `is_new` selalu 0 pada baris bertarget; tidak berguna sebagai fitur.
- `terima` kosong 100% di SNBT.
- API mengembalikan `200 OK` berisi `[]` untuk `id_ptn` yang salah; kegagalannya senyap.
- 21 entri fakultas ITB (`is_fakultas = 1`) dikeluarkan dari pemodelan.
- Pencocokan kata kunci harus di **awal kata**; substring polos terbukti salah (`IKAN` di *PENDIDIKAN*/*PERBAIKAN*).
