"""
Fitur `kelompok_bidang` dan penanda `is_fakultas` dari kolom `prodi` pada
data/olahan/snpmb_panel.csv.

Pendekatan: pencocokan KATA KUNCI pada nama prodi yang sudah dinormalisasi,
bukan pencocokan nama persis -- nama yang sama ditulis berbeda antar PTN
(INFORMATIKA / TEKNIK INFORMATIKA / ILMU KOMPUTER).

Klasifikasi ini disusun tim, bukan berasal dari SNPMB. Sebutkan demikian di
laporan.

MODE TINJAU (bawaan): hanya mencetak, tidak menyimpan apa pun.
Simpan hasil (setelah disetujui): python fitur_kelompok_bidang.py --simpan

--------------------------------------------------------------------------
ATURAN PRIORITAS (dievaluasi berurutan, yang pertama cocok menang)
--------------------------------------------------------------------------
 1. Pengecualian "PENDIDIKAN" non-kependidikan -> kesehatan.
    "PENDIDIKAN DOKTER" adalah gelar kedokteran, bukan program calon guru.
 2. pendidikan  -- "PENDIDIKAN ...", KEGURUAN, TADRIS, PAUD, BIMBINGAN
    KONSELING. Karena di atas teknik, "PENDIDIKAN TEKNIK MESIN" masuk
    pendidikan: yang dilatih adalah gurunya, bukan insinyurnya.
 3. Pengecualian teknik -> teknik: nama bermuatan TEKNIK SIPIL / INFRASTRUKTUR.
    Mencegah "...SUMBER DAYA AIR DAN SANITASI LINGKUNGAN" tertarik ke kesehatan.
 4. kesehatan   -- kata kunci spesifik: KEPERAWATAN (bukan PERAWAT, yang ikut
    cocok di PERAWATAN mesin), PROFESI DOKTER/NERS/BIDAN (bukan PROFESI, yang
    ikut cocok di PROFESIONAL).
 5. seni        -- sebelum teknik, agar "DESAIN ..." tidak tertarik ke teknik.
 6. pertanian   -- sebelum teknik, agar TEKNIK PERTANIAN, TEKNOLOGI PANGAN,
    TEKNOLOGI INDUSTRI PERTANIAN masuk pertanian. Kata kunci sengaja spesifik
    ("ILMU KELAUTAN", bukan "KELAUTAN") supaya TEKNIK KELAUTAN tetap teknik.
 7. teknik      -- sebelum sains, agar TEKNIK KIMIA masuk teknik.
 8. sains       -- tanpa kata kunci "SAINS" polos (SAINS KOMUNIKASI bukan sains).
 9. Pengecualian HUKUM / DAKWAH -> sosial_humaniora, sebelum ekonomi
    (HUKUM BISNIS bukan ekonomi; MANAJEMEN DAKWAH bukan manajemen).
10. ekonomi
11. sosial_humaniora -- termasuk rumpun media: periklanan, penyiaran,
    penerbitan, produksi media, humas.
12. olahraga    -- ilmu keolahragaan, kepelatihan, rekreasi, masase.
    (Pendidikan jasmani/olahraga sudah tertangkap aturan 2 -> pendidikan.)
13. pariwisata  -- pariwisata, perhotelan, perjalanan wisata, MICE, tata boga.
14. belum_terpetakan -- TIDAK ada yang dipaksa masuk kelompok.

 0. Sebelum semua aturan di atas: PETA_KHUSUS (nama persis) untuk segelintir
    nama ambigu yang diputuskan manual. Lihat komentar pada PETA_KHUSUS.

Kata kunci dicocokkan di AWAL kata saja (IKAN tidak cocok di PENDIDIKAN,
LAHAN tidak cocok di PENGOLAHAN), tapi boleh sebagai awalan (AGROTEK).

PADANAN ISCED-F 2013 (UNESCO) -- dasar yang dapat disitasi
  kesehatan        -> 09 Health and welfare
  teknik           -> 06 ICT + 07 Engineering, manufacturing and construction
  sains            -> 05 Natural sciences, mathematics and statistics
  pertanian        -> 08 Agriculture, forestry, fisheries and veterinary
  ekonomi          -> 04 Business, administration and law (tanpa hukum)
  sosial_humaniora -> 02 Arts and humanities (humaniora) + 03 Social sciences,
                      journalism and information + hukum dari 04
  pendidikan       -> 01 Education
  seni             -> 02 Arts and humanities (seni)
  pariwisata       -> 10 Services (hospitality, travel, tourism, catering)
  olahraga         -> 10 Services (sports)
  Penyesuaian terhadap ISCED beserta alasannya: docs/KEPUTUSAN_METODOLOGI.md
  (hukum -> sosial_humaniora, kedokteran hewan -> kesehatan, teknologi pangan
  -> pertanian, 10 Services dipecah menjadi pariwisata dan olahraga).

PENANDA is_fakultas
  Entri ITB yang diterima per fakultas/sekolah (nama berawalan FAKULTAS atau
  SEKOLAH). Peminatnya gabungan beberapa prodi, sehingga bukan pembanding
  setara. Tetap diberi kelompok_bidang; dikeluarkan dari pemodelan di fondasi.
"""

