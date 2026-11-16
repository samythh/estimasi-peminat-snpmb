"""
Fitur berbasis kesamaan nama program studi (K-20).

1. `prodi_normal`: nama prodi yang sudah diseragamkan supaya prodi yang sama di
   PTN berbeda punya nama yang sama.
   Contoh: INFORMATIKA / TEKNIK INFORMATIKA / ILMU KOMPUTER -> INFORMATIKA.
2. tambah_fitur_sejenis(): tiga fitur t-1 berbasis prodi sejenis, dipanggil oleh
   fondasi.py. Tidak ditulis ke panel.

    python src/fitur_prodi_sejenis.py          # mode tinjau pemetaan nama
    python src/fitur_prodi_sejenis.py --uji    # uji fitur sejenis vs hitung manual

--------------------------------------------------------------------------
URUTAN NORMALISASI (normalkan_prodi)
--------------------------------------------------------------------------
 0. PETA_MENTAH   -- segelintir nama yang isi kurungnya justru nama prodinya,
                     mis. "P. SENI DRAMA, TARI & MUSIK (P. SENI TARI)".
 1. Dasar         -- huruf besar, isi tanda kurung dibuang (penanda kampus,
                     NK, kelas internasional, singkatan nama).
 2. Singkatan     -- EJAAN_TAMBAHAN di sini, lalu normalkan() dari
                     fitur_kelompok_bidang (PEND., PGSD, PPKN, ADM., salah ketik).
 3. Penanda       -- kampus/lokasi (PSDKU, KAMPUS, K. KAB), kelas
                     internasional, bilingual, akhiran S1.
 4. Ejaan         -- SUMBERDAYA -> SUMBER DAYA, BUDI DAYA -> BUDIDAYA, dst.
 5. Awalan ILMU   -- "ILMU X" -> "X" (ILMU HUKUM -> HUKUM), kecuali "ILMU DAN ..."
                     dan nama di ILMU_DIPERTAHANKAN.
 6. PETA_SINONIM  -- padanan yang tidak tertangkap aturan umum, dicocokkan
                     pada nama PERSIS hasil langkah 1-5.
"""

import re
import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
from fitur_kelompok_bidang import normalkan as normalkan_ejaan  # noqa: E402

AKAR = Path(__file__).resolve().parents[1]
FILE_PANEL = AKAR / "data" / "olahan" / "snpmb_panel.csv"
BENIH = 42

# 0. Nama mentah (huruf besar, spasi dirapikan) yang ditangani khusus karena
#    isi kurungnya adalah nama prodi yang sebenarnya, atau singkatannya
#    disalahartikan oleh aturan umum (KOM di sini = komputer, bukan komunikasi).
PETA_MENTAH = {
    "P. SENI DRAMA, TARI & MUSIK (P. SENI TARI)": "PENDIDIKAN SENI TARI",
    "P. SENI DRAMA, TARI & MUSIK (P. SENI MUSIK)": "PENDIDIKAN SENI MUSIK",
    "ILMU SOSIAL EKONOMI PERTANIAN (AGRIBISNIS)": "AGRIBISNIS",
    "PEND. INF./KOM": "PENDIDIKAN INFORMATIKA",
}

# 2. Singkatan khusus nama prodi, diterapkan SEBELUM normalkan_ejaan().
EJAAN_TAMBAHAN = [
    (r"^P\.?\s+(?=GURU|SENI)", "PENDIDIKAN "),       # P. GURU ..., P. SENI ...
    (r"\bSEK\b\.?", "SEKOLAH"),                        # P. GURU SEK DASAR
    (r"\bSIST\b\.?", "SISTEM"),                        # TEK. SIST PERKAPALAN
    (r"\bKLS\b\.?", "KELAS"),
    (r"\bINTERNAS\b\.?", "INTERNASIONAL"),
    (r"\bIPA\b", "ILMU PENGETAHUAN ALAM"),
    (r"\bIPS\b", "ILMU PENGETAHUAN SOSIAL"),
    (r"^(PEND\.?|PENDIDIKAN)\s+B\.?\s+(?=INGGRIS)", "PENDIDIKAN BAHASA "),
    (r"\bKES\b\.?\s*REK\b\.?", "KESEHATAN DAN REKREASI"),   # PEND. JASMANI KES REK
    (r"\bOR$", "OLAHRAGA"),                            # PEND. KEPELATIHAN OR
]

