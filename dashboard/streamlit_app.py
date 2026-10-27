"""Antarmuka publik SNPMB; data dibangun oleh skrip resmi kelompok."""
from __future__ import annotations

from pathlib import Path
import subprocess
import sys

import altair as alt
import pandas as pd
import streamlit as st

AKAR = Path(__file__).resolve().parents[1]
PANEL = AKAR / "data/olahan/snpmb_panel.csv"
MENU: dict[str, str] = {
    "Beranda": ":material/home:",
    "Cari Jurusan": ":material/search:",
    "Bandingkan Jurusan": ":material/compare_arrows:",
    "Perkiraan Peminat": ":material/insights:",
    "Hasil Pengujian": ":material/verified:",
    "Panduan": ":material/help_outline:",
}
WARNA = ["#2563eb", "#0d9488", "#ea580c", "#9333ea", "#be185d"]


@st.cache_resource(show_spinner="Menyiapkan data kampus. Tunggu sebentar…")
def siapkan_panel() -> Path:
    if PANEL.exists():
        return PANEL
    # Cloud tidak membawa data/olahan yang diabaikan Git. Pakai snapshot dan
    # skrip resmi, sehingga tidak ada pengolahan alternatif atau unduhan ulang.
    for nama in ("mentah_snbp.json", "mentah_snbt.json"):
        if not (AKAR / "data/mentah" / nama).is_file():
            raise FileNotFoundError(f"Snapshot {nama} tidak tersedia. Pulihkan data/mentah dari repo tim.")
    proses = subprocess.run(
        [sys.executable, "-X", "utf8", str(AKAR / "src/ambil_data_snpmb.py")],
        cwd=AKAR, capture_output=True, text=True, encoding="utf-8", timeout=180,
        check=False,
    )
    if proses.returncode != 0 or not PANEL.is_file():
        raise RuntimeError(f"Skrip data gagal (kode {proses.returncode}). {proses.stderr[-2500:]}")
    return PANEL


@st.cache_data(show_spinner=False)
def baca_data(lokasi: Path, revisi: int) -> pd.DataFrame:
    data = pd.read_csv(lokasi)
    wajib = {"id_prodi", "id_ptn", "ptn_nama", "prodi", "jenjang", "jalur", "tahun", "peminat", "daya_tampung", "is_fakultas"}
    hilang = wajib.difference(data.columns)
    if hilang:
        raise ValueError(f"Kolom wajib tidak ada: {', '.join(sorted(hilang))}. Bangun ulang panel resmi.")
    data = data[data.is_fakultas.eq(0)].dropna(subset=["tahun", "peminat"]).copy()
    if data.empty:
        raise ValueError("Panel tidak memiliki riwayat peminat program studi yang dapat ditampilkan.")
    data["tahun"] = data.tahun.astype(int)
    data["label"] = data.prodi.str.title() + " · " + data.jenjang + " — " + data.ptn_nama.str.title()
    if data.duplicated(["id_prodi", "jalur", "tahun"]).any():
        raise ValueError("Ada baris prodi/jalur/tahun ganda. Periksa fondasi data bersama.")
    return data


def angka(nilai: float | int) -> str:
    return f"{nilai:,.0f}".replace(",", ".")


def pindah(halaman: str) -> None:
    st.session_state["halaman"] = halaman


def tombol(label: str, tujuan: str, kunci: str) -> None:
    st.button(label, key=kunci, on_click=pindah, args=(tujuan,), icon=":material/arrow_forward:", width="stretch")


def sidebar() -> str:
    aktif = str(st.session_state.get("halaman", "Beranda"))
    with st.sidebar:
        st.html('<div class="brand"><div class="brand-icon">S</div><div><b>SNPMB Insight</b><small>Kenali pilihan kuliahmu</small></div></div>')
        st.caption("JELAJAHI PILIHANMU")
        for nama in list(MENU)[:4]:
            st.button(nama, icon=MENU[nama], type="primary" if aktif == nama else "tertiary", width="stretch", key=f"menu_{nama}", on_click=pindah, args=(nama,))
        st.divider()
        st.caption("PAHAMI DATANYA")
        for nama in list(MENU)[4:]:
            st.button(nama, icon=MENU[nama], type="primary" if aktif == nama else "tertiary", width="stretch", key=f"menu_{nama}", on_click=pindah, args=(nama,))
        st.html('<div class="sidebar-note"><b>Mulai dari rasa ingin tahu.</b><p>Cari kampus dan jurusan, lalu lihat bagaimana jumlah peminatnya berubah.</p><span>DATA 2021–2025</span></div>')
        st.caption("Proyek mahasiswa · Bukan situs resmi SNPMB")
    return aktif


