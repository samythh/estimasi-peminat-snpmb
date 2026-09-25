"""
Fondasi bersama pemodelan: memuat data, validasi, lipatan waktu, evaluasi.

Dipakai oleh SEMUA model (Linear Regression, Random Forest, XGBoost) supaya
ketiganya dilatih dan dinilai pada data yang persis sama.

Pemakaian singkat:
    from fondasi import muat_data, evaluasi, lipatan_waktu, ke_log, dari_log
    X_train, X_test, y_train, y_test = muat_data("dengan_lag")
    ...latih model...
    evaluasi(y_test, prediksi, "random_forest", "dengan_lag", None)

Keputusan yang diterapkan di sini (rincian: docs/KEPUTUSAN_METODOLOGI.md):
  - Pembagian temporal: latih 2021-2024, uji 2025 (K-06).
  - Tanpa imputasi: baris dengan nilai kosong dikeluarkan, bukan diisi (K-05).
  - Fitur terlarang tidak pernah masuk X (K-07).
  - Entri fakultas ITB dikeluarkan (K-09).
  - daya_tampung tahun berjalan, BUKAN daya_tampung_kini (K-13).
  - is_new bukan fitur (K-14).
  - Target skala asli; ke_log()/dari_log() untuk varian log (K-15).
  - is_pendidikan & is_psdku diturunkan dari nama (K-16).
  - peminat_lag2 tidak dipakai secara bawaan (K-17).
  - lipatan_waktu() untuk penyetelan hyperparameter (K-18).
"""

import json
import os
import re
import sys
from datetime import datetime
from functools import lru_cache
from pathlib import Path

import numpy as np
import pandas as pd

AKAR = Path(__file__).resolve().parents[1]
FILE_PANEL = AKAR / "data" / "olahan" / "snpmb_panel.csv"
FILE_MENTAH = [AKAR / "data" / "mentah" / "mentah_snbp.json",
               AKAR / "data" / "mentah" / "mentah_snbt.json"]
# Bisa dialihkan lewat variabel lingkungan, mis. saat menguji template.
FILE_EVALUASI = Path(os.environ.get("FONDASI_FILE_EVALUASI",
                                    AKAR / "hasil" / "evaluasi.csv"))

RANDOM_STATE = 42
TAHUN_LATIH = (2021, 2022, 2023, 2024)
TAHUN_UJI = 2025
SKENARIO = ("dengan_lag", "tanpa_lag")
JALUR = ("SNBP", "SNBT")
TARGET = "peminat"

FITUR_NUMERIK = ["daya_tampung", "jumlah_prodi_ptn"]
FITUR_BINER = ["is_ptnbh", "is_akademik", "is_vokasi", "is_ptkin",
               "is_pendidikan", "is_psdku"]
FITUR_KATEGORIK = ["jenjang", "portofolio", "kelompok_bidang", "provinsi", "jalur"]
FITUR_LAG = ["peminat_lag1", "daya_tampung_lag1"]

# Tidak boleh ada di X dalam kondisi apa pun (K-07, K-13, K-14).
KOLOM_TERLARANG = {
    "terima", "total_peminat_ptn", "terima_lag1",
    "proporsi_peminat_lokal", "jumlah_provinsi_asal",
    "daya_tampung_kini", "is_new", "is_fakultas", TARGET,
    "id_ptn", "ptn_nama", "id_prodi", "kode_prodi", "prodi", "kota", "tahun",
}

# PTN kependidikan (eks-IKIP), dari nama PTN: 12 PTN (K-16).
POLA_PTN_PENDIDIKAN = re.compile(r"UNIVERSITAS NEGERI|PENDIDIKAN")
# Program Studi di Luar Kampus Utama, dari nama prodi (K-16). "K. KAB" / "K, KAB"
# menangkap singkatan kampus pada Politeknik Negeri Pontianak.
POLA_PSDKU = re.compile(r"PSDKU|KAMPUS|\bK[.,]\s*KAB")


# --------------------------------------------------------------------------
# Penyiapan panel
# --------------------------------------------------------------------------
@lru_cache(maxsize=1)
def _atribut_ptn():
    """Atribut PTN dari daftar PTN mentah (identik di kedua jalur)."""
    baris = {}
    for berkas in FILE_MENTAH:
        for p in json.loads(berkas.read_text(encoding="utf-8"))["ptn"]:
            prov = (p.get("provinsi") or [{}])[0].get("nama_prov1")
            baris.setdefault(int(p["id_ptn"]), {
                "id_ptn": int(p["id_ptn"]),
                "is_ptnbh": int(p["is_ptnbh"]),
                "is_akademik": int(p["is_akademik"]),
                "is_vokasi": int(p["is_vokasi"]),
                "is_ptkin": int(p["is_ptkin"]),
                "provinsi": prov,
                "is_pendidikan": int(bool(POLA_PTN_PENDIDIKAN.search(str(p["nama"]).upper()))),
            })
    return pd.DataFrame(baris.values())


