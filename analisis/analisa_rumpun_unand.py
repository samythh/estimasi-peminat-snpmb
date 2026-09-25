"""
Uji klaim "rumpun sosial-humaniora turun, rumpun kesehatan naik" pada SELURUH
prodi Unand yang riwayatnya lengkap 2021-2025 -- bukan hanya 5 prodi terpilih.

PENTING - dari mana rumpun ini berasal:
  API SNPMB TIDAK menyediakan field rumpun / kelompok ujian. Pemetaan di bawah
  disusun manual dari nama prodi dan merupakan penilaian penulis, bukan data
  dari sumber. Ia ditulis eksplisit di sini supaya bisa diperiksa dan diubah.
  Pengelompokan mengikuti rumpun keilmuan, bukan kelompok ujian SNBT
  (mis. AGRIBISNIS di sini masuk Pertanian, bukan Soshum).

Dijalankan per jalur: python analisa_rumpun_unand.py [SNBP|SNBT]
"""

import sys
from pathlib import Path

import numpy as np
import pandas as pd

FILE_UNAND = Path(__file__).resolve().parents[1] / "data" / "contoh_unand" / "unand_panel.csv"
JALUR = (sys.argv[1] if len(sys.argv) > 1 else "SNBP").upper()
FILE_KELUAR = (Path(__file__).resolve().parents[1] / "data" / "contoh_unand" /
               f"unand_rumpun_{JALUR.lower()}.csv")

RUMPUN = {
    "Sosial-Humaniora": [
        "ADMINISTRASI PUBLIK", "AKUNTANSI", "ANTROPOLOGI SOSIAL", "EKONOMI",
        "EKONOMI PEMBANGUNAN (KAMPUS PAYAKUMBUH)", "HUBUNGAN INTERNASIONAL",
        "HUKUM", "ILMU KOMUNIKASI", "ILMU POLITIK", "MANAJEMEN",
        "MANAJEMEN (KAMPUS 2 PAYAKUMBUH)", "PSIKOLOGI", "SASTRA INDONESIA",
        "SASTRA INGGRIS", "SASTRA JEPANG", "SASTRA MINANGKABAU", "SEJARAH",
        "SOSIOLOGI",
    ],
    "Kesehatan": [
        "FARMASI", "GIZI", "ILMU BIOMEDIS", "KEBIDANAN", "KEDOKTERAN",
        "KEDOKTERAN GIGI", "KEPERAWATAN", "KESEHATAN MASYARAKAT",
    ],
    "Teknik & Komputasi": [
        "SISTEM INFORMASI", "TEKNIK ELEKTRO", "TEKNIK INDUSTRI",
        "TEKNIK KOMPUTER", "TEKNIK LINGKUNGAN", "TEKNIK MESIN", "TEKNIK SIPIL",
    ],
    "Pertanian & Peternakan": [
        "AGRIBISNIS", "AGROEKOTEKNOLOGI", "AGROTEKNOLOGI", "ILMU TANAH",
        "PENYULUHAN PERTANIAN", "PETERNAKAN", "PETERNAKAN ( KAMPUS II PAYAKUMBUH)",
        "PROTEKSI TANAMAN", "TEKNIK PERTANIAN DAN BIOSISTEM",
        "TEKNOLOGI INDUSTRI PERTANIAN", "TEKNOLOGI PANGAN DAN HASIL PERTANIAN",
    ],
    "Sains Dasar": ["BIOLOGI", "FISIKA", "KIMIA", "MATEMATIKA"],
}

PETA = {prodi: rumpun for rumpun, daftar in RUMPUN.items() for prodi in daftar}


def main():
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:  # noqa: BLE001
        pass

    df = pd.read_csv(FILE_UNAND)
    df = df[(df["jalur"] == JALUR) & df["tahun"].notna() & df["peminat"].notna()]
    df = df.sort_values(["id_prodi", "tahun"])

    baris = []
    for id_prodi, g in df.groupby("id_prodi"):
        if g["tahun"].nunique() < 5:
            continue                      # hanya riwayat penuh 2021-2025
        awal, akhir = g.iloc[0], g.iloc[-1]
        nama = awal["prodi"]
        baris.append({
            "prodi": nama,
            "rumpun": PETA.get(nama, "TIDAK TERKLASIFIKASI"),
            "peminat_awal": int(awal["peminat"]),
            "peminat_akhir": int(akhir["peminat"]),
            "pct": (akhir["peminat"] - awal["peminat"]) / awal["peminat"] * 100,
            "slope": float(np.polyfit(g["tahun"], g["peminat"], 1)[0]),
        })

    t = pd.DataFrame(baris)
    belum = t[t["rumpun"] == "TIDAK TERKLASIFIKASI"]
    if len(belum):
        print("PERINGATAN - prodi belum masuk pemetaan rumpun:")
        print("  " + "\n  ".join(belum["prodi"]))

    t.to_csv(FILE_KELUAR, index=False, encoding="utf-8-sig")

    print("=" * 96)
    print(f"PERUBAHAN PEMINAT PER RUMPUN - JALUR {JALUR} - {len(t)} prodi riwayat penuh")
    print("Rumpun = klasifikasi manual penulis; API SNPMB tidak menyediakannya.")
    print("=" * 96)

    ring = t.groupby("rumpun").agg(
        n=("prodi", "size"),
        pct_rata=("pct", "mean"),
        pct_median=("pct", "median"),
        pct_min=("pct", "min"),
        pct_maks=("pct", "max"),
        n_naik=("pct", lambda s: int((s > 0).sum())),
        n_turun=("pct", lambda s: int((s < 0).sum())),
    ).sort_values("pct_rata", ascending=False)
    ring["konsisten"] = (ring[["n_naik", "n_turun"]].max(axis=1) / ring["n"] * 100).round(0)

    print(f"\n{'rumpun':<24} {'n':>3} {'rata%':>8} {'median%':>9} "
          f"{'min%':>8} {'maks%':>8} {'naik':>5} {'turun':>6} {'searah%':>8}")
    for r, v in ring.iterrows():
        print(f"{r:<24} {int(v['n']):>3} {v['pct_rata']:>7.1f}% {v['pct_median']:>8.1f}% "
              f"{v['pct_min']:>7.1f}% {v['pct_maks']:>7.1f}% {int(v['n_naik']):>5} "
              f"{int(v['n_turun']):>6} {int(v['konsisten']):>7}%")

    print("\nRincian per prodi (urut perubahan):")
    for r in ring.index:
        sub = t[t["rumpun"] == r].sort_values("pct", ascending=False)
        print(f"\n  {r} (n={len(sub)}):")
        for _, x in sub.iterrows():
            print(f"    {x['pct']:>+7.1f}%  {x['peminat_awal']:>5} -> "
                  f"{x['peminat_akhir']:>5}  {x['prodi']}")

    print(f"\n[simpan] {FILE_KELUAR}")

    sos = t[t["rumpun"] == "Sosial-Humaniora"]
    kes = t[t["rumpun"] == "Kesehatan"]
    print("\nVERDIKT klaim \"soshum turun, kesehatan naik\":")
    print(f"  Soshum   : {int((sos['pct'] < 0).sum())}/{len(sos)} turun, "
          f"rata-rata {sos['pct'].mean():+.1f}%")
    print(f"  Kesehatan: {int((kes['pct'] > 0).sum())}/{len(kes)} naik, "
          f"rata-rata {kes['pct'].mean():+.1f}%")


if __name__ == "__main__":
    main()