def pilih_jalur(kunci: str) -> str:
    return str(st.radio("Jalur masuk", ["SNBP", "SNBT"], horizontal=True, key=kunci, help="SNBP: seleksi berdasarkan prestasi. SNBT: seleksi berdasarkan tes. Data kedua jalur ditampilkan terpisah."))


def beranda(data: pd.DataFrame) -> None:
    st.html('<div class="hero"><span class="eyebrow">LANGKAH AWAL MEMILIH KULIAH</span><h1>Kenali jurusan.<br>Pahami peminatnya.</h1><p>Lihat riwayat peminat dan daya tampung kampus pilihanmu.<br>Mulai dengan mencari jurusan, lalu bandingkan pilihanmu.</p><span class="hero-chip">SNBP & SNBT</span><span class="hero-chip">Data 2021–2025</span></div>')
    a, b, _ = st.columns([1.15, 1.15, 2])
    with a: tombol("Cari jurusan", "Cari Jurusan", "hero_cari")
    with b: tombol("Bandingkan pilihan", "Bandingkan Jurusan", "hero_banding")
    st.write("")
    kiri, kanan = st.columns([3, 1])
    with kiri:
        st.subheader("Sekilas data kampus")
        st.caption("Angka berikut mengikuti jalur dan tahun yang kamu pilih.")
    with kanan:
        tahun = st.selectbox("Tahun data", sorted(data.tahun.unique()), index=len(data.tahun.unique()) - 1)
    jalur = pilih_jalur("jalur_beranda")
    tahun_data = data[data.jalur.eq(jalur) & data.tahun.eq(tahun)]
    if tahun_data.empty:
        st.info("Belum ada data untuk tahun dan jalur ini. Coba pilihan lain.")
        return
    kolom = st.columns(3)
    for col, label, nilai, bantuan in zip(kolom, ["Kampus dalam data", "Jurusan yang tercatat", "Rata-rata peminat per jurusan"], [tahun_data.id_ptn.nunique(), tahun_data.id_prodi.nunique(), tahun_data.peminat.mean()], ["Perguruan tinggi dengan riwayat peminat tersedia.", "Program studi dengan riwayat peminat tersedia.", "Rata-rata antarjurusan, bukan jumlah pendaftar unik. Jurusan populer dapat menaikkan angka ini."]):
        col.metric(label, angka(nilai), help=bantuan)
    st.write("")
    a, b = st.columns([1.65, 1])
    with a, st.container(border=True):
        st.subheader("Bagaimana peminat berubah?")
        st.caption(f"Rata-rata peminat per jurusan melalui {jalur}")
        tren = data[data.jalur.eq(jalur)].groupby("tahun", as_index=False).peminat.mean()
        grafik = alt.Chart(tren).mark_area(color="#dceafe", line={"color": "#2563eb", "strokeWidth": 3}, point={"color": "#2563eb", "size": 55}).encode(
            x=alt.X("tahun:O", title=None, axis=alt.Axis(labelAngle=0)),
            y=alt.Y("peminat:Q", title="Peminat (orang)", scale=alt.Scale(zero=True)),
            tooltip=[alt.Tooltip("tahun:O", title="Tahun"), alt.Tooltip("peminat:Q", title="Rata-rata peminat", format=",.0f")],
        ).properties(height=230)
        st.altair_chart(grafik, width="stretch")
        st.caption("Jumlah jurusan yang tersedia dapat berbeda setiap tahun. Grafik ini bukan prediksi tahun berikutnya.")
    with b, st.container(border=True):
        st.subheader("Baca data dalam 3 langkah")
        st.markdown("**01 · Pilih jalur masuk**  \nLihat SNBP atau SNBT secara terpisah.\n\n**02 · Temukan jurusan**  \nPilih kampus dan jurusan yang ingin kamu kenali.\n\n**03 · Bandingkan riwayatnya**  \nPerhatikan perubahan peminat dan jumlah kursi.")
        tombol("Pelajari cara membaca data", "Panduan", "bantuan_beranda")
    st.caption("Banyak peminat tidak berarti peluang lolosmu dapat dihitung dari angka ini. Gunakan data sebagai bahan pertimbangan, bukan kepastian diterima.")