import re
import sys
from pathlib import Path

import pandas as pd

FILE_PANEL = Path(__file__).resolve().parents[1] / "data" / "olahan" / "snpmb_panel.csv"
BENIH = 42          # contoh acak dapat direproduksi
N_CONTOH = 10

# Salah ketik & singkatan yang ditemukan di data. Diterapkan berurutan setelah
# huruf besar dan perapian spasi, sebelum pencocokan kata kunci.
EJAAN = [
    (r"\bPENDD?\b\.?\s*", "PENDIDIKAN "),
    (r"\bPGSD\b", "PENDIDIKAN GURU SEKOLAH DASAR"),
    (r"\bPG[\s-]?PAUD\b", "PENDIDIKAN GURU PAUD"),
    (r"\bP?PKN\b", "PENDIDIKAN PANCASILA DAN KEWARGANEGARAAN"),
    (r"\bPLB\b", "PENDIDIKAN LUAR BIASA"),
    (r"\bPLS\b", "PENDIDIKAN LUAR SEKOLAH"),
    (r"\bPENJASKES(REK)?\b", "PENDIDIKAN JASMANI KESEHATAN DAN REKREASI"),
    (r"\bBIMB\b\.?\s*", "BIMBINGAN "),
    (r"\b(BHS|BAH)\b\.?\s*", "BAHASA "),
    (r"\bADM\b\.?\s*", "ADMINISTRASI "),
    (r"\bIL\b\.?\s*", "ILMU "),
    (r"\bILM\b\.?\s*", "ILMU "),
    (r"\bKOM\b\.?\s*", "KOMUNIKASI "),
    (r"\bEKO\b\.?\s*", "EKONOMI "),
    (r"\bSUMB\b\.?\s*", "SUMBER DAYA "),
    (r"\bMANAJ\b\.?\s*", "MANAJEMEN "),
    (r"\bTEK\b\.?\s*", "TEKNIK "),
    (r"\bDKV\b", "DESAIN KOMUNIKASI VISUAL"),
    (r"\bAKUTANSI\b", "AKUNTANSI"),
    (r"\bKEWIRUSAHAAN\b", "KEWIRAUSAHAAN"),
    (r"\bFISOTERAPI\b", "FISIOTERAPI"),
    (r"\bOCEANOGRAFI\b", "OSEANOGRAFI"),
    (r"\bLINGKUNGAAN\b", "LINGKUNGAN"),
    (r"\bMAJEMEN\b", "MANAJEMEN"),
]

KECUALI_PENDIDIKAN_KESEHATAN = [
    "PENDIDIKAN DOKTER", "PENDIDIKAN PROFESI DOKTER", "PENDIDIKAN APOTEKER",
    "PENDIDIKAN PROFESI NERS", "PENDIDIKAN PROFESI BIDAN",
]

PENDIDIKAN = [
    "PENDIDIKAN", "KEGURUAN", "TADRIS", "PAUD", "GURU", "BIMBINGAN",
    "KONSELING",
]

KECUALI_TEKNIK = ["TEKNIK SIPIL", "INFRASTRUKTUR"]

KESEHATAN = [
    "DOKTER", "KEDOKTERAN", "KEPERAWATAN", "NERS", "KEBIDANAN", "BIDAN",
    "FARMASI", "APOTEKER", "GIZI", "KESEHATAN", "GIGI", "BIOMEDIS",
    "BIOMEDIK", "RADIOLOGI", "RADIODIAGNOSTIK", "FISIOTERAPI", "TERAPI",
    "ANESTESI", "REKAM MEDIS", "LABORATORIUM MEDIS", "LABORATORIUM MEDIK",
    "ORTOTIK", "PROSTETIK", "AKUPUNKTUR", "BANK DARAH", "OPTOMETRI",
    "SANITASI", "VETERINER", "KARDIOVASKULER", "ELEKTROMEDIK", "TRANSFUSI",
    "PROFESI DOKTER", "PROFESI NERS", "PROFESI BIDAN", "HIGIENE",
    "PENGOBAT",
]