@lru_cache(maxsize=1)
def _panel_pemodelan():
    """Baris yang BISA dimodelkan: punya target, bukan entri fakultas."""
    df = pd.read_csv(FILE_PANEL)
    df = df[df[TARGET].notna() & (df["is_fakultas"] == 0)].copy()
    df["tahun"] = df["tahun"].astype(int)
    df = df.merge(_atribut_ptn(), on="id_ptn", how="left", validate="many_to_one")
    df["is_psdku"] = df["prodi"].str.upper().str.contains(POLA_PSDKU).astype(int)
    return df


def _nama_kolom_aman(nama):
    """XGBoost menolak karakter tertentu pada nama fitur; ganti dengan '_'."""
    return re.sub(r"[^0-9A-Za-z_]+", "_", str(nama)).strip("_")


# --------------------------------------------------------------------------
# API publik
# --------------------------------------------------------------------------
def muat_data(skenario, jalur=None, sertakan_lag2=False, drop_first=False,
              verbose=True):
    """Kembalikan X_train, X_test, y_train, y_test.

    skenario : "dengan_lag" -> fitur struktural + peminat_lag1 + daya_tampung_lag1,
                               hanya baris yang kedua lag-nya terisi.
               "tanpa_lag"  -> fitur struktural saja, semua baris bertarget.
    jalur    : None (gabungan SNBP+SNBT, jalur menjadi fitur), "SNBP", atau "SNBT".
    sertakan_lag2 : tambahkan peminat_lag2 (tidak disarankan; lihat K-17).
    drop_first    : buang kategori pertama pada one-hot. Berguna untuk
                    menafsirkan koefisien Linear Regression; tidak mengubah
                    prediksi.

    Indeks X dan y adalah (id_prodi, jalur, tahun), bukan fitur. Dipakai oleh
    lipatan_waktu() dan info_baris().
    """
    if skenario not in SKENARIO:
        raise ValueError(f"skenario harus salah satu dari {SKENARIO}, bukan {skenario!r}")
    if jalur is not None and jalur not in JALUR:
        raise ValueError(f"jalur harus None, 'SNBP', atau 'SNBT', bukan {jalur!r}")
    if sertakan_lag2 and skenario != "dengan_lag":
        raise ValueError("sertakan_lag2 hanya berlaku untuk skenario 'dengan_lag'")

    df = _panel_pemodelan()
    if jalur is not None:
        df = df[df["jalur"] == jalur]
    df = df[df["tahun"].isin(TAHUN_LATIH + (TAHUN_UJI,))].copy()
    laporan = [f"baris bertarget (tanpa entri fakultas): {len(df)}"]

    fitur_lag = []
    if skenario == "dengan_lag":
        fitur_lag = list(FITUR_LAG)
        sebelum = len(df)
        df = df[df["peminat_lag1"].notna() & df["daya_tampung_lag1"].notna()]
        laporan.append(f"dibuang karena lag1 kosong: {sebelum - len(df)} "
                       f"(termasuk seluruh baris 2021)")
        hilang_lag2 = int(df["peminat_lag2"].isna().sum())
        laporan.append(f"INFO peminat_lag2: bila disertakan, {hilang_lag2} baris lagi "
                       f"hilang ({hilang_lag2 / max(len(df), 1):.0%}), termasuk seluruh 2022")
        if sertakan_lag2:
            fitur_lag.append("peminat_lag2")
            df = df[df["peminat_lag2"].notna()]
            laporan.append(f"peminat_lag2 disertakan: {hilang_lag2} baris dibuang")

    kategorik = [k for k in FITUR_KATEGORIK if not (k == "jalur" and jalur is not None)]
    kolom_fitur = FITUR_NUMERIK + FITUR_BINER + fitur_lag + kategorik

    sebelum = len(df)
    df = df.dropna(subset=kolom_fitur)
    if len(df) != sebelum:
        laporan.append(f"dibuang karena fitur kosong (tanpa imputasi): {sebelum - len(df)}")

    # One-hot pada seluruh baris terpilih: daftar kategori (provinsi, jenjang, ...)
    # diketahui sebelumnya, jadi ini tidak membocorkan target, dan menjamin kolom
    # latih & uji identik.
    dummies = pd.get_dummies(df[kategorik], prefix=kategorik, dtype=int,
                             drop_first=drop_first)
    dummies.columns = [_nama_kolom_aman(c) for c in dummies.columns]

    X = pd.concat([df[FITUR_NUMERIK + FITUR_BINER + fitur_lag].astype(float),
                   dummies.astype(float)], axis=1)
    X.index = pd.MultiIndex.from_frame(df[["id_prodi", "jalur", "tahun"]])
    y = pd.Series(df[TARGET].astype(float).values, index=X.index, name=TARGET)

    uji = X.index.get_level_values("tahun") == TAHUN_UJI
    X_train, X_test, y_train, y_test = X[~uji], X[uji], y[~uji], y[uji]

    _periksa(X_train, X_test, y_train, y_test)

    if verbose:
        th = sorted(X_train.index.get_level_values("tahun").unique())
        print(f"[muat_data] skenario={skenario}  jalur={jalur or 'gabungan'}")
        for baris in laporan:
            print(f"  - {baris}")
        print(f"  latih: {len(X_train)} baris (tahun {th[0]}-{th[-1]})  |  "
              f"uji: {len(X_test)} baris (tahun {TAHUN_UJI})  |  fitur: {X.shape[1]}")
        print("  validasi: lolos (tanpa kolom terlarang, tanpa NaN, split temporal, "
              "kolom latih = kolom uji)")
    return X_train, X_test, y_train, y_test


