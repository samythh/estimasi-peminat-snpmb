"""
Perbandingan model dan pemilihan model sementara per skenario (K-26).

Pemilihan memakai skor VALIDASI dari lipatan_waktu() (data latih 2021-2024),
bukan data uji 2025 (K-06). Data uji hanya dilaporkan sebagai kinerja akhir
dari hasil/evaluasi.csv. Konfigurasi setiap model disalin dari sel
ISI BAGIAN INI notebook pemiliknya dan harus diperbarui bila notebook berubah.

    python scripts/bandingkan_model.py

Keluaran:
    hasil/validasi_perbandingan_model.csv   skor validasi per skenario x model x target
    hasil/perbandingan_model.csv            konfigurasi terpilih + skor uji 2025
"""

import sys
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.linear_model import LinearRegression
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from xgboost import XGBRegressor

AKAR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(AKAR / "src"))
from fondasi import (FILE_EVALUASI, RANDOM_STATE, SKENARIO, VERSI_FONDASI,  # noqa: E402
                     dari_log, info_baris, ke_log, lipatan_waktu, log_fitur, muat_data)

FILE_VALIDASI = AKAR / "hasil" / "validasi_perbandingan_model.csv"
FILE_PERBANDINGAN = AKAR / "hasil" / "perbandingan_model.csv"


# Konfigurasi final dari notebook anggota (fondasi versi 2).
def lr(target):        # notebooks/01_linear_regression.ipynb (Ihsan)
    if target == "log":
        return make_pipeline(log_fitur(), StandardScaler(), LinearRegression())
    return make_pipeline(StandardScaler(), LinearRegression())


def rf(target):        # notebooks/02_random_forest.ipynb (Shiddiq), hasil penyetelan
    return RandomForestRegressor(n_estimators=300, max_depth=None, min_samples_leaf=2,
                                 max_features=0.33, random_state=RANDOM_STATE, n_jobs=-1)


def xgb(target):       # notebooks/03_xgboost.ipynb (Duha)
    return XGBRegressor(n_estimators=500, learning_rate=0.05, max_depth=6,
                        random_state=RANDOM_STATE, n_jobs=-1)


MODEL = {"linear_regression": lr, "random_forest": rf, "xgboost": xgb}
# Baseline terkuat per skenario (sama dengan notebooks/00_baseline.ipynb).
BASELINE = {"dengan_lag": "baseline_lag1", "tanpa_lag": "baseline_rata_kelompok",
            "tanpa_riwayat_sendiri": "baseline_rata_sejenis"}


def nilai(y, p):
    g = y - p
    neg = int((p < 0).sum())
    return {"MAE": float(np.mean(np.abs(g))),
            "R2": float(1 - np.sum(g ** 2) / np.sum((y - y.mean()) ** 2)),
            "RMSLE": float(np.sqrt(np.mean((np.log1p(p) - np.log1p(y)) ** 2))) if neg == 0 else np.nan,
            "n_prediksi_negatif": neg}


def prediksi_baseline(skenario, X, y, i_latih, i_val):
    if skenario == "dengan_lag":
        return X["peminat_lag1"].values[i_val]
    if skenario == "tanpa_riwayat_sendiri":
        return X["rata_peminat_prodi_sejenis_lag1"].values[i_val]
    kelompok = info_baris(X)["kelompok_bidang"].values
    rata = y.iloc[i_latih].groupby(kelompok[i_latih]).mean()
    return pd.Series(kelompok[i_val]).map(rata).values


def validasi():
    """Prediksi gabungan seluruh lipatan validasi; setiap baris validasi tepat sekali."""
    baris = []
    for skenario in SKENARIO:
        X, _, y, _ = muat_data(skenario, verbose=False)
        lipatan = lipatan_waktu(X)
        y_val = np.concatenate([y.values[v] for _, v in lipatan])
        p = np.concatenate([prediksi_baseline(skenario, X, y, l, v) for l, v in lipatan])
        baris.append({"skenario": skenario, "nama_model": BASELINE[skenario], "target": "asli",
                      "n_validasi": len(y_val), **nilai(y_val, p)})
        for nama, buat in MODEL.items():
            for target in ("asli", "log"):
                p = []
                for l, v in lipatan:
                    m = buat(target)
                    if target == "asli":
                        p.append(m.fit(X.iloc[l], y.iloc[l]).predict(X.iloc[v]))
                    else:
                        p.append(dari_log(m.fit(X.iloc[l], ke_log(y.iloc[l])).predict(X.iloc[v])))
                baris.append({"skenario": skenario, "nama_model": nama, "target": target,
                              "n_validasi": len(y_val), **nilai(y_val, np.concatenate(p))})
                print(f"  {skenario:22} {nama:18} {target:4} MAE validasi {baris[-1]['MAE']:.2f}",
                      flush=True)
    return pd.DataFrame(baris)


def pilih(val):
    """Aturan K-26, ditetapkan sebelum melihat hasil:
    1. Hanya konfigurasi tanpa prediksi negatif di validasi (peminat tidak mungkin negatif).
    2. MAE validasi terkecil.
    3. Bila tidak lebih baik dari baseline terkuat skenario itu, baseline yang dipakai.
    """
    pilihan = []
    for skenario, g in val.groupby("skenario", sort=False):
        base = g[g["nama_model"].str.startswith("baseline")].iloc[0]
        calon = g[~g["nama_model"].str.startswith("baseline") & (g["n_prediksi_negatif"] == 0)]
        terbaik = calon.sort_values("MAE").iloc[0]
        menang = terbaik["MAE"] < base["MAE"]
        dipilih = terbaik if menang else base
        pilihan.append({"skenario": skenario, "nama_model": dipilih["nama_model"],
                        "target": dipilih["target"], "MAE_validasi": dipilih["MAE"],
                        "model_terbaik": f"{terbaik['nama_model']} ({terbaik['target']})",
                        "MAE_validasi_model_terbaik": terbaik["MAE"],
                        "MAE_validasi_baseline": base["MAE"],
                        "alasan": ("MAE validasi terkecil dan lebih baik dari baseline"
                                   if menang else "tidak ada model yang lebih baik dari baseline")})
    return pd.DataFrame(pilihan)


def main():
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:  # noqa: BLE001
        pass
    print(f"Validasi dengan lipatan_waktu() (fondasi versi {VERSI_FONDASI}); data uji tidak dipakai.")
    val = validasi()
    val.round(4).to_csv(FILE_VALIDASI, index=False, encoding="utf-8-sig")

    pil = pilih(val)
    uji = pd.read_csv(FILE_EVALUASI)
    uji = uji[(uji["jalur"] == "gabungan") & (uji["versi_fondasi"] == VERSI_FONDASI)]
    pil = pil.merge(uji[["nama_model", "skenario", "target", "MAE", "MAPE", "R2", "RMSLE"]]
                    .rename(columns=lambda c: c if c in ("nama_model", "skenario", "target")
                            else f"{c}_uji_2025"),
                    on=["nama_model", "skenario", "target"], how="left", validate="one_to_one")
    pil.round(4).to_csv(FILE_PERBANDINGAN, index=False, encoding="utf-8-sig")
    print()
    print(pil.round(2).to_string(index=False))


if __name__ == "__main__":
    main()
