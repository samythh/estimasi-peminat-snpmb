"""
Pengambilan & penyiapan data daya tampung / peminat SNPMB untuk DUA jalur:
SNBP (proxy *-sn.php) dan SNBT (proxy *-sb.php).

Alur:
  1. Untuk tiap jalur: ambil daftar PTN, cetak strukturnya, cari id_ptn
     Universitas Andalas via pencocokan nama (bukan hardcode).
  2. Tarik prodi untuk SEMUA PTN, jeda 1 detik antar request, error ditangani
     per-PTN sehingga satu kegagalan tidak menghentikan loop.
  3. Simpan respons MENTAH per jalur SEBELUM diolah:
       SNBP -> data/mentah/mentah_snbp.json
       SNBT -> data/mentah/mentah_snbt.json   (termasuk history_peminat_provinsi utuh)
     Bila file mentah sudah ada, skrip MEMAKAI ULANG file itu dan melewati
     jaringan -- itulah gunanya menyimpan mentah. Paksa unduh ulang dengan
     argumen --paksa-unduh [SNBP|SNBT|semua].
  4. Ratakan ke format panjang (satu baris = satu prodi pada satu tahun pada
     satu jalur), tambahkan fitur lag & agregat, simpan ke CSV.

CATATAN KEBOCORAN DATA (penting untuk tahap modelling):
  Yang HANYA diketahui setelah pendaftaran/seleksi tahun berjalan tidak boleh
  jadi prediktor. Itu mencakup `terima`, keketatan tahun berjalan, DAN tiga
  turunan baru di bawah ini pada tahun berjalannya sendiri:
    - total_peminat_ptn      (ikut memuat peminat prodi itu sendiri)
    - proporsi_peminat_lokal (turunan komposisi pendaftar yang sudah terjadi)
    - jumlah_provinsi_asal   (idem)
  Ketiganya boleh disimpan dan dipakai sebagai deskriptif atau setelah di-lag,
  tidak boleh masuk fitur tahun berjalan. Lihat FITUR_AMAN / FITUR_TERLARANG.

CATATAN JALUR:
  Peminat SNBP dan SNBT TIDAK PERNAH dijumlahkan. Satu orang bisa mendaftar di
  kedua jalur untuk prodi yang sama, jadi penjumlahan akan menghitung ganda.
  Semua agregat dan fitur lag dihitung per (id_prodi, jalur).
"""

import json
import re
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd
import requests

# Satu sumber kebenaran untuk pemetaan bidang: dipanggil di sini supaya panel
# yang dibangun ulang selalu memuat kelompok_bidang & is_fakultas.
from fitur_kelompok_bidang import bangun as tambah_kelompok_bidang

# --------------------------------------------------------------------------
# Konfigurasi
# --------------------------------------------------------------------------
AKAR = Path(__file__).resolve().parents[1]
DIR_DATA = AKAR / "data"

JALUR = {
    "SNBP": {
        "url_ptn": "https://snpmb.id/proxy-ptn-sn.php",
        "url_prodi": "https://snpmb.id/proxy-prodi-sn.php?ptn={id_ptn}",
        "referer": "https://snpmb.id/snbp/daya-tampung-snbp",
        "file_mentah": DIR_DATA / "mentah" / "mentah_snbp.json",
    },
    "SNBT": {
        "url_ptn": "https://snpmb.id/proxy-ptn-sb.php",
        "url_prodi": "https://snpmb.id/proxy-prodi-sb.php?ptn={id_ptn}",
        "referer": "https://snpmb.id/utbk-snbt/daya-tampung-snbt",
        "file_mentah": DIR_DATA / "mentah" / "mentah_snbt.json",
    },
}

USER_AGENT = "Mozilla/5.0"
JEDA_DETIK = 1.0          # jeda antar request -- jangan dihilangkan
PERCOBAAN_MAKS = 3        # percobaan per PTN sebelum dianggap gagal
TIMEOUT = 60

FILE_PANEL = DIR_DATA / "olahan" / "snpmb_panel.csv"
FILE_UNAND = DIR_DATA / "contoh_unand" / "unand_panel.csv"
FILE_PROVINSI = DIR_DATA / "olahan" / "peminat_provinsi_snbt.csv"

TARGET_PTN = "UNIVERSITAS ANDALAS"

