# Dashboard Streamlit — versi awal

Versi ini menyediakan Beranda, Cari Jurusan, Bandingkan Jurusan, Hasil Pengujian, dan Panduan. Perkiraan Peminat menampilkan keterangan bahwa perhitungan baru belum tersedia. Angka eksplorasi dan evaluasi berasal dari data kelompok, bukan contoh buatan.

## Menjalankan

Gunakan Python 3.13 dari akar repo:

```powershell
python -m pip install -r dashboard/requirements.txt
python -m streamlit run dashboard/streamlit_app.py
```

Jika panel belum tersedia, aplikasi menjalankan `src/ambil_data_snpmb.py` dengan snapshot mentah repo. Tidak ada unduhan ulang atau pelatihan model saat startup. Panel hasil tetap berada di `data/olahan/` dan tidak di-commit.

## Deployment awal

Pada Streamlit Community Cloud pilih Create app dan gunakan:

- Repository: `samythh/estimasi-peminat-snpmb`
- Branch: `dashboard-streamlit-duha`
- Main file path: `dashboard/streamlit_app.py`
- Advanced settings → Python: `3.13`
- Secrets: tidak diperlukan.

Dependensi aplikasi berada di `dashboard/requirements.txt`, di sebelah entry point, sehingga deployment tidak memasang paket pelatihan notebook yang tidak digunakan aplikasi. Tema berada di `.streamlit/config.toml`.

Status dokumen ini: paket siap diuji deploy; keberhasilan publikasi perlu dikonfirmasi dari URL aplikasi dan log build. Setelah deployment berhasil, push perubahan ke branch yang sama akan memperbarui aplikasi yang terhubung.

## Pemeriksaan

- AppTest berhasil membuka keenam menu melalui tombol sidebar.
- Startup dari salinan bersih berhasil membangun panel melalui skrip resmi.
- Tampilan desktop diperiksa; bukti `docs/dashboard/beranda.png`.
- Data fakultas dan target kosong dikeluarkan dari tampilan; SNBP dan SNBT terpisah.
- Tahun tanpa observasi tidak diisi; rasio untuk kuota nol/kosong dibiarkan kosong.
- Hasil XGBoost yang belum mengalahkan patokan tahun lalu tetap ditampilkan.

## Batas versi awal

Prediksi baru, model anggota lain, serta rentang prediksi belum diintegrasikan. Uji perangkat seluler dan build Linux cloud masih perlu verifikasi pada deployment. Aplikasi bukan situs resmi SNPMB dan tidak menghitung peluang lolos pribadi.