# 3. Penanda kampus, lokasi, dan kelas. Dibuang beserta sisa nama sesudahnya.
POLA_PENANDA = [
    r"^PSDKU\s+",                                      # awalan: PSDKU MANAJEMEN ...
    r"\s*-?\s*\b(PSDKU|PDSKU|KAMPUS|KAMP)\b.*$",       # ... KAMPUS BONDOWOSO
    r"\s+K\s+KAB\b.*$",                                # ... K. KAB. KAPUAS HULU
    r"\s+KAB(UPATEN)?\s+\w.*$",                        # sisa lokasi sesudah awalan PSDKU
    r"\s+KELAS\s+INTERNASIONAL\b.*$",
    r"\s+BILINGUAL\b.*$",
    r"\s+S1$",
]

# 4. Ejaan yang berbeda untuk kata yang sama, termasuk salah ketik di sumber.
EJAAN_KATA = [
    (r"-", " "),
    (r"/", " "),
    (r"\bSUMBERDAYA\b", "SUMBER DAYA"),
    (r"\bBUDI DAYA\b", "BUDIDAYA"),
    (r"\bSENIRUPA\b", "SENI RUPA"),
    (r"\bAGRO INDUSTRI\b", "AGROINDUSTRI"),
    (r"\bAGROBISNIS\b", "AGRIBISNIS"),
    (r"\bGEO FISIKA\b", "GEOFISIKA"),
    (r"\bETNO MUSIKOLOGI\b", "ETNOMUSIKOLOGI"),
    (r"\bNON FORMAL\b", "NONFORMAL"),
    (r"\bPERANCIS\b", "PRANCIS"),
    (r"\bAUTOMASI\b", "OTOMASI"),
    (r"\bBIOMEDIK\b", "BIOMEDIS"),
    (r"\bMEDIK\b", "MEDIS"),
    (r"\bINDO?\b", "INDONESIA"),                       # BAHASA DAN SASTRA INDO / IND
    # salah ketik di data sumber
    (r"\bPENDIDI?KA?AN\b", "PENDIDIKAN"),             # PENDIDKAN, PENDIDIKAAN
    (r"\bPANCASLA\b", "PANCASILA"),
    (r"\bKEWARGANEG\b", "KEWARGANEGARAAN"),
    (r"\bPEBANKAN\b", "PERBANKAN"),
    (r"\bSISTIM\b", "SISTEM"),
    (r"\bREKASAYA\b", "REKAYASA"),
    (r"\bMANA(JA|GE)MEN\b", "MANAJEMEN"),             # MANAJAMEN, MANAGEMEN
    (r"\bPEMBANG(N|U)AN\b", "PEMBANGUNAN"),
    (r"\bSATRA\b", "SASTRA"),
    (r"\bINFRASRUKTUR\b", "INFRASTRUKTUR"),
]

# 5. "ILMU X" yang TIDAK dipotong: hasil potongannya terlalu umum atau berubah arti.
ILMU_DIPERTAHANKAN = {"ILMU PENDIDIKAN"}

# 6a. Padanan pola umum.
POLA_SINONIM = [
    (r"^BAHASA DAN SASTRA (.+)$", r"SASTRA \1"),
    (r"^PENDIDIKAN BAHASA DAN SASTRA (.+)$", r"PENDIDIKAN BAHASA \1"),
]