SENI = [
    "SENI", "DESAIN", "MUSIK", "TARI", "KARAWITAN", "TEATER", "KRIYA",
    "FILM", "TELEVISI", "FOTOGRAFI", "ANIMASI", "PEDALANGAN",
    "ETNOMUSIKOLOGI", "SENDRATASIK", "KOMUNIKASI VISUAL", "INTERIOR",
    "FASHION", "BUSANA", "TATA RIAS", "KOREOGRAFI", "KERIS",
]

PERTANIAN = [
    "PERTANIAN", "AGRIBISNIS", "AGROBISNIS", "AGROTEK", "AGROEKOTEK", "AGRONOMI",
    "AGROINDUSTRI", "AGROFOREST", "AGROWISATA", "AGRICULTURE", "PETERNAKAN",
    "TERNAK", "PAKAN", "PERIKANAN", "IKAN", "AKUAKULTUR", "BUDIDAYA",
    "BUDI DAYA", "PERAIRAN", "AKUATIK", "ILMU KELAUTAN",
    "TEKNOLOGI KELAUTAN", "KEHUTANAN", "HUTAN", "SILVIKULTUR", "PERKEBUNAN",
    "HORTIKULTURA", "TANAMAN", "ILMU TANAH", "LAHAN", "PANGAN",
    "TEKNOLOGI HASIL", "BIOSISTEM", "PENYULUHAN", "BENIH", "PERBENIHAN", "EKOWISATA",
    "PENGOLAHAN HASIL",
]

TEKNIK = [
    "TEKNIK", "TEKNOLOGI REKAYASA", "REKAYASA", "INFORMATIKA", "BIOINFORMATIKA",
    "ILMU KOMPUTER", "SISTEM INFORMASI", "TEKNOLOGI INFORMASI",
    "SISTEM KOMPUTER", "ARSITEKTUR", "PERENCANAAN WILAYAH", "MESIN",
    "ELEKTRO", "SIPIL", "PERTAMBANGAN", "METALURGI", "PERKAPALAN",
    "PENERBANGAN", "OTOMOTIF", "MEKATRONIKA", "INSTRUMENTASI",
    "TELEKOMUNIKASI", "ELEKTRONIKA", "MANUFAKTUR", "KONSTRUKSI", "GEODESI",
    "GEOMATIKA", "NUKLIR", "DIRGANTARA", "NAUTIKA", "TRANSPORTASI",
    "MULTIMEDIA", "ROBOTIKA", "INDUSTRI", "KOMPUTER", "JARINGAN",
    "PERANGKAT LUNAK", "SURVEI DAN PEMETAAN", "PENGINDERAAN JAUH",
    "LISTRIK", "KELISTRIKAN", "ALAT BERAT", "KECERDASAN ARTIFISIAL", "KECERDASAN BUATAN",
    "BIOPROSES", "PERMAINAN", "GAME", "PERKERETAAPIAN", "ENERGI",
    "PEMBANGKIT", "PENGECORAN", "LOGAM", "PERKAKAS", "PESAWAT",
    "MINYAK DAN GAS", "PULP", "KERTAS", "BANGUNAN GEDUNG",
    "JALAN DAN JEMBATAN", "PERUMAHAN", "PERMUKIMAN", "PEMUKIMAN",
    "TATA RUANG", "INOVASI DIGITAL", "KOSMETIK", "PERAWATAN",
]

SAINS = [
    "MATEMATIKA", "FISIKA", "KIMIA", "BIOLOGI", "STATISTIK", "AKTUARIA",
    "ASTRONOMI", "GEOGRAFI", "GEOFISIKA", "GEOLOGI", "BIOTEKNOLOGI",
    "MIKROBIOLOGI", "BIOKIMIA", "SAINS DATA", "METEOROLOGI", "OSEANOGRAFI",
    "ILMU LINGKUNGAN", "KEBUMIAN", "HAYATI", "PEMBANGUNAN WILAYAH",
    "BIOSAINS", "SAINS ATMOSFIR", "SAINS LINGKUNGAN", "LABORATORIUM SAINS",
]

KECUALI_SOSHUM = ["HUKUM", "DAKWAH"]

EKONOMI = [
    "EKONOMI", "MANAJEMEN", "AKUNTANSI", "BISNIS", "KEUANGAN", "PERBANKAN",
    "PERPAJAKAN", "PAJAK", "ADMINISTRASI NIAGA", "KEWIRAUSAHAAN",
    "ENTERPRENEUR", "ENTREPRENEUR", "PEMASARAN", "LOGISTIK", "KOPERASI",
    "ASURANSI", "PERDAGANGAN", "KETATALAKSANAAN",
]

