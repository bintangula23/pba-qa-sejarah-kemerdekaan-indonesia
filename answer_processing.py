"""Answer Processing — QA Sejarah Indonesia, tanpa LLM
"""

import re
from collections import defaultdict
from question_processing import normalize_question
from validasi_tokoh import (
    POLA_NAMA, POLA_KELAHIRAN, ambil_tokoh_pertanyaan,
    validasi_tokoh, cek_subjek_kelahiran, periksa_konteks_tokoh,
)

# pola bersama, kapitalisasi nama tidak dinonaktifkan oleh IGNORECASE global.
NAMA = POLA_NAMA
INISIAL = r"(?:[A-Z][a-z]+\s+)?(?:[A-Z]\.\s*)+[A-Z][a-z]+"
LOKASI = rf"{NAMA}(?:,\s*{NAMA})?"
ANGKA = r"(?<![\w.,])(?:\d{1,3}(?:\.\d{3})+|\d+)(?![\d.,])"
BULAN = (r"Januari|Februari|Maret|April|Mei|Juni|Juli|Agustus|"
         r"September|Oktober|November|Desember")
SATUAN = ("negara bagian", "anggota", "orang", "korban", "pasukan", "hari", "bulan", "tahun")
PENGHUBUNG = r"\b(?:dan kemudian|kemudian|lalu|setelah itu|sedangkan|sementara itu)\b|;"

# nama relasi internal, bukan nama tokoh, jawaban, atau ID evaluasi.
RELASI_DATE = {
    "KELAHIRAN": POLA_KELAHIRAN,
    "PENDIRIAN": r"\b(?:mendirikan|didirikan|pendirian)\b",
    "PELANTIKAN": r"\b(?:dilantik|melantik|pelantikan)\b",
    "PEMBAWAAN": r"\b(?:dibawa(?:nya)?|membawa|pembawaan)\b",
    "PELUNCURAN": r"\b(?:dilancarkan|melancarkan)\b",
    "KEMERDEKAAN": r"\b(?:memproklamasikan\s+kemerdekaan|proklamasi\s+kemerdekaan|merdeka)\b",
    "KEMATIAN": r"\b(?:meninggal|wafat)\b",
    "PEMBENTUKAN": r"\b(?:dibentuk|membentuk)\b",
    "PENANDATANGANAN": r"\b(?:ditandatangani|menandatangani)\b",
    "PERMULAAN": r"\b(?:dimulai|memulai)\b",
}
RELASI_PER = {
    "PEMBERIAN_JULUKAN": r"\b(?:julukan|dijuluki)\b",
    "KOMANDAN_TEWAS": r"\bkomandan\b.*\btewas\b",
    "PEMILIHAN_PANGLIMA": r"\b(?:terpilih|dipilih)\b.*\bpanglima\b",
    "PELEDAKAN": r"\bmeledakkan\b",
    "MEMIMPIN_PASUKAN": r"\bmemimpin\s+pasukan\b",
    "PERANTARA": r"\bperantara\b",
    "KEPALA_DELEGASI": r"\b(?:kepala|pemimpin)\s+delegasi\b",
    "PENUNJUKAN_WAKIL_PRESIDEN": r"\bwakil\s+presiden\b",
    "PENUNJUKAN_PRESIDEN": r"\bpresiden\b",
}
RELASI_LOC = {
    "KELAHIRAN": POLA_KELAHIRAN,
    "PENGASINGAN": r"\b(?:diasingkan|dikapalkan|dipindahkan)\b",
    "BERLABUH": r"\bberlabuh\b",
    "PEMBUKAAN": r"\bpersidangan\b.*\bdibuka\b",
    "PENDARATAN": r"\bpendaratan\b",
}

def unik(hasil):
    nilai = list(dict.fromkeys(x for x in hasil if x))
    return nilai[0] if len(nilai) == 1 else None

def cocok_grup(pola, teks, flags=0):
    m = re.search(pola, teks, flags)
    return m.group(1).strip() if m else None