# 6b. Padanan nama persis (hasil langkah 1-5) -> nama baku. Dikelompokkan
#     menurut dasar keputusannya; prinsip dan keputusan yang diperdebatkan
#     dicatat di docs/KEPUTUSAN_METODOLOGI.md (K-20).
_SINONIM = {
    # -- contoh yang ditetapkan pengguna
    "INFORMATIKA": ["TEKNIK INFORMATIKA", "KOMPUTER"],      # KOMPUTER <- ILMU KOMPUTER
    "KEDOKTERAN": ["PENDIDIKAN DOKTER", "PENDIDIKAN KEDOKTERAN"],
    "AKUAKULTUR": ["BUDIDAYA PERAIRAN", "BUDIDAYA PERIKANAN", "BUDIDAYA IKAN",
                   "TEKNOLOGI AKUAKULTUR", "TEKNOLOGI BUDIDAYA PERIKANAN",
                   "TEKNOLOGI BUDIDAYA IKAN",
                   "TEKNOLOGI BUDIDAYA PERIKANAN TEKNOLOGI AKUAKULTUR",
                   "TEKNOLOGI DAN MANAJEMEN PERIKANAN BUDIDAYA"],
    "PENDIDIKAN JASMANI KESEHATAN DAN REKREASI": [
        "PENDIDIKAN JASMANI KESEHATAN REKREASI",
        "PENDIDIKAN OLAHRAGA DAN KESEHATAN"],
    # -- pola yang sama dengan contoh pengguna
    "KEDOKTERAN GIGI": ["PENDIDIKAN DOKTER GIGI"],
    "KEDOKTERAN HEWAN": ["PENDIDIKAN DOKTER HEWAN"],
    "PENDIDIKAN INFORMATIKA": ["PENDIDIKAN TEKNIK INFORMATIKA", "PENDIDIKAN KOMPUTER",
                               "PENDIDIKAN ILMU KOMPUTER",
                               "PENDIDIKAN TEKNIK INFORMATIKA DAN KOMPUTER",
                               "PENDIDIKAN TEKNOLOGI INFORMATIKA DAN KOMPUTER"],
    # -- PTN sendiri menuliskan kedua nama sebagai satu prodi (bukti dari data)
    "AGROTEKNOLOGI": ["AGROEKOTEKNOLOGI", "AGRONOMI", "AGRONOMI AGROEKOTEKNOLOGI",
                      "AGROTEKNOLOGI AGROEKOTEKNOLOGI", "AGRONOMI DAN HORTIKULTURA"],
    "AGRIBISNIS": ["SOSIAL EKONOMI PERTANIAN AGRIBISNIS"],
    "PENDIDIKAN KHUSUS": ["PENDIDIKAN LUAR BIASA", "PENDIDIKAN LUAR BIASA P KH"],
    "MANAJEMEN SUMBER DAYA PERAIRAN": ["MANAJEMEN SUMBER DAYA AKUATIK"],
    "PERENCANAAN WILAYAH DAN KOTA": ["TEKNIK PERENCANAAN WILAYAH DAN KOTA",
                                     "PERENCANAAN WILAYAH DAN KOTA PLANOLOGI"],
    "ADMINISTRASI BISNIS": ["ADMINISTRASI NIAGA", "ADMINISTRASI NIAGA BISNIS"],
    "MANAJEMEN PEMASARAN": ["MANAJEMEN PEMASARAN MARKETING"],
    # -- perubahan nomenklatur / label berbeda untuk prodi yang sama
    "ADMINISTRASI PUBLIK": ["ADMINISTRASI NEGARA"],
    "ARSITEKTUR": ["TEKNIK ARSITEKTUR"],
    "AKTUARIA": ["SAINS AKTUARIA"],
    "BIOMEDIS": ["SAINS BIOMEDIS"],
    "KEOLAHRAGAAN": ["SAINS KEOLAHRAGAAN"],
    "PERIKANAN": ["SAINS PERIKANAN"],
    "KOMUNIKASI": ["SAINS KOMUNIKASI", "KOMUNIKASI KONST HUMAS",
                   "KOMUNIKASI KONST JURNALISTIK"],
    "LINGKUNGAN": ["SAINS LINGKUNGAN"],
    "SAINS DATA": ["TEKNOLOGI SAINS DATA"],
    "KELAUTAN": ["ILMU DAN TEKNOLOGI KELAUTAN"],
    "PETERNAKAN": ["ILMU DAN INDUSTRI PETERNAKAN"],
    "TEKNOLOGI PANGAN": ["ILMU DAN TEKNOLOGI PANGAN", "TEKNIK PANGAN",
                         "TEKNOLOGI REKAYASA PANGAN"],
    "EKONOMI PEMBANGUNAN": ["EKONOMI DAN STUDI PEMBANGUNAN"],
    "PERPUSTAKAAN": ["PERPUSTAKAAN DAN SAINS INFORMASI",
                     "PERPUSTAKAAN DAN ILMU INFORMASI", "INFORMASI DAN PERPUSTAKAAN"],
    "PENDIDIKAN GURU PENDIDIKAN ANAK USIA DINI": [
        "PENDIDIKAN GURU PAUD", "PENDIDIKAN ANAK USIA DINI",
        "PENDIDIKAN GURU ANAK USIA DINI", "PAUD"],
    "PENDIDIKAN LUAR SEKOLAH": ["PENDIDIKAN NONFORMAL", "PENDIDIKAN MASYARAKAT"],
    "PENDIDIKAN PANCASILA DAN KEWARGANEGARAAN": ["PENDIDIKAN KEWARGANEGARAAN"],
    "PENDIDIKAN JASMANI SEKOLAH DASAR": [
        "PENDIDIKAN GURU SEKOLAH DASAR PENDIDIKAN JASMANI"],
    "PENDIDIKAN GURU SEKOLAH DASAR": ["PENDIDIKAN GURU SD"],
    "PENDIDIKAN SENI DRAMA TARI DAN MUSIK": ["PENDIDIKAN SENDRATASIK"],
    "PENDIDIKAN SENI MUSIK": ["PENDIDIKAN MUSIK"],
    "PENDIDIKAN SENI TARI": ["PENDIDIKAN TARI"],
    "PENDIDIKAN SENI RUPA": ["PENDIDIKAN SENI RUPA DAN KERAJINAN"],
    "SENI MUSIK": ["MUSIK"],
    "SENI TARI": ["TARI"],
    "SENI RUPA": ["SENI RUPA MURNI"],
    # GEOLOGI (ilmu murni) sengaja TIDAK digabung: tidak punya pembanding
    # bukan alasan untuk menyamakan prodi yang berbeda (K-20).
    "TEKNIK GEOLOGI": ["REKAYASA GEOLOGI"],
    "PERHOTELAN": ["MANAJEMEN PERHOTELAN", "PENGELOLAAN PERHOTELAN"],
    "KEUANGAN DAN PERBANKAN": ["PERBANKAN DAN KEUANGAN"],
    "PEMANFAATAN SUMBER DAYA PERIKANAN": ["PEMANFAATAN SUMBER DAYA PERAIRAN"],
    "TEKNOLOGI HASIL PERIKANAN": ["TEKNOLOGI HASIL PERAIRAN", "TEKNIK HASIL PERIKANAN"],
    "TEKNOLOGI HASIL PERTANIAN": ["TEKNIK HASIL PERTANIAN"],
    "TEKNOLOGI INDUSTRI PERTANIAN": ["TEKNIK INDUSTRI PERTANIAN"],
    "KESELAMATAN DAN KESEHATAN KERJA": ["TEKNIK KESELAMATAN DAN KESEHATAN KERJA"],
    "PERANCANGAN JALAN DAN JEMBATAN": ["TEKNIK PERANCANGAN JALAN DAN JEMBATAN"],
    "REKAYASA PERANGKAT LUNAK": ["TEKNIK REKAYASA PERANGKAT LUNAK",
                                 "TEKNOLOGI REKAYASA PERANGKAT LUNAK"],
    # -- vokasi: "TEKNIK X" (nama lama), "TEKNOLOGI X" (D3) dan "TEKNOLOGI
    #    REKAYASA X" (D4) untuk subjek yang sama. Jenjang tetap membedakan
    #    D3/D4/S1. Nama baku = "TEKNIK X" bila ada; tidak pernah ke ilmu murni
    #    (TEKNOLOGI REKAYASA KIMIA -> TEKNIK KIMIA, bukan KIMIA).
    "TEKNIK MESIN": ["TEKNOLOGI MESIN", "TEKNOLOGI REKAYASA MESIN"],
    "TEKNIK SIPIL": ["TEKNOLOGI SIPIL"],
    "TEKNIK LISTRIK": ["TEKNOLOGI LISTRIK"],
    "TEKNIK ELEKTRO": ["TEKNOLOGI REKAYASA ELEKTRO"],
    "TEKNIK KIMIA": ["TEKNOLOGI KIMIA", "TEKNOLOGI REKAYASA KIMIA"],
    "TEKNIK PERTAMBANGAN": ["TEKNOLOGI PERTAMBANGAN"],
    "TEKNIK OTOMOTIF": ["TEKNOLOGI OTOMOTIF", "TEKNOLOGI REKAYASA OTOMOTIF"],
    "TEKNIK ELEKTRONIKA": ["TEKNOLOGI ELEKTRONIKA", "ELEKTRONIKA",
                           "TEKNOLOGI REKAYASA ELEKTRONIKA"],
    "TEKNIK TELEKOMUNIKASI": ["TEKNOLOGI TELEKOMUNIKASI", "TELEKOMUNIKASI"],
    "TEKNIK KONVERSI ENERGI": ["TEKNOLOGI KONVERSI ENERGI",
                               "TEKNOLOGI REKAYASA KONVERSI ENERGI"],
    "TEKNIK MANUFAKTUR": ["TEKNOLOGI MANUFAKTUR", "TEKNOLOGI REKAYASA MANUFAKTUR"],
    "TEKNIK GEOMATIKA": ["TEKNOLOGI GEOMATIKA"],
    "TEKNIK KONSTRUKSI JALAN DAN JEMBATAN": [
        "TEKNOLOGI KONSTRUKSI JALAN DAN JEMBATAN",
        "TEKNOLOGI REKAYASA KONSTRUKSI JALAN DAN JEMBATAN"],
    "TEKNIK KOMPUTER": ["SISTEM KOMPUTER", "TEKNOLOGI REKAYASA KOMPUTER"],
    "TEKNIK MEKATRONIKA": ["TEKNOLOGI REKAYASA MEKATRONIKA"],
    "TEKNIK OTOMASI": ["TEKNOLOGI REKAYASA OTOMASI"],
    "TEKNIK MULTIMEDIA": ["TEKNOLOGI REKAYASA MULTIMEDIA"],
    "TEKNIK ENERGI TERBARUKAN": ["TEKNOLOGI REKAYASA ENERGI TERBARUKAN"],
    "TEKNIK INSTALASI LISTRIK": ["TEKNOLOGI REKAYASA INSTALASI LISTRIK"],
    "TEKNIK INSTRUMENTASI": ["TEKNOLOGI REKAYASA INSTRUMENTASI"],
    "TEKNIK METALURGI": ["TEKNOLOGI REKAYASA METALURGI", "METALURGI"],
    "TEKNIK PEMBANGKIT ENERGI": ["TEKNOLOGI REKAYASA PEMBANGKIT ENERGI"],
    "TEKNIK PENGENDALIAN PENCEMARAN LINGKUNGAN": [
        "TEKNOLOGI REKAYASA PENGENDALIAN PENCEMARAN LINGKUNGAN"],
    "TEKNIK PERMESINAN KAPAL": ["TEKNOLOGI REKAYASA PERMESINAN KAPAL"],
    "TEKNIK KONSTRUKSI PERKAPALAN": ["TEKNOLOGI REKAYASA KONSTRUKSI PERKAPALAN"],
    "TEKNIK PERAWATAN DAN PERBAIKAN MESIN": ["PERAWATAN DAN PERBAIKAN MESIN"],
    "TEKNOLOGI KONSTRUKSI BANGUNAN AIR": ["TEKNOLOGI REKAYASA KONSTRUKSI BANGUNAN AIR"],
    "KONSTRUKSI BANGUNAN GEDUNG": ["TEKNOLOGI REKAYASA KONSTRUKSI BANGUNAN GEDUNG"],
    "TEKNOLOGI KIMIA INDUSTRI": ["TEKNOLOGI REKAYASA KIMIA INDUSTRI", "KIMIA INDUSTRI"],
    "PERANCANGAN MANUFAKTUR": ["TEKNOLOGI REKAYASA PERANCANGAN MANUFAKTUR"],
    "TEKNOLOGI PRODUKSI TANAMAN PANGAN": ["TEKNIK PRODUKSI TANAMAN PANGAN"],
    "TEKNOLOGI PRODUKSI TERNAK": ["PRODUKSI TERNAK"],
    "TEKNIK ALAT BERAT": ["ALAT BERAT", "PEMELIHARAAN ALAT BERAT",
                          "PERAWATAN ALAT BERAT", "TEKNIK MESIN ALAT BERAT",
                          "TEKNIK PENGELOLAAN DAN PERAWATAN ALAT BERAT",
                          "TEKNOLOGI REKAYASA PEMELIHARAAN ALAT BERAT"],
    # -- ejaan / urutan kata / kata penghubung
    "BIMBINGAN DAN KONSELING": ["BIMBINGAN KONSELING",
                                "PENDIDIKAN BIMBINGAN DAN KONSELING"],
    "DESAIN KOMUNIKASI VISUAL": ["DESAIN DAN KOMUNIKASI VISUAL"],
    "PENDIDIKAN SOSIOLOGI DAN ANTROPOLOGI": ["PENDIDIKAN SOSIOLOGI ANTROPOLOGI"],
    "TEKNOLOGI MULTIMEDIA DAN BROADCASTING": ["TEKNOLOGI MULTIMEDIA BROADCASTING"],
    "TEKNIK INFRASTRUKTUR LINGKUNGAN": ["TEKNIK INFRASTRUKTUR DAN LINGKUNGAN"],
    "STATISTIKA": ["STATISTIK"],
    "ANALISIS KIMIA": ["ANALIS KIMIA"],
    "ADMINISTRASI PERPAJAKAN": ["ADMINISTRASI PAJAK"],
    "BUDIDAYA TERNAK": ["BUDIDAYA PETERNAKAN"],
    "TEKNOLOGI PERBENIHAN": ["TEKNOLOGI BENIH"],
    "TEKNOLOGI PEMBENIHAN IKAN": ["TEKNOLOGI DAN MANAJEMEN PEMBENIHAN IKAN"],
    "KESEKRETARIATAN": ["SEKRETARI"],
    "PENDIDIKAN KESEJAHTERAAN KELUARGA": ["PENDIDIKAN KES KEL"],
}
PETA_SINONIM = {lama: baku for baku, daftar in _SINONIM.items()
                for lama in daftar if lama != baku}