def tampilkan_pilihan(terpilih: pd.DataFrame, jalur: str) -> None:
    if terpilih.empty:
        st.info("Belum ada data yang bisa ditampilkan. Pilih minimal satu jurusan atau perluas rentang tahun.", icon=":material/search:")
        return
    data = terpilih.sort_values(["label", "tahun"]).copy()
    data["segmen"] = data.groupby("id_prodi").tahun.transform(lambda x: x.diff().ne(1).cumsum()).astype(str)
    label = sorted(data.label.unique().tolist())
    st.subheader("Riwayat peminat")
    st.caption(f"{jalur} · Setiap titik adalah jumlah peminat pada satu tahun.")
    grafik = alt.Chart(data).mark_line(point=True, strokeWidth=3).encode(
        x=alt.X("tahun:O", title="Tahun", axis=alt.Axis(labelAngle=0)),
        y=alt.Y("peminat:Q", title="Peminat (orang)", scale=alt.Scale(zero=True)),
        color=alt.Color("label:N", title=None, scale=alt.Scale(domain=label, range=WARNA[:len(label)]), legend=alt.Legend(orient="bottom", labelLimit=650)),
        detail=["id_prodi:N", "segmen:N"],
        tooltip=[alt.Tooltip("prodi:N", title="Jurusan"), alt.Tooltip("ptn_nama:N", title="Kampus"), alt.Tooltip("tahun:O", title="Tahun"), alt.Tooltip("peminat:Q", title="Peminat", format=",.0f")],
    ).properties(height=310)
    st.altair_chart(grafik, width="stretch")
    st.caption("Garis terputus berarti riwayat tahun tersebut tidak tersedia; bukan berarti peminatnya nol.")
    st.subheader("Angka lengkapnya")
    data["peminat_per_kursi"] = data.peminat.div(data.daya_tampung.where(data.daya_tampung.gt(0))).round(1)
    tabel = data[["ptn_nama", "prodi", "jenjang", "jalur", "tahun", "peminat", "daya_tampung", "peminat_per_kursi"]].rename(columns={"ptn_nama": "Kampus", "prodi": "Jurusan", "jenjang": "Jenjang", "jalur": "Jalur", "tahun": "Tahun", "peminat": "Peminat (orang)", "daya_tampung": "Kursi tersedia", "peminat_per_kursi": "Peminat per kursi"})
    st.dataframe(tabel, hide_index=True, width="stretch")
    st.caption("Peminat per kursi = jumlah peminat ÷ kursi tersedia. Ini bukan peluang lolos. Nilai kosong berarti kuota tidak tersedia atau bernilai nol.")
    st.download_button("Simpan tabel ke CSV", tabel.to_csv(index=False).encode("utf-8-sig"), file_name=f"pilihan_jurusan_{jalur.lower()}.csv", mime="text/csv", icon=":material/download:")


def jelajah(data: pd.DataFrame, bandingkan: bool) -> None:
    st.title("Bandingkan pilihanmu" if bandingkan else "Temukan jurusan pilihanmu")
    st.write("Lihat riwayat beberapa jurusan dari kampus berbeda, pada jalur masuk yang sama." if bandingkan else "Pilih kampus, lalu lihat perubahan peminat jurusan yang kamu minati.")
    jalur = pilih_jalur("jalur_jelajah")
    dasar = data[data.jalur.eq(jalur)]
    kampus = sorted(dasar.ptn_nama.unique().tolist())
    with st.container(border=True):
        a, b = st.columns([2, 1])
        with a:
            if bandingkan:
                pilihan_ptn = st.multiselect("1. Pilih kampus (maksimal 3)", kampus, default=kampus[:2], max_selections=3, format_func=str.title)
            else:
                pilihan_ptn = [st.selectbox("1. Pilih kampus", kampus, format_func=str.title)]
        with b:
            rentang = st.slider("2. Pilih tahun", int(data.tahun.min()), int(data.tahun.max()), (int(data.tahun.min()), int(data.tahun.max())))
        kandidat = dasar[dasar.ptn_nama.isin(pilihan_ptn)]
        katalog = kandidat.drop_duplicates("id_prodi").sort_values("label")
        nama: dict[int, str] = dict(zip(katalog.id_prodi.astype(int), katalog.label))
        pilihan = st.multiselect("3. Pilih jurusan (maksimal 5)", list(nama), default=list(nama)[:2], max_selections=5, format_func=lambda kode: nama[kode], key=f"pilih_{bandingkan}_{jalur}_{'|'.join(pilihan_ptn)}", help="Ketik nama jurusan untuk mempercepat pencarian.")
    terpilih = kandidat[kandidat.id_prodi.isin(pilihan) & kandidat.tahun.between(*rentang)]
    tampilkan_pilihan(terpilih, jalur)