# Nama field daya tampung tahun berjalan berbeda per jalur; tidak di-hardcode
# ke salah satu, kedua nama dicoba lalu pola umumnya sebagai jaring pengaman.
FIELD_DAYA_TAMPUNG = ("daya_tampung_snbp", "daya_tampung_snbt")

KOLOM_PANEL = [
    "id_ptn", "ptn_nama", "jalur",
    "id_prodi", "kode_prodi", "prodi", "jenjang", "portofolio",
    "kelompok_bidang", "is_fakultas", "is_new",
    "daya_tampung_kini",
    "tahun", "daya_tampung", "peminat", "terima",
    "peminat_lag1", "peminat_lag2", "daya_tampung_lag1", "terima_lag1",
    "jumlah_prodi_ptn", "total_peminat_ptn",
    "proporsi_peminat_lokal", "jumlah_provinsi_asal",
]

TARGET = "peminat"

# Sumber kebenaran status fitur: docs/KAMUS_DATA.md. Daftar di sini hanya
# untuk ringkasan cetak. daya_tampung_kini & is_new sengaja tidak dicantumkan
# (lihat T-01, T-02 di docs/KEPUTUSAN_METODOLOGI.md).
FITUR_AMAN = [
    "peminat_lag1", "peminat_lag2", "daya_tampung_lag1", "jumlah_prodi_ptn",
    "jenjang", "portofolio", "kelompok_bidang", "jalur",
]

FITUR_TERLARANG = [
    "terima", "total_peminat_ptn", "terima_lag1",
    "proporsi_peminat_lokal", "jumlah_provinsi_asal",
]

KOLOM_INT = [
    "daya_tampung_kini", "tahun", "daya_tampung", "peminat", "terima",
    "peminat_lag1", "peminat_lag2", "daya_tampung_lag1", "terima_lag1",
    "jumlah_prodi_ptn", "total_peminat_ptn", "jumlah_provinsi_asal",
]


# --------------------------------------------------------------------------
# Util
# --------------------------------------------------------------------------
def normalkan(teks):
    """Rapikan nama untuk pencocokan: huruf besar, spasi tunggal."""
    return re.sub(r"\s+", " ", str(teks or "")).strip().upper()


# Daftar PTN dan history_peminat_provinsi memakai penamaan provinsi berbeda.
# Hanya padanan yang benar-benar merujuk wilayah sama yang dipetakan.
# "Papua Selatan" SENGAJA tidak dipetakan ke "Papua": provinsi itu baru
# dimekarkan 2022 dan data peminat masih memakai "Papua" gabungan, sehingga
# memetakannya akan menggelembungkan proporsi peminat lokal. Dibiarkan kosong.
ALIAS_PROVINSI = {
    "JAKARTA RAYA": "DKI JAKARTA",
    "YOGYAKARTA": "DI YOGYAKARTA",
}


def normalkan_prov(teks):
    norm = normalkan(teks)
    return ALIAS_PROVINSI.get(norm, norm)


def ke_int(nilai):
    """Konversi ke int. Nilai kosong/tidak valid -> None (dibiarkan kosong)."""
    if nilai is None:
        return None
    teks = str(nilai).strip()
    if teks == "" or teks.lower() in {"none", "null", "-"}:
        return None
    try:
        return int(float(teks))
    except (TypeError, ValueError):
        return None


def daya_tampung_kini(prodi):
    """Ambil daya tampung tahun berjalan tanpa mengunci pada satu nama field."""
    for field in FIELD_DAYA_TAMPUNG:
        if field in prodi:
            return ke_int(prodi.get(field))
    for kunci, nilai in prodi.items():
        if kunci.startswith("daya_tampung") and not kunci.startswith("history"):
            return ke_int(nilai)
    return None


def ambil_json(sesi, url, referer, label):
    """GET + parse JSON dengan percobaan ulang. Melempar exception bila gagal total."""
    headers = {"User-Agent": USER_AGENT, "Referer": referer}
    galat_terakhir = None
    for percobaan in range(1, PERCOBAAN_MAKS + 1):
        try:
            resp = sesi.get(url, headers=headers, timeout=TIMEOUT)
            resp.raise_for_status()
            return resp.json()
        except Exception as exc:  # noqa: BLE001 - sengaja luas, dicatat pemanggil
            galat_terakhir = exc
            if percobaan < PERCOBAAN_MAKS:
                print(f"    ! {label}: percobaan {percobaan} gagal ({exc}), ulangi...")
                time.sleep(JEDA_DETIK * percobaan)
    raise RuntimeError(f"{type(galat_terakhir).__name__}: {galat_terakhir}")