def entitas_ada(entitas, teks):
    """Kesamaan frasa dengan batas token; mendukung singkatan huruf awal."""
    if not entitas:
        return False
    nama = normalize_question(entitas)
    normal = normalize_question(teks)
    if re.search(rf"(?<!\w){re.escape(nama)}(?!\w)", normal):
        return True
    if re.fullmatch(r"[A-Z]{2,8}", entitas):
        # cocokan singkatan dengan rangkaian kata yang menyebut nama
        # minimal satu kata harus berkapital dalam teks asli
        kata = re.findall(r"[A-Za-z]+", teks)
        n = len(entitas)
        for i in range(len(kata) - n + 1):
            frasa = kata[i:i+n]
            nama_formal = all(k[0].isupper() for k in frasa)
            awalan_lembaga = frasa[0].casefold() in {"republik", "tentara", "partai", "panitia", "badan", "perserikatan"}
            if (nama_formal or (awalan_lembaga and all(k[0].isupper() for k in frasa[1:]))) and "".join(k[0].upper() for k in frasa) == entitas:
                return True
    return False

def relasi_pertama(aturan, pertanyaan):
    return next((label for label, pola in aturan.items()
                 if re.search(pola, pertanyaan, re.I)), None)

def identifikasi_peristiwa_per(pertanyaan):
    return relasi_pertama(RELASI_PER, pertanyaan)

def ambil_tokoh_pertanyaan_tanggal(pertanyaan):
    return cocok_grup(r"^\s*(?:kapan(?:kah)?|(?:pada\s+)?tanggal\s+berapa|(?:pada\s+)?tahun\s+berapa)\s+(.+?)\s+(?:lahir|dilahirkan)\s*\??\s*$", pertanyaan, re.I)

