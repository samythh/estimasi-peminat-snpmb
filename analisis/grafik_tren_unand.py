"""
Grafik garis tren peminat SNBP 2021-2025 untuk 5 prodi Universitas Andalas.
Keluaran PNG resolusi tinggi (300 dpi, rasio 16:9) siap tempel ke PPT.

Membaca data/unand_panel.csv - tidak menarik ulang data, tidak mengarang nilai.

Palet: slot 1-5 palet kategoris referensi, sudah divalidasi (light mode):
  lightness band PASS - chroma floor PASS - CVD separation PASS (worst adj
  dE 9.1 protan) - normal-vision floor PASS (worst adj dE 19.6) - kontras
  WARN untuk aqua/kuning/magenta sehingga "relief rule" berlaku: setiap seri
  wajib punya label langsung yang terlihat (dipenuhi lewat label ujung +
  leader line, plus tabel nilai yang ikut disimpan sebagai CSV).
"""

import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")

import matplotlib.pyplot as plt
import pandas as pd
from matplotlib.lines import Line2D

AKAR = Path(__file__).resolve().parents[1]
FILE_UNAND = AKAR / "data" / "contoh_unand" / "unand_panel.csv"
DIR_GRAFIK = AKAR / "hasil" / "grafik"
FILE_PNG = DIR_GRAFIK / "tren_peminat_unand_2021_2025.png"
FILE_TABEL = DIR_GRAFIK / "tren_peminat_unand_2021_2025.csv"

# Urutan seri = urutan slot palet. Sengaja dikelompokkan turun lalu naik, dan
# disusun agar dua seri yang berpotongan di 2025 (ILMU KOMUNIKASI 437 vs
# ILMU BIOMEDIS 438) tidak menempati slot warna bersebelahan.
SERI = [
    ("HUKUM", "#2a78d6"),            # slot 1 biru
    ("MANAJEMEN", "#eb6834"),        # slot 2 oranye
    ("ILMU KOMUNIKASI", "#1baf7a"),  # slot 3 aqua
    ("KEBIDANAN", "#eda100"),        # slot 4 kuning
    ("ILMU BIOMEDIS", "#e87ba4"),    # slot 5 magenta
]

SURFACE = "#fcfcfb"
INK = "#0b0b0b"
INK_2 = "#52514e"
INK_3 = "#8a887f"
GRID = "#e8e7e3"

TAHUN = [2021, 2022, 2023, 2024, 2025]
JALUR_GRAFIK = "SNBP"


def muat():
    df = pd.read_csv(FILE_UNAND)
    df = df[df["tahun"].notna() & df["peminat"].notna()].copy()
    df["tahun"] = df["tahun"].astype(int)
    df["peminat"] = df["peminat"].astype(int)

    nama = [n for n, _ in SERI]
    # Panel memuat dua jalur; grafik ini khusus SNBP -- deret SNBP dan SNBT
    # terpisah dan tidak boleh dicampur dalam satu garis.
    sub = df[df["prodi"].isin(nama) & (df["jenjang"] == "S1")
             & (df["jalur"] == JALUR_GRAFIK)]

    data = {}
    for n in nama:
        g = sub[sub["prodi"] == n].sort_values("tahun")
        got = g["tahun"].tolist()
        if got != TAHUN:
            raise SystemExit(f"Riwayat '{n}' tidak lengkap 2021-2025: {got}")
        data[n] = g["peminat"].tolist()
    return data


def posisi_label(nilai_akhir, jarak_min):
    """Geser label ujung agar tidak bertumpuk; leader line yang menyambungkannya."""
    urut = sorted(nilai_akhir.items(), key=lambda kv: kv[1], reverse=True)
    pos = {}
    sebelumnya = None
    for nama, y in urut:
        if sebelumnya is not None and sebelumnya - y < jarak_min:
            y = sebelumnya - jarak_min
        pos[nama] = y
        sebelumnya = y
    return pos