SOSHUM = [
    "SOSIOLOGI", "ANTROPOLOGI", "POLITIK", "HUBUNGAN INTERNASIONAL",
    "KOMUNIKASI", "PSIKOLOGI", "SASTRA", "BAHASA", "LINGUISTIK", "SEJARAH",
    "FILSAFAT", "ARKEOLOGI", "ADMINISTRASI", "SEKRETARI", "KESEKRETARIATAN", "KESEJAHTERAAN SOSIAL",
    "PERPUSTAKAAN", "KEARSIPAN", "ARSIP", "JURNALISTIK", "KRIMINOLOGI",
    "SYARIAH", "USHULUDDIN", "TAFSIR", "HADIS", "AQIDAH", "MUAMALAH",
    "SOSIAL", "ILMU AL", "PERBANDINGAN MAZHAB", "KENOTARIATAN",
    "PEMERINTAHAN", "KEPENDUDUKAN", "HUMANIORA", "HUMANITAS", "AGAMA",
    "TEOLOGI", "PERIKLANAN", "PENYIARAN", "PENERBITAN", "PRODUKSI MEDIA",
    "HUMAS", "HUBUNGAN MASYARAKAT", "TRADISI LISAN", "KELUARGA DAN KONSUMEN",
    "STUDI PEMBANGUNAN",
]

PARIWISATA = [
    "PARIWISATA", "PERHOTELAN", "USAHA PERJALANAN", "PERJALANAN WISATA",
    "WISATA", "TATA BOGA", "KULINER", "KONVENSI", "MEETING INCENTIVE",
    "PAMERAN",
]

OLAHRAGA = [
    "KEOLAHRAGAAN", "OLAHRAGA", "KEPELATIHAN", "REKREASI", "MASASE",
]

# Nama ambigu yang diputuskan manual oleh tim, dicocokkan pada nama PERSIS
# (setelah normalisasi) dan diperiksa sebelum aturan kata kunci. Dipakai hanya
# bila kata kunci akan salah menarik nama lain (mis. menambahkan
# "SAINS INFORMASI" ke teknik akan ikut menarik "ILMU PERPUSTAKAAN DAN SAINS
# INFORMASI" yang seharusnya sosial_humaniora).
PETA_KHUSUS = {
    "SAINS INFORMASI": "teknik",               # UPN Veteran Jakarta; dugaan, belum diverifikasi
    "PENGELOLAAN LINGKUNGAN": "pertanian",     # diselenggarakan politeknik pertanian
    "SENI KULINER": "pariwisata",              # sejalan dengan TATA BOGA / KULINER
}

# Urutan inilah aturan prioritasnya.
ATURAN = [
    ("kesehatan", KECUALI_PENDIDIKAN_KESEHATAN),
    ("pendidikan", PENDIDIKAN),
    ("teknik", KECUALI_TEKNIK),
    ("kesehatan", KESEHATAN),
    ("seni", SENI),
    ("pertanian", PERTANIAN),
    ("teknik", TEKNIK),
    ("sains", SAINS),
    ("sosial_humaniora", KECUALI_SOSHUM),
    ("ekonomi", EKONOMI),
    ("sosial_humaniora", SOSHUM),
    ("olahraga", OLAHRAGA),
    ("pariwisata", PARIWISATA),
]

KELOMPOK = ["kesehatan", "teknik", "sains", "pertanian", "ekonomi",
            "sosial_humaniora", "pendidikan", "seni", "pariwisata", "olahraga",
            "belum_terpetakan"]


def normalkan(nama):
    """Huruf besar, tanda baca dirapikan, singkatan & salah ketik dibentangkan."""
    t = str(nama or "").upper()
    t = t.replace("&", " DAN ")
    t = re.sub(r"[^A-Z0-9\.\s-]", " ", t)
    t = re.sub(r"\s+", " ", t).strip()
    for pola, ganti in EJAAN:
        t = re.sub(pola, ganti, t)
    t = t.replace(".", " ")
    return re.sub(r"\s+", " ", t).strip()


# Kata kunci hanya cocok di AWAL kata, tidak di tengahnya. Tanpa ini "IKAN"
# ikut cocok di PENDIDIKAN dan "LAHAN" di PENGOLAHAN. Akhir kata dibiarkan
# terbuka agar awalan tetap berlaku (AGROTEK -> AGROTEKNOLOGI).
POLA = [(k, re.compile("|".join(r"(?<![A-Z])" + re.escape(w) for w in kk)))
        for k, kk in ATURAN]