def analisis_pertanyaan(info):
    """Ekstrak relasi dan argumen dari struktur pertanyaan yang didukung."""
    q = info.get("original_question", "").strip().rstrip("?").strip()
    tipe = info.get("answer_type")
    a = {"tipe": tipe, "pertanyaan": q,
         "normal": info.get("normalized_question") or normalize_question(q),
         "relasi": None, "entitas": [], "topik": [], "konteks": [],
         "ketelitian": "TANGGAL", "tokoh": None, "satuan": None}
    def grup(pola):
        return cocok_grup(pola, q, re.I)
    def wajib(kunci, *nilai):
        a[kunci].extend(v for v in nilai if v)

    if tipe == "DATE":
        r = a["relasi"] = relasi_pertama(RELASI_DATE, q)
        if re.search(r"\btahun\s+berapa\b", q, re.I):
            a["ketelitian"] = "TAHUN"
        elif re.search(r"\bbulan\s+apa\b", q, re.I):
            a["ketelitian"] = "BULAN"
        if r == "KELAHIRAN":
            a["tokoh"] = ambil_tokoh_pertanyaan_tanggal(q)
        elif r == "PENDIRIAN":
            wajib("entitas", grup(r"\bmendirikan\s+(.+)$") or grup(r"^(?:kapan(?:kah)?|(?:pada\s+)?(?:tanggal|tahun)\s+berapa)\s+(.+?)\s+didirikan\b"))
            a["aktor"] = grup(r"^(?:kapan(?:kah)?|(?:pada\s+)?(?:tanggal|tahun)\s+berapa)\s+(.+?)\s+mendirikan\b")
        elif r == "PEMBAWAAN":
            nama = grup(r"^(?:kapan(?:kah)?|(?:pada\s+)?tanggal\s+berapa)\s+(.+?)\s+dibawa\b")
            wajib("entitas", *(re.split(r"\s+dan\s+", nama, flags=re.I) if nama else []), grup(r"\bdibawa\s+ke\s+(.+)$"))
        elif r == "PELANTIKAN":
            wajib("entitas", grup(r"^(?:kapan(?:kah)?|(?:pada\s+)?tanggal\s+berapa)\s+(.+?)\s+dilantik\b"), grup(r"\bsebagai\s+(.+?)(?:\s+pada\s+|$)"), grup(r"\bpada\s+(Kabinet\s+.+)$"))
        elif r == "PELUNCURAN":
            wajib("entitas", grup(r"\bsebutan\s+(.+?)\s+dilancarkan\b") or grup(r"^(?:kapan\s+)?(.+?)\s+dilancarkan\b"))
        elif r == "KEMERDEKAAN":
            wajib("entitas", grup(r"^kapan(?:kah)?\s+(.+?)\s+merdeka\b") or grup(r"\bkemerdekaan\s+(.+)$"))
        elif r:
            wajib("entitas", grup(r"^(?:kapan(?:kah)?|(?:pada\s+)?(?:tanggal|tahun)\s+berapa)\s+(.+?)\s+(?:meninggal|wafat|dibentuk|ditandatangani|dimulai)\b"))

    elif tipe == "PER":
        r = a["relasi"] = identifikasi_peristiwa_per(q)
        if r == "PEMBERIAN_JULUKAN":
            wajib("entitas", grup(r'\bjulukan\s+["“]([^"”]+)["”]') or grup(r"\bjulukan\s+(.+?)(?:\s+kepada\s+|$)"))
        elif r == "KOMANDAN_TEWAS":
            wajib("entitas", grup(r"\bkomandan\s+pasukan\s+(.+?)\s+yang\s+tewas\b"))
            wajib("topik", grup(r"\bdi\s+(.+)$"))
            tanggal = grup(r"\bpada\s+(\d{1,2}\s+\w+\s+\d{4})\b")
            if tanggal:
                hari_bulan, tahun = tanggal.rsplit(" ", 1)
                wajib("entitas", hari_bulan)
                wajib("konteks", tahun)
        elif r == "PEMILIHAN_PANGLIMA":
            wajib("entitas", grup(r"\bpanglima\s+(.+)$"))
        elif r == "PELEDAKAN":
            wajib("konteks", grup(r"\bmeledakkan\s+(.+?)(?:\s+di\s+|\s+dengan\s+|$)"), grup(r"\bdi\s+(.+?)(?:\s+dengan\s+|$)"))
        elif r == "MEMIMPIN_PASUKAN":
            wajib("entitas", grup(r"\bdari\s+(.+?)(?:\s+hingga\s+|\s+sampai\s+|\s+dalam\s+|$)"), grup(r"\b(?:hingga|sampai)\s+ke\s+(.+?)(?:\s+dalam\s+|$)"))
            wajib("topik", grup(r"\bdalam\s+(.+)$"))
        elif r in {"KEPALA_DELEGASI", "PERANTARA"}:
            if r == "KEPALA_DELEGASI":
                wajib("entitas", grup(r"\bdelegasi\s+(.+?)(?:\s+dalam\s+|\s+pada\s+|$)"))
            wajib("topik", grup(r"\b(?:perundingan|perjanjian)\s+(.+)$"))
            if r == "PERANTARA" and re.search(r"\btahap awal\b", q, re.I):
                wajib("entitas", "tahap awal")
        elif r in {"PENUNJUKAN_PRESIDEN", "PENUNJUKAN_WAKIL_PRESIDEN"}:
            wajib("konteks", grup(r"\bditunjuk\s+(.+?)\s+sebagai\b"))
            wajib("entitas", grup(r"\bpresiden(?:\s+pertama)?\s+(.+)$"))
            a["pertama"] = bool(re.search(r"\bpertama\b", q, re.I))

    elif tipe == "LOC":
        r = a["relasi"] = relasi_pertama(RELASI_LOC, q)
        if r == "KELAHIRAN":
            a["tokoh"] = ambil_tokoh_pertanyaan(q)
        elif r == "PENGASINGAN":
            a["tokoh"] = grup(r"^(?:ke|di)\s+(?:\w+\s+)?mana(?:kah)?\s+(.+?)\s+(?:diasingkan|dikapalkan|dipindahkan)\b")
            wajib("entitas", a["tokoh"], grup(r"\btahun\s+(\d{4})\b"))
        elif r == "BERLABUH":
            wajib("entitas", grup(r"\bkapal\s+(.+?)\s+berlabuh\b"))
        elif r == "PEMBUKAAN":
            wajib("entitas", grup(r"\bpersidangan\s+(?:pertama\s+)?(.+?)\s+dibuka\b"))
        elif r == "PENDARATAN":
            a["operasi"] = grup(r"\boperasi\s+(.+)$")
            wajib("entitas", a["operasi"])
            wajib("konteks", grup(r"\bpasukan\s+(.+?)\s+melakukan\b"))

    elif tipe == "NUM":
        a["satuan"] = next((s for s in SATUAN if re.search(rf"\b{re.escape(s)}\b", q, re.I)), None)
        if a["satuan"]:
            a["relasi"] = "JUMLAH"
            wajib("entitas", grup(rf"\b{re.escape(a['satuan'])}\s+(.+)$"))

    elif tipe == "MISC":
        if re.search(r"\bsumber daya alam\b", q, re.I):
            a["relasi"] = "SUMBER_DAYA"
            wajib("entitas", grup(r"\bsasaran utama\s+(.+?)(?:\s+dalam\s+|$)"), grup(r"\bpendudukannya\s+di\s+(.+)$"))
        elif re.search(r"\bnama kapal\b", q, re.I):
            a["relasi"] = "KAPAL_PENYERAHAN"
            wajib("entitas", grup(r"\btempat\s+(.+?)(?:\s+secara resmi)?\s+menyerah\b"), grup(r"\bmenyerah\s+kepada\s+(.+)$"))
    return a