# --------------------------------------------------------------------------
# Pengambilan (dipakai kedua jalur - tidak ada duplikasi per jalur)
# --------------------------------------------------------------------------
def ambil_daftar_ptn(sesi, nama_jalur):
    cfg = JALUR[nama_jalur]
    print(f"\n[{nama_jalur}] Ambil daftar PTN - {cfg['url_ptn']}")
    data = ambil_json(sesi, cfg["url_ptn"], cfg["referer"], f"daftar PTN {nama_jalur}")

    print(f"  tipe respons : {type(data).__name__}")
    if not isinstance(data, list):
        raise SystemExit(
            f"Respons PTN {nama_jalur} bertipe {type(data).__name__}, bukan list."
        )
    print(f"  jumlah PTN   : {len(data)}")
    print(f"  kunci per PTN: {list(data[0].keys())}")
    return data


def cari_ptn(daftar_ptn, target, nama_jalur):
    """Cari PTN berdasarkan nama (bukan hardcode id)."""
    target_norm = normalkan(target)
    persis = [p for p in daftar_ptn if normalkan(p.get("nama")) == target_norm]
    if persis:
        cocok = persis
    else:
        kata_kunci = target_norm.split()[-1]
        cocok = [p for p in daftar_ptn if kata_kunci in normalkan(p.get("nama"))]
    if not cocok:
        raise SystemExit(f"PTN '{target}' tidak ada di daftar {nama_jalur}.")
    print(f"  '{target}' -> id_ptn={cocok[0].get('id_ptn')} "
          f"({len(cocok)} kecocokan)")
    return cocok[0]


def tarik_semua_prodi(sesi, nama_jalur, daftar_ptn):
    cfg = JALUR[nama_jalur]
    total = len(daftar_ptn)
    print(f"\n[{nama_jalur}] Tarik prodi untuk {total} PTN (jeda {JEDA_DETIK}s)")

    prodi_per_ptn = {}
    ptn_gagal = []

    for i, ptn in enumerate(daftar_ptn, 1):
        id_ptn = ptn.get("id_ptn")
        nama_ptn = str(ptn.get("nama"))
        try:
            prodi = ambil_json(sesi, cfg["url_prodi"].format(id_ptn=id_ptn),
                               cfg["referer"], f"{nama_jalur} PTN {id_ptn}")
            if not isinstance(prodi, list):
                raise TypeError(
                    f"respons prodi bertipe {type(prodi).__name__}, bukan list"
                )
            prodi_per_ptn[str(id_ptn)] = prodi
            print(f"  [{i:>3}/{total}] id_ptn={id_ptn:<5} {nama_ptn[:42]:<42} "
                  f"{len(prodi):>4} prodi")
        except Exception as exc:  # noqa: BLE001 - satu kegagalan tak menghentikan loop
            ptn_gagal.append({"id_ptn": id_ptn, "nama": nama_ptn, "galat": str(exc)})
            print(f"  [{i:>3}/{total}] id_ptn={id_ptn:<5} {nama_ptn[:42]:<42} "
                  f"GAGAL: {exc}")
        finally:
            time.sleep(JEDA_DETIK)

    return prodi_per_ptn, ptn_gagal


def muat_atau_unduh(sesi, nama_jalur, paksa):
    """Pakai ulang file mentah bila ada; kalau tidak, unduh lalu simpan mentah."""
    cfg = JALUR[nama_jalur]
    berkas = cfg["file_mentah"]

    if berkas.exists() and not paksa:
        mb = berkas.stat().st_size / 1_048_576
        print(f"\n[{nama_jalur}] Pakai ulang mentah: {berkas} ({mb:.1f} MB) "
              f"- lewati jaringan (--paksa-unduh untuk unduh ulang)")
        return json.loads(berkas.read_text(encoding="utf-8"))

    print("\n" + "=" * 78)
    print(f"UNDUH JALUR {nama_jalur}")
    print("=" * 78)
    daftar_ptn = ambil_daftar_ptn(sesi, nama_jalur)
    ptn_target = cari_ptn(daftar_ptn, TARGET_PTN, nama_jalur)
    time.sleep(JEDA_DETIK)

    prodi_per_ptn, ptn_gagal = tarik_semua_prodi(sesi, nama_jalur, daftar_ptn)

    # Simpan MENTAH lebih dulu, sebelum pengolahan apa pun.
    mentah = {
        "jalur": nama_jalur,
        "diambil_pada": datetime.now(timezone.utc).isoformat(),
        "sumber": {"ptn": cfg["url_ptn"], "prodi": cfg["url_prodi"],
                   "referer": cfg["referer"]},
        "id_ptn_unand": ptn_target.get("id_ptn"),
        "ptn": daftar_ptn,
        "prodi_per_ptn": prodi_per_ptn,
        "ptn_gagal": ptn_gagal,
    }
    berkas.write_text(json.dumps(mentah, ensure_ascii=False), encoding="utf-8")
    mb = berkas.stat().st_size / 1_048_576
    print(f"\n[{nama_jalur}] [simpan mentah] {berkas} ({mb:.1f} MB)")
    return mentah