def _rapikan(t):
    return re.sub(r"\s+", " ", t).strip()


def bentuk_dasar(nama):
    """Langkah 0-4: pembersihan mekanis (kurung, singkatan, penanda, ejaan)."""
    mentah = _rapikan(str(nama or "").upper())
    if mentah in PETA_MENTAH:
        return PETA_MENTAH[mentah]

    t = re.sub(r"\([^)]*\)?", " ", mentah)             # 1. isi kurung
    for pola, ganti in EJAAN_TAMBAHAN:                   # 2. singkatan
        t = re.sub(pola, ganti, t)
    t = normalkan_ejaan(t)
    for pola in POLA_PENANDA:                            # 3. penanda
        t = re.sub(pola, "", t)
    for pola, ganti in EJAAN_KATA:                       # 4. ejaan
        t = re.sub(pola, ganti, t)
    return _rapikan(t)


def padankan(t):
    """Langkah 5-6: awalan ILMU dan padanan sinonim."""
    m = re.match(r"^ILMU\s+(?!DAN\b)(.+)$", t)            # 5. awalan ILMU
    if m and t not in ILMU_DIPERTAHANKAN:
        t = m.group(1)
    for pola, ganti in POLA_SINONIM:                     # 6a. pola umum
        t = re.sub(pola, ganti, t)
    return PETA_SINONIM.get(t, t)                        # 6b. nama persis