def validasi_relevansi(a, teks, konteks=None):
    """Validasi argumen yang dikenali. Topik hanya untuk pertanyaan bertopik,
    jawaban dan relasi tetap harus muncul di kalimat bukti, bukan di judul.
    """
    konteks = konteks or {}
    sekitar = " ".join([teks, konteks.get("sebelumnya", "")])
    topik = " ".join([sekitar, konteks.get("judul", "")])
    for entitas in a["entitas"]:
        if entitas_ada(entitas, teks):
            continue
        if a["tipe"] == "NUM" and entitas.lower().startswith("republik "):
            if entitas_ada(entitas[9:], teks) and entitas_ada(entitas, sekitar):
                continue
        return False
    return (all(entitas_ada(x, topik) for x in a["topik"])
            and all(entitas_ada(x, sekitar) for x in a["konteks"]))

# DATE: ekstraksi waktu dipisahkan dari keputusan relevansi
def ekstrak_tanggal(teks):
    return [{"tanggal": m.group(), "awal": m.start(), "akhir": m.end()}
            for m in re.finditer(rf"\b\d{{1,2}}\s+(?:{BULAN})\s+\d{{4}}\b", teks, re.I)]

def ekstrak_tahun(teks):
    return re.findall(r"\b(?:18|19|20)\d{2}\b", teks)

def ekstrak_bulan_tahun(teks):
    return list(dict.fromkeys(re.findall(rf"\b(?:{BULAN})\s+\d{{4}}\b", teks, re.I)))

def _waktu(a, teks, konteks=None):
    r = a["relasi"]
    if not r or (r == "KELAHIRAN" and not a["tokoh"]) or (r != "KELAHIRAN" and not a["entitas"]):
        return None
    if r == "PENDIRIAN" and a.get("aktor"):
        aktor = a["aktor"]
        judul = (konteks or {}).get("judul", "")
        if not entitas_ada(aktor, teks) and not (entitas_ada(aktor, judul) and entitas_ada(aktor.split()[-1], teks)):
            return None
    jawaban = []
    for klausa in re.split(PENGHUBUNG, teks, flags=re.I):
        if not re.search(RELASI_DATE[r], klausa, re.I):
            continue
        if r == "KEMERDEKAAN":
            if re.search(r"\b(?:hut|peringatan|pidato|ulang tahun)\b", klausa, re.I):
                continue
            if not re.search(r"\b(?:memproklamasikan\s+kemerdekaan|proklamasi\s+kemerdekaan.*(?:dibacakan|dilaksanakan)|(?:merdeka|kemerdekaan)\s+pada)\b", klausa, re.I):
                continue
        if not validasi_relevansi(a, klausa, konteks):
            continue
        if r == "PENDIRIAN":
            # Organisasi merupakan objek mendirikan atau subjek didirikan.
            n = normalize_question(klausa)
            organisasi = re.escape(normalize_question(a["entitas"][0]))
            pola = rf"(?:\bmendirikan\s+(?:sebuah\s+)?{organisasi}(?!\w)|(?<!\w){organisasi}\s+(?:resmi\s+)?didirikan\b)"
            if not re.search(pola, n):
                continue
        if a["ketelitian"] == "TAHUN":
            pilihan = ekstrak_tahun(klausa)
        elif a["ketelitian"] == "BULAN":
            pilihan = ekstrak_bulan_tahun(klausa)
        else:
            pilihan = [x["tanggal"] for x in ekstrak_tanggal(klausa)]
        if unik(pilihan):
            jawaban.append(unik(pilihan))
    return unik(jawaban)