def main():
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:  # noqa: BLE001
        pass

    DIR_GRAFIK.mkdir(parents=True, exist_ok=True)
    data = muat()

    plt.rcParams.update({
        "font.family": "sans-serif",
        "font.sans-serif": ["Segoe UI", "Arial", "DejaVu Sans"],
        "figure.facecolor": SURFACE,
        "axes.facecolor": SURFACE,
        "savefig.facecolor": SURFACE,
    })

    fig, ax = plt.subplots(figsize=(12.0, 6.75), dpi=300)
    fig.subplots_adjust(left=0.075, right=0.700, top=0.775, bottom=0.200)

    y_maks = 1500
    ax.set_ylim(0, y_maks)
    ax.set_xlim(2020.82, 2025.08)

    # Grid horizontal hairline, resesif; sumbu tanpa spine.
    ax.set_axisbelow(True)
    ax.yaxis.grid(True, color=GRID, linewidth=1.0, linestyle="-")
    ax.xaxis.grid(False)
    for sisi in ax.spines.values():
        sisi.set_visible(False)
    ax.tick_params(axis="both", length=0, colors=INK_2, labelsize=13)

    ax.set_xticks(TAHUN)
    ax.set_xticklabels([str(t) for t in TAHUN])
    ax.set_yticks(range(0, y_maks + 1, 300))
    ax.set_yticklabels([f"{v:,}".replace(",", ".") for v in range(0, y_maks + 1, 300)])

    for nama, warna in SERI:
        ax.plot(TAHUN, data[nama], color=warna, linewidth=2.0,
                solid_capstyle="round", solid_joinstyle="round", zorder=3)
        ax.plot(TAHUN, data[nama], linestyle="none", marker="o",
                markersize=8, markerfacecolor=warna,
                markeredgecolor=SURFACE, markeredgewidth=2.0, zorder=4)

    # Label langsung di ujung kanan. Satu baris per seri (nama kiri, nilai rata
    # kanan) supaya blok label pendek -- dengan begitu pergeseran anti-tumpuk
    # tetap kecil dan label tidak terlepas jauh dari garisnya. ILMU KOMUNIKASI
    # (437) dan ILMU BIOMEDIS (438) praktis berimpit di 2025, jadi selisihnya
    # dijembatani leader line lurus, bukan label yang ditumpuk.
    akhir = {nama: data[nama][-1] for nama, _ in SERI}
    pos = posisi_label(akhir, jarak_min=y_maks * 0.075)
    x_nama = 2025.13

    teks_nama = {}
    for nama, warna in SERI:
        y_data, y_lab = akhir[nama], pos[nama]
        ax.plot([2025, x_nama - 0.03], [y_data, y_lab],
                color=warna, linewidth=1.0, clip_on=False, zorder=2)
        teks_nama[nama] = ax.text(x_nama, y_lab, nama, color=INK, fontsize=13,
                                  fontweight="semibold", va="center", ha="left",
                                  clip_on=False)

    # Kolom nilai diletakkan tepat setelah nama TERPANJANG, diukur dari hasil
    # render sungguhan -- bukan koordinat tebakan yang bisa bertabrakan.
    fig.canvas.draw()
    perender = fig.canvas.get_renderer()
    ke_data = ax.transData.inverted()
    tepi_kanan = max(
        ke_data.transform((t.get_window_extent(renderer=perender).x1, 0))[0]
        for t in teks_nama.values()
    )
    x_nilai = tepi_kanan + 0.10

    for nama, _ in SERI:
        y_data, y_lab = akhir[nama], pos[nama]
        awal = data[nama][0]
        pct = (y_data - awal) / awal * 100
        ax.text(x_nilai, y_lab,
                f"{y_data:,}".replace(",", ".") + f"  ({pct:+.0f}%)",
                color=INK_2, fontsize=11.5, va="center", ha="left", clip_on=False)

    # Judul & subjudul
    fig.text(0.075, 0.945, "Peminat SNBP lima program studi Universitas Andalas",
             fontsize=21, fontweight="semibold", color=INK, ha="left", va="top")
    fig.text(0.075, 0.884,
             "Lima program studi dengan perubahan paling kontras, 2021–2025",
             fontsize=13.5, color=INK_2, ha="left", va="top")

    # Legenda (identitas tidak pernah lewat warna saja)
    kunci = [Line2D([0], [0], color=w, linewidth=2.0, marker="o", markersize=7,
                    markeredgecolor=SURFACE, markeredgewidth=1.5, label=n)
             for n, w in SERI]
    leg = ax.legend(handles=kunci, loc="lower left", bbox_to_anchor=(0.0, 1.015),
                    ncol=5, frameon=False, handlelength=1.5, handletextpad=0.5,
                    columnspacing=1.6, fontsize=11.5)
    for teks in leg.get_texts():
        teks.set_color(INK_2)

    ax.set_ylabel("Jumlah peminat", fontsize=12.5, color=INK_2, labelpad=14)

    # Menghubungkan grafik ke persoalan yang mendasari proyek: angka ini
    # belum bisa dinilai tanpa pembanding lintas-PTN.
    fig.text(0.075, 0.128,
             "Penurunan 34% pada Hukum dan kenaikan 72% pada Ilmu Biomedis tidak dapat "
             "dinilai tanpa pembanding:\n"
             "apakah ini pola khas Unand, atau tren nasional yang dialami semua PTN?",
             fontsize=12.5, color=INK_2, ha="left", va="top", linespacing=1.45)

    fig.text(0.075, 0.024,
             "Sumber: API publik SNPMB (snpmb.id), diakses 7 September 2026  ·  "
             "angka dalam kurung = perubahan 2021→2025",
             fontsize=11, color=INK_3, ha="left", va="center")

    fig.savefig(FILE_PNG, dpi=300)
    plt.close(fig)

    tabel = pd.DataFrame(data, index=TAHUN).rename_axis("tahun")
    tabel.to_csv(FILE_TABEL, encoding="utf-8-sig")

    print(f"[simpan] {FILE_PNG}")
    print(f"[simpan] {FILE_TABEL}  (tabel nilai pendamping)")
    print()
    print(tabel.to_string())


if __name__ == "__main__":
    main()