def normalkan_prodi(nama):
    """Nama prodi mentah -> prodi_normal."""
    return padankan(bentuk_dasar(nama))


# --------------------------------------------------------------------------
# Fitur prodi sejenis
# --------------------------------------------------------------------------
# Prodi sejenis = prodi_normal + jenjang yang sama, pada jalur yang sama (K-03).
KUNCI_SEJENIS = ["prodi_normal", "jenjang", "jalur"]
FITUR_SEJENIS = ["rata_peminat_prodi_sejenis_lag1",
                 "jumlah_ptn_punya_prodi_sejenis_lag1",
                 "rasio_peminat_vs_sejenis_lag1"]


def tambah_fitur_sejenis(df):
    """Tambahkan prodi_normal dan tiga fitur prodi sejenis ke df.

    df harus berisi baris bertarget tanpa entri fakultas (seperti panel
    pemodelan di fondasi.py), dengan kolom prodi, jenjang, jalur, tahun,
    id_ptn, peminat, dan peminat_lag1.

    Untuk baris (prodi P, PTN A, tahun t), dihitung dari prodi sejenis P di
    PTN LAIN pada tahun t-1:
      rata_peminat_prodi_sejenis_lag1     rata-rata peminat per prodi
      jumlah_ptn_punya_prodi_sejenis_lag1 jumlah PTN lain
      rasio_peminat_vs_sejenis_lag1       peminat_lag1 / rata_peminat_..._lag1
    Seluruh prodi PTN A dikecualikan, bukan hanya baris P sendiri: kampus
    utama dan PSDKU dari PTN yang sama bukan pembanding antar-PTN.
    Tahun t-1 diambil lewat penggabungan pada nilai tahun (K-04). Bila tidak
    ada prodi sejenis di PTN lain pada t-1, ketiganya NaN (K-05).
    """
    df = df.copy()
    df["prodi_normal"] = df["prodi"].map(normalkan_prodi)
    kunci = KUNCI_SEJENIS + ["tahun"]

    total = (df.groupby(kunci)
               .agg(_jumlah=("peminat", "sum"), _n=("peminat", "size"),
                    _n_ptn=("id_ptn", "nunique"))
               .reset_index())
    sendiri = (df.groupby(kunci + ["id_ptn"])
                 .agg(_jumlah_sendiri=("peminat", "sum"), _n_sendiri=("peminat", "size"))
                 .reset_index())
    # Geser ke tahun berikutnya: nilai tahun t-1 menempel di baris tahun t.
    total["tahun"] += 1
    sendiri["tahun"] += 1

    n_awal = len(df)
    df = (df.merge(total, on=kunci, how="left", validate="many_to_one")
            .merge(sendiri, on=kunci + ["id_ptn"], how="left", validate="many_to_one"))
    assert len(df) == n_awal, "Penggabungan fitur sejenis mengubah jumlah baris"

    # PTN ini tidak punya prodi sejenis di t-1 -> kontribusinya ke jumlah memang 0.
    ada_sendiri = df["_n_sendiri"].notna()
    n_lain = df["_n"] - df["_n_sendiri"].where(ada_sendiri, 0)
    jumlah_lain = df["_jumlah"] - df["_jumlah_sendiri"].where(ada_sendiri, 0)
    ptn_lain = df["_n_ptn"] - ada_sendiri.astype(int)
    punya = n_lain > 0                                   # NaN dibandingkan -> False

    rata = (jumlah_lain / n_lain).where(punya)
    df["rata_peminat_prodi_sejenis_lag1"] = rata
    df["jumlah_ptn_punya_prodi_sejenis_lag1"] = ptn_lain.where(punya)
    # Rata-rata prodi sejenis 0 -> rasio tidak terdefinisi, dibiarkan NaN.
    df["rasio_peminat_vs_sejenis_lag1"] = (df["peminat_lag1"] / rata).where(rata > 0)
    return df.drop(columns=["_jumlah", "_n", "_n_ptn", "_jumlah_sendiri", "_n_sendiri"])


