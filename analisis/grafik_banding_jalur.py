"""
Grafik pendamping: peminat lima prodi Unand pada DUA jalur, berdampingan.

Kunci desain:
  - Skala sumbu Y DIKUNCI sama di kedua panel (ditetapkan manual, bukan
    diserahkan ke matplotlib). Volume SNBT jauh lebih besar; skala per panel
    akan membuat penurunan SNBP terlihat setara padahal besarannya berbeda.
  - Warna per prodi konsisten antar panel -- warna mengikuti entitas, bukan
    peringkat, sehingga mata bisa menelusuri prodi yang sama lintas panel.
  - Peminat SNBP dan SNBT tidak pernah dijumlahkan (satu orang bisa mendaftar
    di kedua jalur untuk prodi yang sama).

Palet: slot 1-5 palet kategoris referensi, sudah divalidasi (light mode).
Kontras aqua/kuning/magenta di bawah 3:1 sehingga "relief rule" berlaku:
identitas dibawa legenda + label ujung, dan tabel nilai ikut disimpan CSV.
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
FILE_PANEL = AKAR / "data" / "olahan" / "snpmb_panel.csv"
DIR_GRAFIK = AKAR / "hasil" / "grafik"
FILE_PNG = DIR_GRAFIK / "banding_jalur_unand_2021_2025.png"
FILE_TABEL = DIR_GRAFIK / "banding_jalur_unand_2021_2025.csv"

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
PANEL = ["SNBP", "SNBT"]

# Skala Y ditetapkan manual dan dipakai kedua panel. 2.400 memuat nilai
# tertinggi (HUKUM SNBT 2.248) dengan sedikit ruang di atas.
Y_MAKS = 2400
Y_LANGKAH = 600


def muat():
    df = pd.read_csv(FILE_UNAND)
    df = df[df["tahun"].notna() & df["peminat"].notna()].copy()
    df["tahun"] = df["tahun"].astype(int)
    df["peminat"] = df["peminat"].astype(int)

    nama = [n for n, _ in SERI]
    data = {}
    for jalur in PANEL:
        sub = df[(df["jalur"] == jalur) & df["prodi"].isin(nama)
                 & (df["jenjang"] == "S1")]
        data[jalur] = {}
        for n in nama:
            g = sub[sub["prodi"] == n].sort_values("tahun")
            if g["tahun"].tolist() != TAHUN:
                raise SystemExit(
                    f"Riwayat '{n}' jalur {jalur} tidak lengkap: {g['tahun'].tolist()}")
            data[jalur][n] = g["peminat"].tolist()
    return data


def posisi_label(nilai_akhir, jarak_min):
    """Geser label ujung agar tidak bertumpuk; leader line yang menyambungkan."""
    urut = sorted(nilai_akhir.items(), key=lambda kv: kv[1], reverse=True)
    pos, sebelumnya = {}, None
    for nama, y in urut:
        if sebelumnya is not None and sebelumnya - y < jarak_min:
            y = sebelumnya - jarak_min
        pos[nama] = y
        sebelumnya = y
    return pos


def gambar_panel(ax, jalur, seri_data, pakai_nama):
    ax.set_ylim(0, Y_MAKS)
    ax.set_xlim(2020.85, 2025.05)
    ax.set_axisbelow(True)
    ax.yaxis.grid(True, color=GRID, linewidth=1.0, linestyle="-")
    ax.xaxis.grid(False)
    for sisi in ax.spines.values():
        sisi.set_visible(False)
    ax.tick_params(axis="both", length=0, colors=INK_2, labelsize=12)
    ax.set_xticks(TAHUN)
    ax.set_xticklabels([str(t) for t in TAHUN])
    ax.set_yticks(range(0, Y_MAKS + 1, Y_LANGKAH))
    ax.set_yticklabels([f"{v:,}".replace(",", ".")
                        for v in range(0, Y_MAKS + 1, Y_LANGKAH)])

    for nama, warna in SERI:
        ax.plot(TAHUN, seri_data[nama], color=warna, linewidth=2.0,
                solid_capstyle="round", solid_joinstyle="round", zorder=3)
        ax.plot(TAHUN, seri_data[nama], linestyle="none", marker="o",
                markersize=7, markerfacecolor=warna,
                markeredgecolor=SURFACE, markeredgewidth=2.0, zorder=4)

    akhir = {n: seri_data[n][-1] for n, _ in SERI}
    pos = posisi_label(akhir, jarak_min=Y_MAKS * 0.062)
    x_kiri = 2025.10

    teks = {}
    for nama, warna in SERI:
        ax.plot([2025, x_kiri - 0.03], [akhir[nama], pos[nama]],
                color=warna, linewidth=1.0, clip_on=False, zorder=2)
        if pakai_nama:
            teks[nama] = ax.text(x_kiri, pos[nama], nama, color=INK,
                                 fontsize=11, fontweight="semibold",
                                 va="center", ha="left", clip_on=False)

    # Kolom nilai ditaruh setelah nama terpanjang, diukur dari render nyata.
    if pakai_nama:
        ax.figure.canvas.draw()
        perender = ax.figure.canvas.get_renderer()
        ke_data = ax.transData.inverted()
        x_nilai = max(ke_data.transform(
            (t.get_window_extent(renderer=perender).x1, 0))[0]
            for t in teks.values()) + 0.09
    else:
        x_nilai = x_kiri

    for nama, _ in SERI:
        awal, akhir_n = seri_data[nama][0], akhir[nama]
        pct = (akhir_n - awal) / awal * 100
        ax.text(x_nilai, pos[nama],
                f"{akhir_n:,}".replace(",", ".") + f"  ({pct:+.0f}%)",
                color=INK_2, fontsize=11, va="center", ha="left", clip_on=False)

    ax.set_title(f"Jalur {jalur}", fontsize=15, fontweight="semibold",
                 color=INK, loc="left", pad=12)


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

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(13.333, 7.5), dpi=300,
                                   sharey=True)
    # Margin kiri memberi ruang judul sumbu; margin kanan menampung blok
    # label panel SNBT (nama + nilai) supaya tidak terpotong tepi gambar.
    fig.subplots_adjust(left=0.075, right=0.790, top=0.735, bottom=0.150,
                        wspace=0.28)

    gambar_panel(ax1, "SNBP", data["SNBP"], pakai_nama=False)
    gambar_panel(ax2, "SNBT", data["SNBT"], pakai_nama=True)
    ax1.set_ylabel("Jumlah peminat", fontsize=12.5, color=INK_2, labelpad=12)

    fig.text(0.075, 0.955, "Peminat lima program studi Universitas Andalas",
             fontsize=22, fontweight="semibold", color=INK, ha="left", va="top")
    fig.text(0.075, 0.898,
             "Prodi yang sama dapat bergerak berlawanan arah di kedua jalur, "
             "2021–2025 · skala sumbu Y sama di kedua panel",
             fontsize=13.5, color=INK_2, ha="left", va="top")

    kunci = [Line2D([0], [0], color=w, linewidth=2.0, marker="o", markersize=7,
                    markeredgecolor=SURFACE, markeredgewidth=1.5, label=n)
             for n, w in SERI]
    leg = fig.legend(handles=kunci, loc="upper left", bbox_to_anchor=(0.075, 0.855),
                     ncol=5, frameon=False, handlelength=1.5, handletextpad=0.5,
                     columnspacing=1.8, fontsize=12)
    for t in leg.get_texts():
        t.set_color(INK_2)

    fig.text(0.075, 0.062,
             "Peminat SNBP dan SNBT tidak dijumlahkan: satu pendaftar dapat "
             "melamar prodi yang sama di kedua jalur.",
             fontsize=12, color=INK_2, ha="left", va="center")
    fig.text(0.075, 0.024,
             "Sumber: API publik SNPMB (snpmb.id), diakses 7 September 2026  ·  "
             "angka dalam kurung = perubahan 2021→2025",
             fontsize=11, color=INK_3, ha="left", va="center")

    fig.savefig(FILE_PNG, dpi=300)
    plt.close(fig)

    tabel = pd.concat(
        {j: pd.DataFrame(data[j], index=TAHUN) for j in PANEL},
        names=["jalur", "tahun"])
    tabel.to_csv(FILE_TABEL, encoding="utf-8-sig")
    print(f"[simpan] {FILE_PNG}")
    print(f"[simpan] {FILE_TABEL}")
    print()
    print(tabel.to_string())

    cetak_selisih()


def cetak_selisih():
    """PTN & prodi yang hanya ada di salah satu jalur."""
    d = pd.read_csv(FILE_PANEL)
    snbp, snbt = d[d["jalur"] == "SNBP"], d[d["jalur"] == "SNBT"]

    ptn_p = snbp[["id_ptn", "ptn_nama"]].drop_duplicates()
    ptn_t = snbt[["id_ptn", "ptn_nama"]].drop_duplicates()
    set_p, set_t = set(ptn_p["id_ptn"]), set(ptn_t["id_ptn"])

    print("\n" + "=" * 96)
    print("PTN: SNBP vs SNBT")
    print("=" * 96)
    print(f"SNBP {len(set_p)} PTN  ·  SNBT {len(set_t)} PTN  ·  irisan {len(set_p & set_t)}")

    hanya_p = ptn_p[ptn_p["id_ptn"].isin(set_p - set_t)]
    hanya_t = ptn_t[ptn_t["id_ptn"].isin(set_t - set_p)]
    print(f"\nAda di SNBP tapi TIDAK di SNBT ({len(hanya_p)}):")
    for _, r in hanya_p.sort_values("id_ptn").iterrows():
        print(f"  id_ptn={r['id_ptn']:<5} {r['ptn_nama']}")
    print(f"\nAda di SNBT tapi TIDAK di SNBP ({len(hanya_t)}):")
    for _, r in hanya_t.sort_values("id_ptn").iterrows():
        print(f"  id_ptn={r['id_ptn']:<5} {r['ptn_nama']}")
    if hanya_t.empty:
        print("  (tidak ada)")

    kol = ["id_prodi", "kode_prodi", "prodi", "jenjang", "ptn_nama"]
    pr_p = snbp[kol].drop_duplicates("id_prodi")
    pr_t = snbt[kol].drop_duplicates("id_prodi")
    sp, st = set(pr_p["id_prodi"]), set(pr_t["id_prodi"])

    print("\n" + "=" * 96)
    print("PRODI: SNBP vs SNBT")
    print("=" * 96)
    print(f"di kedua jalur {len(sp & st)}  ·  hanya SNBP {len(sp - st)}  ·  "
          f"hanya SNBT {len(st - sp)}")

    for judul, tabel, beda in (("HANYA DI SNBP", pr_p, sp - st),
                               ("HANYA DI SNBT", pr_t, st - sp)):
        sub = tabel[tabel["id_prodi"].isin(beda)].sort_values(["ptn_nama", "prodi"])
        print(f"\n{judul} ({len(sub)}):")
        print(f"  {'id_prodi':<10} {'jjg':<4} {'prodi':<44} PTN")
        for _, r in sub.iterrows():
            print(f"  {r['id_prodi']:<10} {str(r['jenjang']):<4} "
                  f"{str(r['prodi'])[:44]:<44} {r['ptn_nama']}")


if __name__ == "__main__":
    main()