def pilih_tanggal(pertanyaan, teks):
    a = analisis_pertanyaan({"original_question": pertanyaan, "answer_type": "DATE"})
    if a["relasi"] == "KELAHIRAN" and (not a["tokoh"] or validasi_tokoh(a["tokoh"], teks) != "COCOK"):
        return None
    return _waktu(a, teks)

def ekstrak_tahun_pendirian(pertanyaan, teks):
    """Kompatibilitas fungsi lama."""
    a = analisis_pertanyaan({"original_question": pertanyaan, "answer_type": "DATE"})
    return _waktu(a, teks) if a["relasi"] == "PENDIRIAN" else None

# PER:
# setiap pola mengikat nama ke peran/tindakan, kata kunci case-insensitive.
POLA_PER = {
    "PEMBERIAN_JULUKAN": [
        rf"\b({NAMA})\s+(?i:memberikan\s+julukan)\b",
        rf"(?i:\b(?:diberi\s+julukan|dijuluki)\b[^.!?\n]{{0,120}}?\boleh\s+)({NAMA})",
        rf"(?i:\bjulukan\s+[^.!?\n]{{1,100}}?\s+diberikan\s+oleh\s+)({NAMA})",
    ],
    "KOMANDAN_TEWAS": [
        rf"(?i:\bkomandan\s+pasukan\s+[^,]+,\s+)({INISIAL}|{NAMA})\s*,?\s*(?i:tewas)\b",
        rf"(?i:\bkomandan\s+pasukan\s+[^,.!?]+?\s+yang\s+tewas\s+adalah\s+)({INISIAL}|{NAMA})",
    ],
    "PEMILIHAN_PANGLIMA": [
        rf"(?i:\bbernama\s+)({NAMA})\s+(?i:terpilih|dipilih)\s+(?i:menjadi|sebagai)\s+(?i:panglima)\b",
        rf"\b({NAMA})\s+(?i:terpilih|dipilih)\s+(?i:menjadi|sebagai)\s+(?i:panglima)\b",
    ],
    "PELEDAKAN": [rf"\b({NAMA})\s+(?i:(?:berhasil\s+)?meledakkan)\b"],
    "MEMIMPIN_PASUKAN": [rf"\b({NAMA})\s+(?i:(?:langsung\s+)?memimpin\s+pasukan)\b"],
    "PERANTARA": [rf",\s*({NAMA}),\s*(?i:bertindak\s+sebagai\s+perantara)\b"],
    "KEPALA_DELEGASI": [rf"(?i:\b(?:kepala|pemimpin)\s+delegasi\s+[^,]+,\s*)({NAMA})\s*,"],
}
POLA_PASANGAN = (rf"(?i:\bmenunjuk\s+)({NAMA})\s+(?i:dan)\s+({NAMA})"
                 r"\s+(?i:masing-masing\s+sebagai\s+presiden\s+dan\s+wakil\s+presiden)\b")

def ekstrak_pelaku(teks, peristiwa=None):
    if peristiwa is None:
        peristiwa = identifikasi_peristiwa_per(teks)
    if peristiwa in {"PENUNJUKAN_PRESIDEN", "PENUNJUKAN_WAKIL_PRESIDEN"}:
        m = re.search(POLA_PASANGAN, teks)
        return m.group(2 if peristiwa.endswith("WAKIL_PRESIDEN") else 1) if m else None
    for pola in POLA_PER.get(peristiwa, []):
        hasil = cocok_grup(pola, teks)
        if hasil:
            return hasil
    return None

