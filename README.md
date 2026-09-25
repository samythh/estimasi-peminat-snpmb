# Estimasi Jumlah Peminat Program Studi — Data SNPMB

**Judul penelitian:** *Estimasi Jumlah Peminat Program Studi Menggunakan Regresi pada Data SNPMB sebagai Dasar Pembentukan Angka Pembanding Antar Perguruan Tinggi*

Proyek ini memprediksi jumlah pendaftar (`peminat`) setiap program studi di seluruh PTN peserta SNPMB, jalur SNBP dan SNBT, tahun 2021–2025. Tiga model regresi (Linear Regression, Random Forest, XGBoost) dilatih di atas fondasi data dan evaluasi yang sama, sehingga hasilnya dapat dibandingkan.

## Mulai cepat

```bash
python -m pip install -r requirements.txt

python src/ambil_data_snpmb.py            # bangun panel dari data mentah yang sudah ada
python src/fitur_kelompok_bidang.py       # tinjau pemetaan kelompok bidang
```

Pengambilan ulang dari API (±10 menit, jeda 1 detik per permintaan):

```bash
python src/ambil_data_snpmb.py --paksa-unduh semua
```

## Struktur

```
.
├── src/                 kode inti: pengambilan data, fitur, fondasi pemodelan
├── analisis/            analisis deskriptif & grafik (contoh Unand)
├── notebooks/           baseline dan template model untuk anggota tim
├── data/
│   ├── mentah/          respons API asli — JANGAN DIUBAH
│   ├── olahan/          panel siap pakai
│   └── contoh_unand/    subset & ringkasan contoh Universitas Andalas
├── hasil/
│   └── grafik/          grafik PNG 300 dpi + CSV nilai pendamping
└── docs/                dokumentasi proyek
```

## Dokumentasi

| Dokumen | Isi |
|---|---|
| [docs/STANDAR_PENGERJAAN.md](docs/STANDAR_PENGERJAAN.md) | Aturan kerja tim — **baca sebelum mulai** |
| [docs/KAMUS_DATA.md](docs/KAMUS_DATA.md) | Arti setiap kolom dan boleh-tidaknya dipakai sebagai fitur |
| [docs/KEPUTUSAN_METODOLOGI.md](docs/KEPUTUSAN_METODOLOGI.md) | Keputusan metodologis beserta alasannya, siap dikutip di laporan |
| [docs/CHANGELOG.md](docs/CHANGELOG.md) | Riwayat perubahan proyek |
| [CLAUDE.md](CLAUDE.md) | Panduan untuk Claude Code |

## Sumber data

API publik SNPMB (`snpmb.id`), diakses September 2026. Rincian endpoint di [docs/KAMUS_DATA.md](docs/KAMUS_DATA.md#sumber).