def _periksa(X_train, X_test, y_train, y_test):
    """Pemeriksaan pasca-prapemrosesan. Gagal = berhenti, bukan peringatan."""
    terlarang = KOLOM_TERLARANG & set(X_train.columns)
    assert not terlarang, f"Kolom terlarang masuk ke fitur: {terlarang}"
    assert list(X_train.columns) == list(X_test.columns), "Kolom latih dan uji berbeda"
    for nama, obj in (("X_train", X_train), ("X_test", X_test),
                      ("y_train", y_train), ("y_test", y_test)):
        assert not obj.isna().any().any() if isinstance(obj, pd.DataFrame) \
            else not obj.isna().any(), f"Ada NaN di {nama}"
    th_latih = set(X_train.index.get_level_values("tahun"))
    th_uji = set(X_test.index.get_level_values("tahun"))
    assert th_latih <= set(TAHUN_LATIH), f"Tahun latih keluar batas: {th_latih}"
    assert th_uji == {TAHUN_UJI}, f"Tahun uji harus hanya {TAHUN_UJI}: {th_uji}"
    for nama, X in (("X_train", X_train), ("X_test", X_test)):
        assert not X.index.duplicated().any(), f"Baris duplikat di {nama}"
        assert all(np.issubdtype(t, np.number) for t in X.dtypes), f"Kolom non-angka di {nama}"
    assert (y_train >= 0).all() and (y_test >= 0).all(), "Target negatif"


def info_baris(X):
    """Identitas baris (PTN, prodi, kelompok bidang, provinsi) untuk X tertentu.

    Tidak dipakai sebagai fitur; untuk baseline, analisis galat, dan angka
    pembanding per PTN.
    """
    kunci = ["id_prodi", "jalur", "tahun"]
    info = _panel_pemodelan()[kunci + ["id_ptn", "ptn_nama", "prodi", "jenjang",
                                       "kelompok_bidang", "provinsi"]]
    return (X.index.to_frame(index=False)
             .merge(info, on=kunci, how="left", validate="one_to_one")
             .set_index(kunci))


def lipatan_waktu(X_train):
    """Lipatan validasi silang berbasis waktu (expanding window).

    Untuk setiap tahun latih kecuali yang pertama: latih pada tahun-tahun
    sebelumnya, validasi pada tahun itu. Pakai sebagai `cv=` di GridSearchCV,
    RandomizedSearchCV, atau cross_val_score. Data uji 2025 tidak tersentuh.

        dengan_lag: 2022 -> 2023, 2022-2023 -> 2024
        tanpa_lag : 2021 -> 2022, 2021-2022 -> 2023, 2021-2023 -> 2024
    """
    tahun = np.asarray(X_train.index.get_level_values("tahun"))
    lipatan = []
    for t in sorted(set(tahun))[1:]:
        lipatan.append((np.where(tahun < t)[0], np.where(tahun == t)[0]))
    return lipatan


def ke_log(y):
    """Target ke skala log: log(1 + y)."""
    return np.log1p(y)


def dari_log(prediksi):
    """Prediksi skala log kembali ke skala asli (dibatasi >= 0)."""
    return np.clip(np.expm1(prediksi), 0, None)