def _pelaku(a, teks, konteks):
    r = a["relasi"]
    if r == "KEPALA_DELEGASI" and a["entitas"]:
        m = re.search(rf"(?i:\b(?:kepala|pemimpin)\s+delegasi\s+)([^,]+),\s*({NAMA})\s*,", teks)
        if not m or not all(entitas_ada(x, m.group(1)) for x in a["entitas"]):
            return None
    if r and r.startswith("PENUNJUKAN_") and a.get("pertama") and not re.search(r"\bpertama\b", teks, re.I):
        return None
    return ekstrak_pelaku(teks, r) if r and validasi_relevansi(a, teks, konteks) else None

# LOC:
# nama objek diperoleh dari pertanyaan, bukan nilai tetap.
def ekstrak_lokasi(teks):
    bagian = re.split(PENGHUBUNG, teks, maxsplit=1, flags=re.I)[0]
    return cocok_grup(rf"(?i:\b(?:lahir|dilahirkan)\b).{{0,60}}?(?i:\bdi\s+)({LOKASI})\b", bagian)

def _lokasi(a, teks, konteks):
    r = a["relasi"]
    if r == "KELAHIRAN":
        return ekstrak_lokasi(teks) if a["tokoh"] else None
    if not a["entitas"] or not validasi_relevansi(a, teks, konteks):
        return None
    if r == "PENGASINGAN" and a["tokoh"]:
        pola = rf"({NAMA})\s+(?i:diasingkan|dikapalkan|dipindahkan)\b[^;.!?]{{0,180}}?(?i:\bke\s+(?:kota\s+)?(?:terpencil\s+)?)({LOKASI})"
        m = re.search(pola, teks)
        return m.group(2) if m and entitas_ada(a["tokoh"], m.group(1)) else None
    if r == "BERLABUH":
        # Pola lama dipertahankan untuk klausa relatif tentang kapal.
        m = re.search(rf"(?i:\bberlabuh\s+di\s+)({LOKASI})", teks)
        if not m:
            return None
        nama = re.escape(normalize_question(a["entitas"][0]))
        sebelum = normalize_question(teks[:m.start()])
        # Nama kapal harus terkait dengan predikat, bukan hanya disebut
        # jauh sebelumnya (contoh: kapal lain yang berlabuh).
        pola_subjek = rf"(?<!\w){nama}(?!\w)(?:\s*,\s*kapal[^.!?]{{0,100}}?\bsaat)?\s*$"
        return m.group(1) if re.search(pola_subjek, sebelum) else None
    if r == "PEMBUKAAN":
        lokasi = cocok_grup(rf"(?i:\bpembukaan\s+masa\s+persidangan\b[^.?!]{{0,100}}?\bdi\s+)((?i:gedung)\s+{NAMA}\s+(?i:di)\s+{NAMA})", teks)
        return lokasi[0].upper() + lokasi[1:] if lokasi else None
    if r == "PENDARATAN" and a.get("operasi") and re.search(r"\bpendaratan\b", teks, re.I):
        return cocok_grup(rf"(?i:\b{re.escape(a['operasi'])}\s+di\s+)({LOKASI})", teks)
    return None

def ekstrak_lokasi_peristiwa(pertanyaan, teks):
    a = analisis_pertanyaan({"original_question": pertanyaan, "answer_type": "LOC"})
    if a["relasi"] == "KELAHIRAN" and (not a["tokoh"] or validasi_tokoh(a["tokoh"], teks) != "COCOK"):
        return None
    return _lokasi(a, teks, {})