def petakan(nama):
    t = normalkan(nama)
    if t in PETA_KHUSUS:
        return PETA_KHUSUS[t]
    for kelompok, pola in POLA:
        if pola.search(t):
            return kelompok
    return "belum_terpetakan"


def is_fakultas(nama):
    return int(bool(re.match(r"^(FAKULTAS|SEKOLAH)\b", normalkan(nama))))


def bangun(df):
    """Tambahkan kelompok_bidang & is_fakultas ke seluruh baris panel."""
    peta = {p: (petakan(p), is_fakultas(p)) for p in df["prodi"].dropna().unique()}
    df = df.copy()
    df["kelompok_bidang"] = df["prodi"].map(lambda p: peta.get(p, (None, None))[0])
    df["is_fakultas"] = df["prodi"].map(lambda p: peta.get(p, (None, None))[1])
    return df


def tinjau(df):
    unik = df.drop_duplicates("id_prodi")[
        ["id_prodi", "prodi", "ptn_nama", "kelompok_bidang", "is_fakultas"]].copy()
    unik["nama_normal"] = unik["prodi"].map(normalkan)

    print("=" * 92)
    print("MODE TINJAU - tidak ada file yang ditulis")
    print(f"{len(unik)} prodi unik (id_prodi), "
          f"{unik['nama_normal'].nunique()} nama unik setelah normalisasi")
    print("=" * 92)

    print("\nDISTRIBUSI PRODI UNIK PER KELOMPOK BIDANG")
    print("-" * 92)
    hit = unik["kelompok_bidang"].value_counts()
    print(f"{'kelompok':<20} {'prodi':>7} {'%':>7}   {'nama unik':>10}")
    for k in KELOMPOK:
        n = int(hit.get(k, 0))
        nu = unik[unik["kelompok_bidang"] == k]["nama_normal"].nunique()
        print(f"{k:<20} {n:>7} {n / len(unik) * 100:>6.1f}%   {nu:>10}")
    print(f"{'TOTAL':<20} {len(unik):>7}")

    belum = unik[unik["kelompok_bidang"] == "belum_terpetakan"]
    print(f"\n\nSELURUH NAMA 'belum_terpetakan' ({belum['nama_normal'].nunique()} "
          f"nama unik, {len(belum)} prodi) - urut frekuensi")
    print("-" * 92)
    frek = (belum.groupby("nama_normal")
                 .agg(n_prodi=("id_prodi", "size"), contoh_ptn=("ptn_nama", "first"))
                 .sort_values(["n_prodi"], ascending=False, kind="stable"))
    if frek.empty:
        print("  (tidak ada)")
    else:
        print(f"  {'n':>4}  {'nama prodi (ternormalisasi)':<52} contoh PTN")
        for nama, r in frek.iterrows():
            print(f"  {r['n_prodi']:>4}  {nama[:52]:<52} {str(r['contoh_ptn'])[:34]}")

    print(f"\n\nCONTOH ACAK {N_CONTOH} NAMA PER KELOMPOK (benih={BENIH})")
    print("=" * 92)
    for k in KELOMPOK:
        sub = unik[unik["kelompok_bidang"] == k]
        if sub.empty:
            print(f"\n[{k}] kosong")
            continue
        nama_unik = pd.Series(sorted(sub["nama_normal"].unique()))
        ambil = nama_unik.sample(min(N_CONTOH, len(nama_unik)), random_state=BENIH)
        print(f"\n[{k}] {len(sub)} prodi / {len(nama_unik)} nama unik")
        for n in sorted(ambil):
            print(f"    {n}")

    fak = unik[unik["is_fakultas"] == 1].sort_values("nama_normal")
    print(f"\n\nPENANDA is_fakultas = 1 ({len(fak)} entri, "
          f"PTN: {', '.join(sorted(fak['ptn_nama'].unique()))})")
    print("-" * 92)
    for _, r in fak.iterrows():
        print(f"  [{r['kelompok_bidang']:<16}] {r['nama_normal'][:70]}")


def main():
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:  # noqa: BLE001
        pass

    df = bangun(pd.read_csv(FILE_PANEL))

    if "--simpan" in sys.argv:
        df.to_csv(FILE_PANEL, index=False, encoding="utf-8-sig")
        print(f"[simpan] {FILE_PANEL} - kolom kelompok_bidang & is_fakultas ditambahkan")
        return

    tinjau(df)
    print("\nTidak ada file yang disimpan. Setelah disetujui: "
          "python fitur_kelompok_bidang.py --simpan")


if __name__ == "__main__":
    main()