def evaluasi(y_true, y_pred, nama_model, skenario, jalur, target="asli",
             n_latih=None, n_fitur=None, catatan="", simpan=True):
    """Hitung MAE, MAPE, R2, RMSLE lalu simpan satu baris ke hasil/evaluasi.csv.

    y_true dan y_pred HARUS dalam skala asli (jumlah orang). Untuk model yang
    dilatih pada log, kembalikan dulu prediksinya dengan dari_log().

    Baris dengan kunci (nama_model, skenario, jalur, target) yang sama
    diganti, sehingga tabel selalu berisi hasil terbaru per konfigurasi.
    simpan=False: hanya hitung & cetak, tidak menulis berkas.
    """
    if skenario not in SKENARIO:
        raise ValueError(f"skenario harus salah satu dari {SKENARIO}")
    if target not in ("asli", "log"):
        raise ValueError("target harus 'asli' atau 'log'")

    yt = np.asarray(y_true, dtype=float)
    yp = np.asarray(y_pred, dtype=float).ravel()
    if yt.shape != yp.shape:
        raise ValueError(f"Panjang y_true ({len(yt)}) dan y_pred ({len(yp)}) berbeda")
    if np.isnan(yp).any():
        raise ValueError("y_pred mengandung NaN")
    if target == "log" and yp.max() < 30 and yt.max() > 300:
        raise ValueError("Prediksi tampak masih dalam skala log. "
                         "Kembalikan dulu dengan dari_log(prediksi).")

    galat = yt - yp
    mae = float(np.mean(np.abs(galat)))
    nonnol = yt != 0
    mape = float(np.mean(np.abs(galat[nonnol] / yt[nonnol])) * 100)
    r2 = float(1 - np.sum(galat ** 2) / np.sum((yt - yt.mean()) ** 2))
    n_negatif = int((yp < 0).sum())
    rmsle = (float(np.sqrt(np.mean((np.log1p(yp) - np.log1p(yt)) ** 2)))
             if n_negatif == 0 else np.nan)

    baris = {
        "waktu": datetime.now().isoformat(timespec="seconds"),
        "nama_model": nama_model,
        "skenario": skenario,
        "jalur": jalur or "gabungan",
        "target": target,
        "n_latih": n_latih,
        "n_uji": len(yt),
        "n_fitur": n_fitur,
        "MAE": round(mae, 2),
        "MAPE": round(mape, 2),
        "n_mape_dikecualikan": int((~nonnol).sum()),
        "R2": round(r2, 4),
        "RMSLE": round(rmsle, 4) if not np.isnan(rmsle) else np.nan,
        "n_prediksi_negatif": n_negatif,
        "catatan": catatan,
    }

    if simpan:
        kunci = ["nama_model", "skenario", "jalur", "target"]
        FILE_EVALUASI.parent.mkdir(parents=True, exist_ok=True)
        if FILE_EVALUASI.exists():
            lama = pd.read_csv(FILE_EVALUASI)
            sama = (lama[kunci] == pd.Series({k: baris[k] for k in kunci})).all(axis=1)
            tabel = pd.concat([lama[~sama], pd.DataFrame([baris])], ignore_index=True)
        else:
            tabel = pd.DataFrame([baris])
        tabel.to_csv(FILE_EVALUASI, index=False, encoding="utf-8-sig")

    rmsle_txt = f"{rmsle:.4f}" if not np.isnan(rmsle) else "- (ada prediksi negatif)"
    print(f"[evaluasi] {nama_model} | {skenario} | {baris['jalur']} | target={target}")
    print(f"  MAE={mae:.2f}  MAPE={mape:.2f}% ({baris['n_mape_dikecualikan']} baris "
          f"peminat=0 dikecualikan)  R2={r2:.4f}  RMSLE={rmsle_txt}")
    if n_negatif:
        print(f"  PERHATIAN: {n_negatif} prediksi bernilai negatif")
    return baris


# --------------------------------------------------------------------------
def _ringkasan():
    """python src/fondasi.py -> ringkasan data per skenario & jalur."""
    for skenario in SKENARIO:
        for jalur in (None,) + JALUR:
            muat_data(skenario, jalur)
            print()
    X, *_ = muat_data("tanpa_lag", verbose=False)
    print("Fitur tanpa_lag (gabungan):", list(X.columns))


def _tinjau_psdku():
    """python src/fondasi.py --tinjau-psdku -> daftar prodi berlabel is_psdku."""
    # Tinjau seluruh katalog prodi non-fakultas, termasuk prodi baru tanpa target.
    # Pemodelan hanya memakai 170 prodi bertarget, tetapi validasi aturan nama
    # harus mencakup 182 prodi PSDKU yang tersedia di katalog (K-16).
    df = pd.read_csv(FILE_PANEL)
    df = df[df["is_fakultas"] == 0].drop_duplicates("id_prodi").copy()
    df["is_psdku"] = df["prodi"].str.upper().str.contains(POLA_PSDKU).astype(int)
    ps = df[df["is_psdku"] == 1].sort_values(["ptn_nama", "prodi"])
    print(f"is_psdku = 1: {len(ps)} prodi dari {len(df)}")
    for _, r in ps.iterrows():
        print(f"  {r['prodi'][:60]:<60} {r['ptn_nama']}")


if __name__ == "__main__":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:  # noqa: BLE001
        pass
    if "--tinjau-psdku" in sys.argv:
        _tinjau_psdku()
    else:
        _ringkasan()