# NUM dan MISC
def _angka(a, teks, konteks):
    satuan = a["satuan"]
    if not satuan or not validasi_relevansi(a, teks, konteks):
        return None
    pola = rf"({ANGKA})\s+{re.escape(satuan)}\b"
    hasil = []
    for klausa in re.split(PENGHUBUNG, teks, flags=re.I):
        if not validasi_relevansi(a, klausa, konteks):
            continue
        for m in re.finditer(pola, klausa, re.I):
            if a["entitas"]:
                n = normalize_question(klausa[:m.start()])
                entitas = a["entitas"][0]
                nama = normalize_question(entitas)
                if nama.startswith("republik ") and not entitas_ada(entitas, klausa):
                    nama = nama[9:]
                pengikat = r"(?:terdiri\s+(?:dari|atas)|memiliki|mempunyai|mencakup|berjumlah|sebanyak)"
                pola_subjek = (rf"(?<!\w){re.escape(nama)}(?:\s+(?:ini|itu|tersebut))?\s+"
                               rf"(?:dibentuk\s+[^,;.]{{1,100}}?\s+yang\s+)?{pengikat}\s*$")
                # Pola NUM yang tidak terhubung dengan entitas ditolak
                if not re.search(pola_subjek, n):
                    continue
            hasil.append(m.group() if satuan == "negara bagian" else m.group(1))
    return unik(hasil)

def ekstrak_angka(pertanyaan, teks):
    return _angka(analisis_pertanyaan({"original_question": pertanyaan, "answer_type": "NUM"}), teks, {})

def _misc(a, teks, konteks):
    if not a["entitas"] or not validasi_relevansi(a, teks, konteks):
        return None
    if a["relasi"] == "SUMBER_DAYA":
        hasil = cocok_grup(r"\b(?:menguasai\s+)?sumber-sumber\s+alam,\s*terutama\s+([a-z]+(?:\s+[a-z]+)*)\s*,", teks, re.I)
        return hasil[0].upper() + hasil[1:] if hasil else None
    if a["relasi"] == "KAPAL_PENYERAHAN":
        return cocok_grup(rf"(?i:\bmenyerah\s+kepada\s+.+?\s+di\s+kapal\s+)({NAMA})", teks)
    return None

def ekstrak_misc(pertanyaan, teks):
    return _misc(analisis_pertanyaan({"original_question": pertanyaan, "answer_type": "MISC"}), teks, {})

# orkestrasi
# indeks konteks satu kali, tanpa mengubah skor atau urutan BM25.
def ambil_konteks(id_kalimat, indeks, blok):
    record = indeks.get(id_kalimat, {})
    daftar = blok.get(record.get("id_blok"), [])
    posisi = next((i for i, x in enumerate(daftar) if x["id_kalimat"] == id_kalimat), 0)
    return {"judul": record.get("judul_dokumen", ""),
            "sebelumnya": " ".join(x["teks_asli"] for x in daftar[max(0, posisi - 3):posisi]),
            "blok": daftar}

def ambil_jawaban(info_pertanyaan, kandidat, kalimat_korpus=None):
    a = analisis_pertanyaan(info_pertanyaan)
    if not a["relasi"]:
        return None
    indeks, blok = {}, defaultdict(list)
    for item in kalimat_korpus or []:
        indeks[item["id_kalimat"]] = item
        blok[item.get("id_blok", item["id_kalimat"].rsplit("-K", 1)[0])].append(item)
    ekstraktor = {"DATE": _waktu, "PER": _pelaku, "LOC": _lokasi,
                 "NUM": _angka, "MISC": _misc}.get(a["tipe"])
    if not ekstraktor:
        return None
    for item in kandidat:
        teks, identitas = item.get("teks_asli", ""), item.get("id_kalimat")
        if not teks or not identitas:
            continue
        konteks = ambil_konteks(identitas, indeks, blok)
        if a["relasi"] == "KELAHIRAN":
            if not a["tokoh"] or not re.search(POLA_KELAHIRAN, teks, re.I):
                continue
            status = validasi_tokoh(a["tokoh"], teks)
            if status == "TIDAK_COCOK":
                continue
            if status == "PERLU_KONTEKS":
                if not re.search(r"\b(?:ia|dia|beliau)\s+(?:lahir|dilahirkan)\b", teks, re.I):
                    continue
                if not periksa_konteks_tokoh(a["tokoh"], identitas, konteks["blok"]):
                    continue
        jawaban = ekstraktor(a, teks, konteks)
        if jawaban:
            return {"jawaban": jawaban, "id_kalimat": identitas}
    return None