# --------------------------------------------------------------------------
# Perataan
# --------------------------------------------------------------------------
def ratakan(nama_jalur, mentah):
    """Satu baris = satu prodi pada satu tahun pada satu jalur.

    Prodi tanpa riwayat (umumnya is_new == 1) tetap diberi SATU baris dengan
    tahun & metrik historis kosong, supaya prodi baru tidak lenyap. Tidak ada
    nilai isian: yang tidak diketahui dibiarkan kosong.
    """
    nama_ptn = {str(p.get("id_ptn")): p.get("nama") for p in mentah["ptn"]}
    baris = []

    for id_ptn, daftar_prodi in mentah["prodi_per_ptn"].items():
        for prodi in daftar_prodi:
            id_ptn_prodi = ke_int(prodi.get("id_ptn")) or ke_int(id_ptn)
            dasar = {
                "id_ptn": id_ptn_prodi,
                "ptn_nama": nama_ptn.get(str(id_ptn_prodi)) or nama_ptn.get(str(id_ptn)),
                "jalur": nama_jalur,
                "id_prodi": ke_int(prodi.get("id_prodi")),
                "kode_prodi": ke_int(prodi.get("kode_prodi")),
                "prodi": prodi.get("nama"),
                "jenjang": prodi.get("jenjang"),
                "portofolio": prodi.get("nama_portofolio"),
                "is_new": ke_int(prodi.get("is_new")),
                "daya_tampung_kini": daya_tampung_kini(prodi),
            }

            riwayat = prodi.get("history_daya_tampung") or []
            if not riwayat:
                baris.append({**dasar, "tahun": None, "daya_tampung": None,
                              "peminat": None, "terima": None})
                continue

            for h in riwayat:
                baris.append({
                    **dasar,
                    "tahun": ke_int(h.get("tahun")),
                    "daya_tampung": ke_int(h.get("daya_tampung")),
                    "peminat": ke_int(h.get("peminat")),
                    "terima": ke_int(h.get("terima")),
                })

    return pd.DataFrame(baris)


def ratakan_provinsi(mentah):
    """Satu baris = prodi x tahun x provinsi asal (khusus SNBT)."""
    nama_ptn = {str(p.get("id_ptn")): p.get("nama") for p in mentah["ptn"]}
    baris = []

    for id_ptn, daftar_prodi in mentah["prodi_per_ptn"].items():
        for prodi in daftar_prodi:
            id_ptn_prodi = ke_int(prodi.get("id_ptn")) or ke_int(id_ptn)
            for p in prodi.get("history_peminat_provinsi") or []:
                baris.append({
                    "id_ptn": id_ptn_prodi,
                    "ptn_nama": nama_ptn.get(str(id_ptn_prodi)),
                    "id_prodi": ke_int(prodi.get("id_prodi")),
                    "prodi": prodi.get("nama"),
                    "jenjang": prodi.get("jenjang"),
                    "tahun": ke_int(p.get("tahun")),
                    "kode_prov": str(p.get("kode_prov")) if p.get("kode_prov") else None,
                    "nama_prov": p.get("nama_prov"),
                    "jml_peminat": ke_int(p.get("jml_peminat")),
                })

    return pd.DataFrame(baris)


def provinsi_ptn(mentah):
    """Peta id_ptn -> nama provinsi kedudukan PTN, dari daftar PTN."""
    peta = {}
    for p in mentah["ptn"]:
        prov = p.get("provinsi") or []
        if prov and prov[0].get("nama_prov1"):
            peta[ke_int(p.get("id_ptn"))] = prov[0]["nama_prov1"]
    return peta