def _uji_fitur_sejenis(df, n=2000):
    """Bandingkan tambah_fitur_sejenis() dengan hitungan manual baris per baris."""
    hasil = tambah_fitur_sejenis(df)
    sampel = hasil.sample(min(n, len(hasil)), random_state=BENIH)
    cocok = 0
    for _, r in sampel.iterrows():
        lain = hasil[(hasil["prodi_normal"] == r["prodi_normal"])
                     & (hasil["jenjang"] == r["jenjang"]) & (hasil["jalur"] == r["jalur"])
                     & (hasil["tahun"] == r["tahun"] - 1) & (hasil["id_ptn"] != r["id_ptn"])]
        if lain.empty:
            harap = (np.nan, np.nan)
        else:
            harap = (lain["peminat"].mean(), lain["id_ptn"].nunique())
        dapat = (r["rata_peminat_prodi_sejenis_lag1"], r["jumlah_ptn_punya_prodi_sejenis_lag1"])
        sama = all((np.isnan(h) and np.isnan(d)) or np.isclose(h, d)
                   for h, d in zip(harap, dapat))
        assert sama, f"Tidak cocok pada {r['prodi']} {r['jalur']} {r['tahun']}: {harap} vs {dapat}"
        cocok += 1
    print(f"Fitur sejenis cocok dengan hitungan manual: {cocok} dari {len(sampel)} baris sampel "
          f"({sampel['rata_peminat_prodi_sejenis_lag1'].isna().sum()} di antaranya NaN)")