def perkiraan() -> None:
    st.title("Perkiraan peminat")
    st.write("Nantinya, kamu dapat melihat perkiraan jumlah peminat berdasarkan karakteristik jurusan.")
    with st.container(border=True):
        st.subheader("Fitur ini sedang disiapkan", icon=":material/construction:")
        st.write("Model penelitian belum dihubungkan ke halaman ini. Karena itu, aplikasi belum bisa menghitung perkiraan baru.")
        st.write("Sambil menunggu, kamu bisa melihat jumlah peminat yang benar-benar tercatat atau membandingkan beberapa jurusan.")
        a, b = st.columns(2)
        with a: tombol("Lihat riwayat peminat", "Cari Jurusan", "perkiraan_cari")
        with b: tombol("Lihat hasil pengujian", "Hasil Pengujian", "perkiraan_uji")
    st.caption("Perkiraan jumlah peminat nantinya tetap bukan jaminan hasil seleksi atau peluang kelulusan seseorang.")


def pengujian() -> None:
    st.title("Seberapa dekat perkiraan dengan kenyataan?")
    st.write("Kami membandingkan hasil perhitungan dengan jumlah peminat yang tercatat pada 2025.")
    lokasi = AKAR / "hasil/evaluasi.csv"
    if not lokasi.exists():
        st.info("Hasil pengujian belum tersedia. Pengelola perlu menambahkan hasil/evaluasi.csv dari evaluasi kelompok.")
        return
    evaluasi = pd.read_csv(lokasi)
    mode = st.radio("Informasi yang digunakan", ["Memakai riwayat tahun sebelumnya", "Tanpa riwayat tahun sebelumnya"], horizontal=True)
    skenario = "dengan_lag" if mode.startswith("Memakai") else "tanpa_lag"
    hasil = evaluasi[evaluasi.skenario.eq(skenario) & evaluasi.jalur.eq("gabungan")].copy()
    if hasil.empty:
        st.info("Hasil untuk pilihan ini belum tersedia.")
        return
    model = {"baseline_lag1": "Patokan: peminat tahun lalu", "baseline_rata_kelompok": "Patokan: rata-rata bidang ilmu", "xgboost": "XGBoost"}
    hasil["Metode"] = hasil.nama_model.map(model).fillna(hasil.nama_model)
    hasil["Metode"] += hasil.apply(lambda r: (" · data asli" if r.target == "asli" else " · data diubah ke skala log") if r.nama_model == "xgboost" else "", axis=1)
    st.info("Lihat besar selisihnya: makin kecil angkanya, makin dekat perkiraan dengan data nyata. Contoh: selisih rata-rata 100 berarti perkiraan meleset sekitar 100 orang per jurusan.", icon=":material/lightbulb:")
    st.altair_chart(alt.Chart(hasil).mark_bar(color="#2563eb", cornerRadiusEnd=5).encode(x=alt.X("MAE:Q", title="Selisih rata-rata (orang)", scale=alt.Scale(zero=True)), y=alt.Y("Metode:N", title=None, sort="x"), tooltip=["Metode", alt.Tooltip("MAE:Q", title="Selisih rata-rata", format=".2f")]).properties(height=240), width="stretch")
    if skenario == "dengan_lag" and {"xgboost", "baseline_lag1"}.issubset(set(hasil.nama_model)):
        xgb = float(hasil.loc[hasil.nama_model.eq("xgboost"), "MAE"].min())
        patokan = float(hasil.loc[hasil.nama_model.eq("baseline_lag1"), "MAE"].iloc[0])
        if xgb > patokan:
            st.warning("Pada pengujian ini, memakai jumlah peminat tahun lalu sebagai patokan masih lebih akurat daripada XGBoost berdasarkan selisih rata-rata. Model belum tentu lebih baik hanya karena lebih rumit.")
    with st.expander("Detail teknis untuk laporan penelitian"):
        st.dataframe(hasil[["Metode", "n_uji", "MAE", "MAPE", "R2", "RMSLE", "n_prediksi_negatif"]].rename(columns={"n_uji": "Baris yang diuji", "n_prediksi_negatif": "Prediksi negatif"}), hide_index=True, width="stretch")
        st.markdown("**MAE:** selisih rata-rata dalam orang. **MAPE:** selisih dalam persen, sangat sensitif pada jumlah peminat kecil. **R²:** ukuran kecocokan terhadap data. **RMSLE:** ukuran selisih pada skala log.\n\nRMSLE kosong jika ada prediksi negatif. Prediksi negatif tidak boleh dibaca sebagai jumlah orang yang mungkin terjadi. Varian log mengubah skala target saat pelatihan dan mengembalikannya ke skala orang saat evaluasi.")
    st.caption("Data latih: 2021–2024. Data uji: 2025. Hasil berasal dari berkas evaluasi kelompok; model yang belum tercantum belum tersedia di versi ini. Pilihan dengan/tanpa riwayat memiliki baris uji berbeda.")


