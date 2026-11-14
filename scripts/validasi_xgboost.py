"""Pemeriksaan notebook XGBoost, evaluasi, dan fondasi tanpa pelatihan ulang."""
import json
import sys
from pathlib import Path

import pandas as pd

AKAR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(AKAR / "src"))
from fondasi import VERSI_FONDASI, muat_data, lipatan_waktu


def utama():
    bukti = []
    template = json.loads((AKAR / "notebooks/template_model.ipynb").read_text(encoding="utf-8"))
    model = json.loads((AKAR / "notebooks/03_xgboost.ipynb").read_text(encoding="utf-8"))
    assert len(template["cells"]) == len(model["cells"])
    for asal, salinan in zip(template["cells"], model["cells"]):
        if "# === ISI BAGIAN INI ===" not in "".join(asal["source"]):
            assert "".join(asal["source"]) == "".join(salinan["source"])
    bukti.append("Sel di luar ISI BAGIAN INI identik dengan template versi 2.")
    for skenario in ("dengan_lag", "tanpa_lag", "tanpa_riwayat_sendiri"):
        X, Xu, y, yu = muat_data(skenario, verbose=False)
        for latih, validasi in lipatan_waktu(X):
            assert X.iloc[latih].index.get_level_values("tahun").max() < X.iloc[validasi].index.get_level_values("tahun").min()
        bukti.append(f"{skenario}: fondasi lolos; latih={len(X)}, uji={len(Xu)}, fitur={X.shape[1]}; lipatan temporal lolos.")

    kode = [c for c in model["cells"] if c["cell_type"] == "code"]
    assert all(c.get("execution_count") for c in kode)
    assert not any(o["output_type"] == "error" for c in kode for o in c.get("outputs", []))
    evaluasi = pd.read_csv(AKAR / "hasil/evaluasi.csv")
    xgb = evaluasi.loc[evaluasi["nama_model"].eq("xgboost")]
    xgb = xgb.loc[xgb["versi_fondasi"].eq(VERSI_FONDASI)]
    assert len(xgb) == 6
    assert set(zip(xgb.skenario, xgb.target, xgb.jalur)) == {
        (sk, target, "gabungan") for sk in ("dengan_lag", "tanpa_lag", "tanpa_riwayat_sendiri") for target in ("asli", "log")
    }
    for baris in xgb.itertuples():
        X, Xu, _, _ = muat_data(baris.skenario, verbose=False)
        assert (baris.n_latih, baris.n_uji, baris.n_fitur) == (len(X), len(Xu), X.shape[1])
    bukti.append("Semua sel kode dieksekusi tanpa error; enam kombinasi evaluasi XGBoost versi 2 lengkap dan ukuran data sesuai fondasi.")

    hasil = AKAR / "hasil" / "hasil_validasi_xgboost.json"
    hasil.write_text(json.dumps({"status": "lolos", "pemeriksaan": bukti}, ensure_ascii=False, indent=2), encoding="utf-8")
    print("\n".join(bukti))


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    utama()