# --------------------------------------------------------------------------
# Mode tinjau
# --------------------------------------------------------------------------
def _katalog():
    """Satu baris per prodi (id_prodi), tanpa entri fakultas ITB (K-09)."""
    df = pd.read_csv(FILE_PANEL)
    df = df[df["is_fakultas"] == 0].drop_duplicates("id_prodi").copy()
    df["nama_mentah"] = df["prodi"].map(lambda p: _rapikan(str(p).upper()))
    df["bentuk_dasar"] = df["prodi"].map(bentuk_dasar)
    df["prodi_normal"] = df["prodi"].map(normalkan_prodi)
    return df


def _periksa_peta():
    """Validasi peta sinonim; gagal = berhenti.

    - tidak berantai (A -> B -> C),
    - satu nama lama hanya di satu kelompok,
    - tidak ada nama baku yang ditulis dua kali di _SINONIM (kamus Python
      diam-diam menimpa kunci ganda, jadi diperiksa dari kode sumber).
    """
    import ast
    from collections import Counter

    rantai = {k: v for k, v in PETA_SINONIM.items() if v in PETA_SINONIM}
    assert not rantai, f"Peta sinonim berantai: {rantai}"

    lama = Counter(n for daftar in _SINONIM.values() for n in daftar)
    ganda = [n for n, c in lama.items() if c > 1]
    assert not ganda, f"Nama lama muncul di lebih dari satu kelompok: {ganda}"

    pohon = ast.parse(Path(__file__).read_text(encoding="utf-8"))
    for simpul in ast.walk(pohon):
        if (isinstance(simpul, ast.Assign) and len(simpul.targets) == 1
                and getattr(simpul.targets[0], "id", None) == "_SINONIM"):
            kunci = Counter(k.value for k in simpul.value.keys)
            dobel = [k for k, c in kunci.items() if c > 1]
            assert not dobel, f"Nama baku ditulis dua kali di _SINONIM: {dobel}"