def panduan() -> None:
    st.title("Biar lebih mudah membaca data")
    st.write("Beberapa istilah yang akan kamu temui saat menjelajahi jurusan.")
    for judul, isi in {
        "Apa yang dimaksud peminat?": "Jumlah pendaftar yang tercatat untuk satu jurusan, satu jalur, dan satu tahun. Angka lintas jurusan atau lintas jalur tidak selalu mewakili orang yang berbeda.",
        "Apa itu daya tampung?": "Jumlah kursi yang tersedia untuk jurusan pada tahun dan jalur yang dipilih. Di tabel, kami menyebutnya ‘Kursi tersedia’.",
        "Mengapa SNBP dan SNBT dipisahkan?": "SNBP adalah seleksi berdasarkan prestasi, sedangkan SNBT berdasarkan tes. Satu orang bisa mengikuti kedua jalur, jadi jumlah peminatnya tidak dijumlahkan.",
        "Apakah peminat per kursi sama dengan peluang lolos?": "Tidak. Jika 400 peminat memperebutkan 40 kursi, rasionya 10 peminat per kursi. Rasio itu bukan peluang lolos pribadi karena hasil seleksi juga bergantung pada kriteria dan kemampuan peserta.",
        "Mengapa ada tahun atau angka yang kosong?": "Data dari sumber belum tersedia untuk bagian tersebut. Aplikasi tidak menganggap nilai kosong sebagai nol dan tidak membuat angka pengganti.",
        "Dari mana datanya?": "Snapshot API publik SNPMB yang diakses kelompok pada September 2026, dengan riwayat 2021–2025. Cakupannya PTN peserta yang tersedia dalam data. Entri fakultas dikeluarkan agar perbandingan berfokus pada program studi.",
    }.items():
        with st.expander(judul): st.write(isi)
    with st.container(border=True):
        st.subheader("Tentang proyek ini")
        st.write("Aplikasi ini adalah bagian dari tugas besar Machine Learning: estimasi jumlah peminat program studi sebagai dasar pembentukan angka pembanding antarperguruan tinggi. Universitas Andalas hanya contoh ilustrasi.")
        st.caption("Bukan situs resmi SNPMB. Data ini bukan jaminan diterima. Kuota historis diasumsikan diumumkan sebelum pendaftaran; beberapa atribut penelitian diturunkan dari aturan nama.")


def utama() -> None:
    st.set_page_config(page_title="SNPMB Insight · Kenali pilihan kuliahmu", page_icon=":material/school:", layout="wide")
    st.html((Path(__file__).with_name("style.css")).read_text(encoding="utf-8"))
    halaman = sidebar()
    st.caption(f"SNPMB INSIGHT  /  {halaman.upper()}")
    try:
        lokasi = siapkan_panel()
        data = baca_data(lokasi, lokasi.stat().st_mtime_ns)
    except (OSError, ValueError, RuntimeError, subprocess.TimeoutExpired) as galat:
        st.error("Data belum bisa dibuka. Coba muat ulang halaman. Jika masih gagal, kirim detail di bawah kepada pengelola.")
        with st.expander("Detail masalah untuk pengelola"):
            st.code(str(galat))
        st.stop()
    if halaman == "Beranda": beranda(data)
    elif halaman == "Cari Jurusan": jelajah(data, False)
    elif halaman == "Bandingkan Jurusan": jelajah(data, True)
    elif halaman == "Perkiraan Peminat": perkiraan()
    elif halaman == "Hasil Pengujian": pengujian()
    else: panduan()
    st.divider()
    st.caption("SNPMB Insight  ·  Data 2021–2025  ·  Sumber: API publik SNPMB, diakses September 2026")


if __name__ == "__main__":
    utama()