# --------------------------------------------------------------------------
# Fitur turunan
# --------------------------------------------------------------------------
def tambah_lag(df):
    """Fitur lag lewat self-merge pada (id_prodi, jalur, tahun-1) dan tahun-2.

    Dicocokkan pada NILAI TAHUN, bukan shift() posisi: kalau baris tahun
    sebelumnya memang tidak ada, lag-nya NaN -- bukan mengambil baris terdekat.
    Kunci menyertakan `jalur` karena deret peminat SNBP dan SNBT terpisah.
    """
    kunci = ["id_prodi", "jalur", "tahun"]
    df = df.sort_values(kunci, na_position="last").reset_index(drop=True)
    hist = df[df["tahun"].notna()]

    sumber = hist[kunci + ["peminat", "daya_tampung", "terima"]]

    lag1 = sumber.rename(columns={
        "peminat": "peminat_lag1",
        "daya_tampung": "daya_tampung_lag1",
        "terima": "terima_lag1",
    }).copy()
    lag1["tahun"] = lag1["tahun"] + 1

    lag2 = sumber[kunci + ["peminat"]].rename(
        columns={"peminat": "peminat_lag2"}).copy()
    lag2["tahun"] = lag2["tahun"] + 2

    df = df.merge(lag1, on=kunci, how="left")
    df = df.merge(lag2, on=kunci, how="left")
    return df


def tambah_agregat_ptn(df):
    """jumlah_prodi_ptn & total_peminat_ptn per (PTN, jalur, tahun).

    Dihitung per jalur -- peminat SNBP dan SNBT tidak pernah dijumlahkan.
    """
    hist = df[df["tahun"].notna()]
    agg = (hist.groupby(["id_ptn", "jalur", "tahun"])
                .agg(jumlah_prodi_ptn=("id_prodi", "nunique"),
                     total_peminat_ptn=("peminat", "sum"))
                .reset_index())
    return df.merge(agg, on=["id_ptn", "jalur", "tahun"], how="left")


def tambah_fitur_provinsi(df, df_prov, peta_prov):
    """proporsi_peminat_lokal & jumlah_provinsi_asal - hanya terisi untuk SNBT.

    'Lokal' = provinsi kedudukan PTN, dicocokkan lewat NAMA provinsi karena
    kode provinsi pada daftar PTN dan pada history_peminat_provinsi memakai
    skema berbeda. PTN yang nama provinsinya tidak ketemu dibiarkan kosong dan
    dilaporkan -- tidak diisi nilai tebakan.
    """
    df["proporsi_peminat_lokal"] = pd.NA
    df["jumlah_provinsi_asal"] = pd.NA
    if df_prov.empty:
        return df, []

    prov = df_prov.copy()
    prov["prov_norm"] = prov["nama_prov"].map(normalkan_prov)

    jumlah = (prov.groupby(["id_prodi", "tahun"])["nama_prov"]
                  .nunique().rename("jumlah_provinsi_asal_baru").reset_index())

    prov["prov_ptn_norm"] = prov["id_ptn"].map(
        lambda i: normalkan_prov(peta_prov.get(i)) if peta_prov.get(i) else None)
    lokal = (prov[prov["prov_norm"] == prov["prov_ptn_norm"]]
             .groupby(["id_prodi", "tahun"])["jml_peminat"]
             .sum().rename("peminat_lokal").reset_index())

    # PTN yang nama provinsinya tidak pernah cocok dengan satu pun baris
    # provinsi miliknya sendiri -> pemetaan gagal, bukan "nol peminat lokal".
    cocok_per_ptn = prov.groupby("id_ptn").apply(
        lambda g: bool((g["prov_norm"] == g["prov_ptn_norm"]).any()),
        include_groups=False)
    ptn_tak_cocok = sorted(
        {int(i) for i, ok in cocok_per_ptn.items() if not ok})

    df = df.merge(jumlah, on=["id_prodi", "tahun"], how="left")
    df = df.merge(lokal, on=["id_prodi", "tahun"], how="left")

    snbt = df["jalur"] == "SNBT"
    df.loc[snbt, "jumlah_provinsi_asal"] = df.loc[snbt, "jumlah_provinsi_asal_baru"]

    bisa = snbt & df["peminat"].notna() & (df["peminat"] > 0) & \
        df["peminat_lokal"].notna() & ~df["id_ptn"].isin(ptn_tak_cocok)
    df.loc[bisa, "proporsi_peminat_lokal"] = (
        df.loc[bisa, "peminat_lokal"] / df.loc[bisa, "peminat"]).round(4)

    df = df.drop(columns=["jumlah_provinsi_asal_baru", "peminat_lokal"])
    return df, ptn_tak_cocok


