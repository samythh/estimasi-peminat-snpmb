"""Jalankan notebook XGBoost versi 2 yang menilai lewat latih_dan_prediksi()."""
import sys
from pathlib import Path

import nbformat
from nbclient import NotebookClient

AKAR = Path(__file__).resolve().parents[1]

if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    lokasi = AKAR / "notebooks" / "03_xgboost.ipynb"
    notebook = nbformat.read(lokasi, as_version=4)
    sel_evaluasi = ["".join(sel.source) for sel in notebook.cells
                    if sel.cell_type == "code" and "# === JANGAN DIUBAH ===" in sel.source]
    if len(sel_evaluasi) != 3 or "latih_dan_prediksi(" not in sel_evaluasi[1]:
        raise RuntimeError("Notebook tidak memakai sel evaluasi template versi 2. Salin ulang tiga sel JANGAN DIUBAH.")
    klien = NotebookClient(notebook, timeout=1800, kernel_name="python3", resources={"metadata": {"path": str(AKAR)}})
    klien.km = klien.create_kernel_manager()
    # Pakai interpreter yang menjalankan skrip, bukan kernel global pengguna.
    klien.km.kernel_spec.argv = [sys.executable, "-m", "ipykernel_launcher", "-f", "{connection_file}"]
    klien.execute()
    nbformat.write(notebook, lokasi)
    print(f"Notebook selesai: {lokasi.relative_to(AKAR)}")
    for sel in notebook.cells:
        for keluaran in sel.get("outputs", []):
            if keluaran.output_type == "stream":
                print(keluaran.text)
