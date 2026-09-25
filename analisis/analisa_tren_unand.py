"""
Ringkasan isi data/contoh_unand/unand_panel.csv: tren peminat per prodi 2021-2025.

Murni deskriptif - membaca CSV yang sudah ada, tidak menarik ulang data dan
tidak mengarang nilai. Prodi tanpa riwayat (is_new) dilaporkan terpisah.
"""

import sys
from pathlib import Path

import numpy as np
import pandas as pd

FILE_UNAND = Path(__file__).resolve().parents[1] / "data" / "contoh_unand" / "unand_panel.csv"

# Panel kini memuat dua jalur; analisis dijalankan untuk SATU jalur saja karena
# deret peminat SNBP dan SNBT terpisah dan tidak boleh dicampur.
JALUR = (sys.argv[1] if len(sys.argv) > 1 else "SNBP").upper()
FILE_RINGKAS = (Path(__file__).resolve().parents[1] / "data" / "contoh_unand" /
                f"unand_tren_peminat_{JALUR.lower()}.csv")


def kemiringan(tahun, nilai):
    """Kemiringan regresi linear peminat terhadap tahun (peminat per tahun)."""
    if len(tahun) < 2:
        return np.nan
    return float(np.polyfit(np.asarray(tahun, float), np.asarray(nilai, float), 1)[0])


def bangun_tren(df):
    hist = df[df["tahun"].notna() & df["peminat"].notna()].copy()
    hist["tahun"] = hist["tahun"].astype(int)
    hist["peminat"] = hist["peminat"].astype(int)
    hist = hist.sort_values(["id_prodi", "tahun"])

    catatan = []
    for id_prodi, grup in hist.groupby("id_prodi"):
        awal, akhir = grup.iloc[0], grup.iloc[-1]
        delta = int(akhir["peminat"] - awal["peminat"])
        catatan.append({
            "id_prodi": id_prodi,
            "prodi": awal["prodi"],
            "jenjang": awal["jenjang"],
            "n_tahun": len(grup),
            "tahun_awal": int(awal["tahun"]),
            "tahun_akhir": int(akhir["tahun"]),
            "peminat_awal": int(awal["peminat"]),
            "peminat_akhir": int(akhir["peminat"]),
            "delta": delta,
            "pct": round(delta / awal["peminat"] * 100, 1) if awal["peminat"] else np.nan,
            "slope": round(kemiringan(grup["tahun"], grup["peminat"]), 1),
            "rata_peminat": round(float(grup["peminat"].mean()), 1),
            "seri": " -> ".join(str(v) for v in grup["peminat"]),
        })
    return pd.DataFrame(catatan)


def tabel(judul, sub, kolom_urut, naik=True, n=10):
    print(f"\n{judul}")
    print("-" * 110)
    urut = sub.sort_values(kolom_urut, ascending=not naik).head(n)
    print(f"{'prodi':<42} {'jjg':<4} {'slope':>7} {'delta':>7} {'pct':>8}   {'seri peminat'}")
    for _, r in urut.iterrows():
        print(f"{str(r['prodi'])[:42]:<42} {str(r['jenjang']):<4} "
              f"{r['slope']:>7.1f} {r['delta']:>7} {r['pct']:>7.1f}%   {r['seri']}")


def main():
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:  # noqa: BLE001
        pass

    df = pd.read_csv(FILE_UNAND)
    tersedia = sorted(df["jalur"].dropna().unique())
    if JALUR not in tersedia:
        raise SystemExit(f"Jalur '{JALUR}' tidak ada. Tersedia: {tersedia}")
    df = df[df["jalur"] == JALUR].copy()

    print("=" * 110)
    print(f"ISI {FILE_UNAND.name} - JALUR {JALUR}  (jalur tersedia: {tersedia})")
    print("=" * 110)
    print(f"Baris                 : {len(df)}")
    print(f"Prodi unik            : {df['id_prodi'].nunique()}")
    print(f"Kolom                 : {list(df.columns)}")
    print("\nJumlah prodi per jenjang:")
    print(df.drop_duplicates("id_prodi")["jenjang"].value_counts().to_string())
    print("\nJumlah baris per tahun:")
    print(df["tahun"].value_counts(dropna=False).sort_index().to_string())

    tren = bangun_tren(df)
    tren.to_csv(FILE_RINGKAS, index=False, encoding="utf-8-sig")
    print(f"\n[simpan] {FILE_RINGKAS}  ({len(tren)} prodi berriwayat)")

    penuh = tren[tren["n_tahun"] >= 5]
    pendek = tren[tren["n_tahun"] < 5]

    print(f"\nProdi dengan riwayat penuh (>=5 tahun): {len(penuh)}")
    print(f"Prodi dengan riwayat pendek (<5 tahun): {len(pendek)}")

    print("\n" + "=" * 110)
    print("RIWAYAT PENUH 2021-2025")
    print("=" * 110)
    tabel("TREN PALING NAIK (kemiringan tertinggi)", penuh, "slope", naik=True)
    tabel("TREN PALING TURUN (kemiringan terendah)", penuh, "slope", naik=False)
    tabel("KENAIKAN RELATIF TERBESAR (%)", penuh, "pct", naik=True)
    tabel("PENURUNAN RELATIF TERBESAR (%)", penuh, "pct", naik=False)

    if len(pendek):
        print("\n" + "=" * 110)
        print("RIWAYAT PENDEK (<5 tahun) - jendela berbeda, jangan dibandingkan langsung")
        print("=" * 110)
        tabel("Paling naik", pendek, "slope", naik=True)
        tabel("Paling turun", pendek, "slope", naik=False)

    baru = df[df["is_new"] == 1].drop_duplicates("id_prodi")
    print(f"\nProdi tanpa riwayat / is_new == 1: {len(baru)}")
    for _, r in baru.sort_values("prodi").iterrows():
        dt = "" if pd.isna(r["daya_tampung_kini"]) else int(r["daya_tampung_kini"])
        print(f"  {str(r['jenjang']):<4} dt_snbp={str(dt):>5}  {r['prodi']}")

    print("\nAgregat peminat Unand per tahun:")
    agg = (df[df["tahun"].notna()]
           .groupby("tahun")
           .agg(prodi=("id_prodi", "nunique"),
                peminat=("peminat", "sum"),
                daya_tampung=("daya_tampung", "sum")))
    agg["peminat_per_kursi"] = (agg["peminat"] / agg["daya_tampung"]).round(2)
    print(agg.to_string())


if __name__ == "__main__":
    main()