def rapikan_tipe(df):
    for kolom in KOLOM_INT:
        if kolom in df.columns:
            df[kolom] = pd.to_numeric(df[kolom], errors="coerce").astype("Int64")
    df["proporsi_peminat_lokal"] = pd.to_numeric(
        df["proporsi_peminat_lokal"], errors="coerce")
    return df.reindex(columns=KOLOM_PANEL)


def tahun_bolong(df):
    """Prodi yang riwayat tahunnya tidak berurutan, per jalur."""
    hist = df[df["tahun"].notna()]
    hasil = {}
    for jalur, g in hist.groupby("jalur"):
        per_prodi = g.groupby("id_prodi")["tahun"].agg(["min", "max", "nunique"])
        bolong = per_prodi[(per_prodi["max"] - per_prodi["min"] + 1)
                           != per_prodi["nunique"]]
        hasil[jalur] = (len(bolong), int(per_prodi.shape[0]),
                        sorted(bolong.index.tolist()))
    return hasil


# --------------------------------------------------------------------------
# Ringkasan
# --------------------------------------------------------------------------
def cetak_ringkasan(df, df_unand, df_prov, mentah, ptn_tak_cocok, id_unand):
    print("\n" + "=" * 78)
    print("RINGKASAN")
    print("=" * 78)

    print(f"{'jalur':<8} {'PTN':>5} {'prodi':>7} {'baris':>8} "
          f"{'baris bertahun':>15} {'tanpa riwayat':>14} {'PTN gagal':>10}")
    for jalur in JALUR:
        g = df[df["jalur"] == jalur]
        gagal = len(mentah[jalur]["ptn_gagal"])
        print(f"{jalur:<8} {g['id_ptn'].nunique():>5} {g['id_prodi'].nunique():>7} "
              f"{len(g):>8} {int(g['tahun'].notna().sum()):>15} "
              f"{int(g['tahun'].isna().sum()):>14} {gagal:>10}")
    print(f"{'TOTAL':<8} {df['id_ptn'].nunique():>5} "
          f"{df['id_prodi'].nunique():>7} {len(df):>8}")

    print("\nPerbandingan dengan panel SNBP sebelumnya (21.668 baris):")
    n_snbp = len(df[df["jalur"] == "SNBP"])
    selisih = n_snbp - 21668
    status = "sama" if selisih == 0 else f"selisih {selisih:+d}"
    print(f"  baris SNBP sekarang: {n_snbp}  ({status})")

    print("\nPTN gagal ditarik:")
    for jalur in JALUR:
        gagal = mentah[jalur]["ptn_gagal"]
        if not gagal:
            print(f"  {jalur}: tidak ada")
        for g in gagal:
            print(f"  {jalur}: id_ptn={g['id_ptn']} {g['nama']} -> {g['galat']}")

    print("\nSebaran baris per tahun per jalur:")
    tab = (df.assign(thn=df["tahun"].astype("Int64").astype(str)
                     .replace("<NA>", "(tanpa riwayat)"))
             .pivot_table(index="thn", columns="jalur", values="id_prodi",
                          aggfunc="size", fill_value=0))
    print(tab.to_string())

    print("\nIrisan prodi antar jalur (berdasarkan id_prodi):")
    set_snbp = set(df[df["jalur"] == "SNBP"]["id_prodi"].dropna())
    set_snbt = set(df[df["jalur"] == "SNBT"]["id_prodi"].dropna())
    print(f"  di kedua jalur     : {len(set_snbp & set_snbt)}")
    print(f"  hanya SNBP         : {len(set_snbp - set_snbt)}")
    print(f"  hanya SNBT         : {len(set_snbt - set_snbp)}")
    print(f"  gabungan           : {len(set_snbp | set_snbt)}")

    print("\nProdi dengan tahun bolong (riwayat tidak berurutan):")
    for jalur, (n_bolong, n_total, contoh) in tahun_bolong(df).items():
        persen = n_bolong / n_total * 100 if n_total else 0
        print(f"  {jalur}: {n_bolong} dari {n_total} prodi berriwayat ({persen:.2f}%)")
        if contoh:
            print(f"    id_prodi: {contoh[:15]}{' ...' if len(contoh) > 15 else ''}")

    print(f"\nFile provinsi SNBT: {len(df_prov)} baris "
          f"(prodi x tahun x provinsi asal)")
    if not df_prov.empty:
        terisi = df[df["jalur"] == "SNBT"]["proporsi_peminat_lokal"].notna().sum()
        total_snbt = int((df["jalur"] == "SNBT").sum())
        print(f"  proporsi_peminat_lokal terisi: {terisi} dari {total_snbt} baris SNBT")
        print(f"  PTN gagal dipetakan provinsinya: {len(ptn_tak_cocok)}"
              f"{' -> ' + str(ptn_tak_cocok[:10]) if ptn_tak_cocok else ''}")

    print(f"\nUnand (id_ptn={id_unand}):")
    for jalur in JALUR:
        g = df_unand[df_unand["jalur"] == jalur]
        print(f"  {jalur}: {g['id_prodi'].nunique()} prodi, {len(g)} baris")

    print("\nProdi Unand is_new == 1 per jalur:")
    for jalur in JALUR:
        baru = (df_unand[(df_unand["jalur"] == jalur) & (df_unand["is_new"] == 1)]
                .drop_duplicates("id_prodi").sort_values("prodi"))
        print(f"  {jalur}: {len(baru)}")
        for _, r in baru.iterrows():
            dt = "" if pd.isna(r["daya_tampung_kini"]) else int(r["daya_tampung_kini"])
            print(f"    {str(r['kode_prodi']):<12} {str(r['jenjang']):<4} "
                  f"dt={str(dt):>5}  {r['prodi']}")

    print("\nCatatan anti-kebocoran:")
    print(f"  target          : {TARGET}")
    print(f"  fitur aman      : {', '.join(FITUR_AMAN)}")
    print(f"  DILARANG (tahun berjalan): {', '.join(FITUR_TERLARANG)}")
    print("  peminat SNBP dan SNBT tidak pernah dijumlahkan (risiko hitung ganda)")


