"""
Contoh keluaran model: prediksi vs aktual 2025 untuk beberapa prodi.

Memakai konfigurasi terpilih per skenario dari hasil/perbandingan_model.csv
(jalankan scripts/bandingkan_model.py lebih dulu). Prediksi dibuat lewat
latih_dan_prediksi(), jadi pada skenario prodi baru setiap prodi ditebak oleh
model yang tidak pernah melihat prodi itu (K-24). Universitas Andalas hanya
ilustrasi (K-01); sisanya sampel acak nasional (random_state=42).

    python scripts/contoh_prediksi.py

Keluaran: hasil/contoh_prediksi_2025.csv
"""

import sys
from pathlib import Path

import numpy as np
import pandas as pd

AKAR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(AKAR / "src"))
sys.path.insert(0, str(AKAR / "scripts"))
from bandingkan_model import FILE_PERBANDINGAN, MODEL  # noqa: E402
from fondasi import (RANDOM_STATE, SKENARIO, dari_log, info_baris, ke_log,  # noqa: E402
                     latih_dan_prediksi, muat_data)

FILE_CONTOH = AKAR / "hasil" / "contoh_prediksi_2025.csv"
PRODI_UNAND = ["HUKUM", "MANAJEMEN", "KEDOKTERAN", "AGROTEKNOLOGI", "SISTEM INFORMASI"]
N_ACAK = 5


def prediksi_model(nama, target, skenario, X_train, y_train, X_test):
    buat = MODEL[nama]
    if target == "asli":
        return latih_dan_prediksi(lambda: buat(target), X_train, y_train, X_test, skenario)
    return dari_log(latih_dan_prediksi(lambda: buat(target), X_train, ke_log(y_train),
                                       X_test, skenario))


def prediksi_baseline(skenario, X_test):
    if skenario == "dengan_lag":
        return X_test["peminat_lag1"].values
    if skenario == "tanpa_riwayat_sendiri":
        return X_test["rata_peminat_prodi_sejenis_lag1"].values
    return None   # tanpa_lag: baseline kelompok sudah tercatat di evaluasi.csv


def main():
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:  # noqa: BLE001
        pass
    pilihan = pd.read_csv(FILE_PERBANDINGAN).set_index("skenario")
    semua = []
    for skenario in SKENARIO:
        X_train, X_test, y_train, y_test = muat_data(skenario, verbose=False)
        terbaik = pilihan.loc[skenario, "model_terbaik"]          # "nama (target)"
        nama, target = terbaik.split(" (")[0], terbaik.split(" (")[1].rstrip(")")
        p = prediksi_model(nama, target, skenario, X_train, y_train, X_test)

        info = info_baris(X_test).reset_index()
        tabel = info[["ptn_nama", "prodi", "jenjang", "jalur"]].copy()
        tabel.insert(0, "skenario", skenario)
        tabel["aktual_2025"] = y_test.values.astype(int)
        tabel["prediksi_model"] = np.round(p).astype(int)
        tabel["model"] = terbaik
        b = prediksi_baseline(skenario, X_test)
        tabel["prediksi_baseline"] = np.round(b).astype(int) if b is not None else pd.NA
        tabel["galat_model"] = tabel["prediksi_model"] - tabel["aktual_2025"]

        unand = tabel[tabel["ptn_nama"].str.contains("ANDALAS", case=False)
                      & tabel["prodi"].str.strip().isin(PRODI_UNAND) & (tabel["jenjang"] == "S1")]
        acak = tabel.drop(unand.index).sample(N_ACAK, random_state=RANDOM_STATE)
        semua.append(pd.concat([unand.assign(contoh="Unand (ilustrasi)"),
                                acak.assign(contoh="acak nasional")]))
    hasil = pd.concat(semua, ignore_index=True)
    hasil.to_csv(FILE_CONTOH, index=False, encoding="utf-8-sig")
    pd.set_option("display.width", 220)
    print(hasil.drop(columns=["jenjang"]).to_string(index=False))


if __name__ == "__main__":
    main()