def tinjau(n_teratas=50, n_jarang=30):
    _periksa_peta()
    kat = _katalog()

    print("=" * 100)
    print("MODE TINJAU - tidak ada file yang ditulis")
    print("=" * 100)
    print(f"Prodi (tanpa 21 entri fakultas ITB)         : {len(kat)}")
    print(f"Nama prodi unik - mentah persis             : {kat['prodi'].nunique()}")
    print(f"Nama prodi unik - huruf besar & spasi rapi  : {kat['nama_mentah'].nunique()}")
    print(f"Nama prodi unik - setelah langkah 1-4       : {kat['bentuk_dasar'].nunique()}")
    print(f"Nama prodi unik - prodi_normal (1-6)        : {kat['prodi_normal'].nunique()}")
    print(f"Entri peta sinonim                          : {len(PETA_SINONIM)}")

    grup = (kat.groupby("prodi_normal")
               .agg(prodi=("id_prodi", "size"), ptn=("id_ptn", "nunique"),
                    jenjang=("jenjang", lambda s: ",".join(sorted(set(s)))))
               .sort_values(["prodi", "ptn"], ascending=False))

    def asal(n):
        sub = kat[kat["prodi_normal"] == n]
        dasar = sub["bentuk_dasar"].value_counts()
        teks = "; ".join(f"{b} ({c})" for b, c in dasar.items())
        tulis = sub["nama_mentah"].nunique()
        return teks, tulis

    print(f"\n{n_teratas} PRODI_NORMAL TERBANYAK")
    print("-" * 100)
    for i, (n, r) in enumerate(grup.head(n_teratas).iterrows(), 1):
        teks, tulis = asal(n)
        print(f"{i:>3}. {n}  [{r['prodi']} prodi, {r['ptn']} PTN, {r['jenjang']}]")
        print(f"       bentuk dasar: {teks}")
        print(f"       variasi tulisan mentah: {tulis}")

    jarang = grup[grup["ptn"] <= 2]
    print(f"\nPRODI_NORMAL DI 1-2 PTN: {len(jarang)} nama "
          f"({jarang['prodi'].sum()} prodi = {jarang['prodi'].sum() / len(kat):.1%})")
    print(f"  di 1 PTN: {(jarang['ptn'] == 1).sum()} | di 2 PTN: {(jarang['ptn'] == 2).sum()}")
    print(f"\n{n_jarang} CONTOH ACAK (benih={BENIH})")
    print("-" * 100)
    for n in sorted(jarang.sample(min(n_jarang, len(jarang)), random_state=BENIH).index):
        sub = kat[kat["prodi_normal"] == n]
        mentah = "; ".join(sorted(sub["prodi"].str.strip().unique()))
        ptn = "; ".join(sorted(sub["ptn_nama"].unique()))
        r = grup.loc[n]
        print(f"  {n}  [{r['ptn']} PTN, {r['jenjang']}]")
        print(f"       mentah: {mentah}")
        print(f"       PTN   : {ptn}")
    return kat, grup


if __name__ == "__main__":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:  # noqa: BLE001
        pass
    if "--uji" in sys.argv:
        _periksa_peta()
        from fondasi import _panel_pemodelan  # noqa: E402
        _uji_fitur_sejenis(_panel_pemodelan())
    else:
        tinjau()
        print("\nTidak ada file yang disimpan.")