# --------------------------------------------------------------------------
def main():
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:  # noqa: BLE001
        pass

    arg = " ".join(sys.argv[1:]).upper()
    paksa = {j: ("--PAKSA-UNDUH" in arg and (j in arg or "SEMUA" in arg))
             for j in JALUR}

    for folder in ("mentah", "olahan", "contoh_unand"):
        (DIR_DATA / folder).mkdir(parents=True, exist_ok=True)
    sesi = requests.Session()

    mentah = {j: muat_atau_unduh(sesi, j, paksa[j]) for j in JALUR}

    print("\n" + "=" * 78)
    print("PERATAAN + FITUR")
    print("=" * 78)

    df = pd.concat([ratakan(j, mentah[j]) for j in JALUR], ignore_index=True)

    df_prov = ratakan_provinsi(mentah["SNBT"])
    peta_prov = provinsi_ptn(mentah["SNBT"])

    df = tambah_lag(df)
    df = tambah_agregat_ptn(df)
    df, ptn_tak_cocok = tambah_fitur_provinsi(df, df_prov, peta_prov)
    df = tambah_kelompok_bidang(df)
    df = rapikan_tipe(df)
    df = df.sort_values(["jalur", "id_ptn", "id_prodi", "tahun"],
                        na_position="last").reset_index(drop=True)

    id_unand = mentah["SNBP"]["id_ptn_unand"]
    df_unand = df[df["id_ptn"] == id_unand].reset_index(drop=True)

    df.to_csv(FILE_PANEL, index=False, encoding="utf-8-sig")
    df_unand.to_csv(FILE_UNAND, index=False, encoding="utf-8-sig")
    if not df_prov.empty:
        df_prov.sort_values(["id_ptn", "id_prodi", "tahun", "nama_prov"]) \
               .to_csv(FILE_PROVINSI, index=False, encoding="utf-8-sig")

    print(f"[simpan] {FILE_PANEL}  ({len(df)} baris)")
    print(f"[simpan] {FILE_UNAND}  ({len(df_unand)} baris)")
    print(f"[simpan] {FILE_PROVINSI}  ({len(df_prov)} baris)")

    cetak_ringkasan(df, df_unand, df_prov, mentah, ptn_tak_cocok, id_unand)


if __name__ == "__main__":
    main()
