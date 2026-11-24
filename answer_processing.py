"""
Modul Answer Processing
Penanggung jawab: Bintang

Fungsi modul:
1. Menerima hasil question processing.
2. Menerima kandidat kalimat dari passage retrieval.
3. Mengekstraksi jawaban berdasarkan answer_type.
4. Mengembalikan jawaban beserta ID kalimat sumber.
"""

import re

from validasi_tokoh import (
    ambil_tokoh_pertanyaan,
    cek_subjek_kelahiran,
    validasi_tokoh,
    periksa_konteks_tokoh
)

def ekstrak_tanggal(teks):
    """
    Menemukan semua tanggal lengkap dalam sebuah teks.
    Parameter:
        teks (str): Kalimat sumber.
    Return:
        list: Daftar tanggal beserta posisi awal dan akhir.
    """

    bulan = (
        r"Januari|Februari|Maret|April|Mei|Juni|"
        r"Juli|Agustus|September|Oktober|November|Desember"
    )

    pola = rf"\b\d{{1,2}}\s+(?:{bulan})\s+\d{{4}}\b"

    hasil_tanggal = []

    for cocok in re.finditer(pola, teks, flags=re.IGNORECASE):
        hasil_tanggal.append({
            "tanggal": cocok.group(),
            "awal": cocok.start(),
            "akhir": cocok.end()
        })

    return hasil_tanggal

def ekstrak_tahun(teks):
    """
    Mengambil tahun empat digit dari teks.
    Tahun yang menjadi bagian tanggal lengkap juga dapat ditemukan.
    """
    pola = r"\b(?:18|19|20)\d{2}\b"

    return re.findall(pola, teks)

def ekstrak_bulan_tahun(teks):
    """
    Mengekstraksi bulan dan tahun dari kalimat sumber.
    Contoh: Desember 1948.
    """

    bulan = (
        r"Januari|Februari|Maret|April|Mei|Juni|"
        r"Juli|Agustus|September|Oktober|November|Desember"
    )

    pola = rf"\b(?:{bulan})\s+\d{{4}}\b"

    hasil = re.findall(pola, teks, flags=re.IGNORECASE)

    return list(dict.fromkeys(hasil))

def ekstrak_tahun_pendirian(pertanyaan, teks):
    """
    Mengekstraksi tahun pendirian organisasi jika
    nama organisasi dalam pertanyaan juga muncul pada kalimat.
    """

    pola_pertanyaan = (
        r"pada\s+tahun\s+berapa\s+"
        r".+?\s+mendirikan\s+(.+?)\s*\?$"
    )

    hasil = re.search(
        pola_pertanyaan,
        pertanyaan,
        flags=re.IGNORECASE
    )

    if hasil is None:
        return None

    organisasi = hasil.group(1).strip()

    # Nama organisasi harus muncul di kalimat sumber.
    if organisasi.casefold() not in teks.casefold():
        return None

    # Kalimat harus membahas peristiwa pendirian.
    if not re.search(
        r"\b(?:mendirikan|didirikan)\b",
        teks,
        flags=re.IGNORECASE
    ):
        return None

    tahun_ditemukan = ekstrak_tahun(teks)

    # Hindari memilih tahun jika ada beberapa kemungkinan.
    tahun_unik = list(dict.fromkeys(tahun_ditemukan))

    if len(tahun_unik) == 1:
        return tahun_unik[0]

    return None

def pilih_tanggal(pertanyaan, teks):
    """
    Memilih tanggal berdasarkan peristiwa dan konteks klausa dalam kalimat sumber.
    """
    if re.search(
        r"\bpada\s+tahun\s+berapa\b",
        pertanyaan,
        flags=re.IGNORECASE
    ):
        return ekstrak_tahun_pendirian(pertanyaan, teks)

    if re.search(
        r"\bpada\s+bulan\s+apa\b",
        pertanyaan,
        flags=re.IGNORECASE
    ):
        bulan_tahun = ekstrak_bulan_tahun(teks)

        if len(bulan_tahun) == 1:
            return bulan_tahun[0]

        return None

    tanggal_ditemukan = ekstrak_tanggal(teks)

    if not tanggal_ditemukan:
        return None

    kata_peristiwa = [
        "lahir",
        "meninggal",
        "dilantik",
        "dibentuk",
        "didirikan",
        "mendirikan",
        "ditandatangani",
        "dimulai",
    ]

    pertanyaan_kecil = pertanyaan.lower()

    # Identifikasi peristiwa yang ditanyakan
    peristiwa = None

    for kata in kata_peristiwa:
        if re.search(
            r"\b" + re.escape(kata) + r"\b",
            pertanyaan_kecil
        ):
            peristiwa = kata
            break

    # Jika peristiwa tidak dikenali, hanya izinkan jawaban jika ada satu tanggal.
    if peristiwa is None:
        if len(tanggal_ditemukan) == 1:
            return tanggal_ditemukan[0]["tanggal"]
        return None

    # Pisahkan kalimat pada beberapa kata penghubung
    klausa = re.split(
        r"\b(?:dan|serta|kemudian)\b",
        teks,
        flags=re.IGNORECASE
    )

    kandidat_jawaban = []

    for bagian in klausa:

        # Periksa apakah klausa memuat peristiwa
        if not re.search(
            r"\b" + re.escape(peristiwa) + r"\b",
            bagian,
            flags=re.IGNORECASE
        ):
            continue

        # Cari tanggal dalam klausa
        tanggal_klausa = ekstrak_tanggal(bagian)

        if len(tanggal_klausa) == 1:
            kandidat_jawaban.append(
                tanggal_klausa[0]["tanggal"]
            )

    # Kembalikan jawaban hanya jika tidak ambigu
    jawaban_unik = list(dict.fromkeys(kandidat_jawaban))

    if len(jawaban_unik) == 1:
        return jawaban_unik[0]

    return None    

def identifikasi_peristiwa_per(pertanyaan):
    """
    Mengidentifikasi jenis peristiwa untuk pertanyaan PER.
    """

    pertanyaan = pertanyaan.lower()

    if "julukan" in pertanyaan:
        return "PEMBERIAN_JULUKAN"

    if "komandan" in pertanyaan and "tewas" in pertanyaan:
        return "KOMANDAN_TEWAS"

    if "terpilih" in pertanyaan and "panglima" in pertanyaan:
        return "PEMILIHAN_PANGLIMA"

    if "meledakkan" in pertanyaan:
        return "PELEDAKAN"

    if "memimpin" in pertanyaan and "pasukan" in pertanyaan:
        return "MEMIMPIN_PASUKAN"

    if "perantara" in pertanyaan:
        return "PERANTARA"

    if "kepala delegasi" in pertanyaan:
        return "KEPALA_DELEGASI"

    if "ditunjuk" in pertanyaan and "wakil presiden" in pertanyaan:
        return "PENUNJUKAN_WAKIL_PRESIDEN"    

    return None

def ekstrak_pelaku(teks, peristiwa=None):
    """
    Mengekstraksi kandidat nama pelaku dari kalimat aktif atau pasif sederhana.
    """

    if peristiwa == "PEMILIHAN_PANGLIMA":

        pola = (
            r"\bbernama\s+"
            r"([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)"
            r"\s+terpilih\s+menjadi\s+panglima\b"
        )

        hasil = re.search(pola, teks)

        if hasil:
            return hasil.group(1)

        return None

    if peristiwa == "PELEDAKAN":

        pola = (
            r"\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)"
            r"\s+berhasil\s+meledakkan\b"
        )

        hasil = re.search(pola, teks)

        if hasil:
            return hasil.group(1)

        return None

    if peristiwa == "MEMIMPIN_PASUKAN":

        pola = (
            r"\b(Letkol\s+[A-Z][a-z]+)"
            r"\s+(?:langsung\s+)?memimpin\s+pasukan\b"
        )

        hasil = re.search(pola, teks)

        if hasil:
            return hasil.group(1)

        return None

    if peristiwa == "PERANTARA":

        pola = (
            r",\s*"
            r"([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)"
            r",\s*bertindak\s+sebagai\s+perantara\b"
        )

        hasil = re.search(pola, teks, flags=re.IGNORECASE)

        if hasil:
            return hasil.group(1)

        return None

    if peristiwa == "KEPALA_DELEGASI":

        pola = (
            r"\bkepala\s+delegasi\s+republik\s+indonesia,\s*"
            r"([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)"
            r"\s*,"
        )

        hasil = re.search(pola, teks, flags=re.IGNORECASE)

        if hasil:
            return hasil.group(1)

        return None

    if peristiwa == "PENUNJUKAN_WAKIL_PRESIDEN":

        pola = (
            r"\bmenunjuk\s+"
            r"([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)"
            r"\s+dan\s+"
            r"([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)"
            r"\s+masing-masing\s+sebagai\s+"
            r"presiden\s+dan\s+wakil\s+presiden\b"
        )

        hasil = re.search(pola, teks, flags=re.IGNORECASE)

        if hasil:
            return hasil.group(2)

        return None
    
    if peristiwa == "PEMBERIAN_JULUKAN":

        pola_julukan = [
            (
                r"\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+)+)"
                r"\s+memberikan\s+julukan\b"
            ),

            # Diberi julukan ... oleh Nama
            (
                r"\bdiberi\s+julukan\b"
                r"[^.!?\n]{0,120}?"
                r"\boleh\s+"
                r"([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)"
            ),

            # Dijuluki ... oleh Nama
            (
                r"\bdijuluki\b"
                r"[^.!?\n]{0,120}?"
                r"\boleh\s+"
                r"([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)"
            )
        ]

        for pola in pola_julukan:
            hasil = re.search(pola, teks)

            if hasil:
                return hasil.group(1)

        return None

    elif peristiwa == "KOMANDAN_TEWAS":

        nama_berinisial = (
            r"((?:[A-Z][a-z]+\s+)?"
            r"(?:[A-Z]\.\s*)+"
            r"[A-Z][a-z]+)"
        )

        pola_komandan = [
            # Jabatan, nama, lalu tewas
            (
                r"(?i:\bkomandan\s+pasukan\s+[^,]+,\s+)"
                + nama_berinisial
                + r"\s*,?\s*(?i:tewas)\b"
            ),

            # Jabatan yang tewas adalah nama
            (
                r"(?i:\bkomandan\s+pasukan\s+"
                r"[^,.!?]+?\s+yang\s+tewas\s+adalah\s+)"
                + nama_berinisial
            )
        ]

        for pola in pola_komandan:
            hasil = re.search(pola, teks)

            if hasil:
                return hasil.group(1)

        return None

    pola_aktif = (
        r"\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+)+)"
        r"\s+memberikan\b"
    )

    pola_pasif = (
        r"\bdiberikan\s+oleh\s+"
        r"([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\b"
    )

    pola_pasif_julukan = (
        r"\bdiberi\s+julukan\s+"
        r"[\"“]?[^\n\"”]{1,100}[\"”]?\s+oleh\s+"
        r"([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\b"
    )

    hasil = re.search(pola_aktif, teks)

    if hasil:
        return hasil.group(1)

    hasil = re.search(pola_pasif, teks, flags=re.IGNORECASE)

    if hasil:
        return hasil.group(1)

    hasil = re.search(pola_pasif_julukan, teks, flags=re.IGNORECASE)

    if hasil:
        return hasil.group(1)

    # Pola nama tokoh yang menggunakan gelar dan inisial
    nama_berinisial = (
        r"((?:[A-Z][a-z]+\s+)?"
        r"(?:[A-Z]\.\s*)+"
        r"[A-Z][a-z]+)"
    )

    # Jabatan, nama, kemudian peristiwa tewas
    pola_jabatan_tewas = (
        r"(?i:\bkomandan\s+pasukan\s+[^,]+,\s+)"
        + nama_berinisial
        + r"\s*,?\s*(?i:tewas)\b"
    )

    # Nama langsung diikuti peristiwa tewas
    pola_nama_tewas = (
        r"\b" + nama_berinisial + r"\s+(?i:tewas)\b"
    )

    # Jabatan yang tewas adalah nama
    pola_jabatan_adalah = (
        r"(?i:\bkomandan\s+pasukan\s+"
        r".+?\s+yang\s+tewas\s+adalah\s+)"
        + nama_berinisial
    )

    for pola in [
        pola_jabatan_tewas,
        pola_nama_tewas,
        pola_jabatan_adalah
    ]:
        hasil = re.search(pola, teks)

        if hasil:
            return hasil.group(1)

    return None

def ekstrak_lokasi(teks):
    """
    Mengekstraksi kandidat lokasi kelahiran. Pencarian dibatasi agar tidak melewati beberapa penghubung peristiwa.
    """

    # Pisahkan teks ketika ada peralihan peristiwa.
    bagian = re.split(
        r"\b(?:dan kemudian|kemudian|lalu|setelah itu)\b",
        teks,
        maxsplit=1,
        flags=re.IGNORECASE
    )[0]

    pola = (
        r"\b(?:lahir|dilahirkan)\b"
        r".{0,60}?"
        r"\bdi\s+"
        r"([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\b"
    )

    hasil = re.search(pola, bagian)

    if hasil:
        return hasil.group(1)

    return None

def ekstrak_lokasi_peristiwa(pertanyaan, teks):
    """
    Mengekstraksi lokasi berdasarkan hubungan peristiwa yang ditanyakan.
    """
    pertanyaan_kecil = pertanyaan.casefold()

    # Lokasi pengasingan ke suatu kota
    if "diasingkan" in pertanyaan_kecil:

        # Pastikan tokoh yang ditanyakan muncul dalam kalimat.
        if "soekarno" not in teks.casefold():
            return None

        pola = (
            r"\bke\s+kota\s+(?:terpencil\s+)?"
            r"([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)"
            r"\s*(?:,|\.|$)"
        )

        hasil = re.search(pola, teks)

        if hasil:
            return hasil.group(1)

        return None

    # Lokasi kapal berlabuh
    if "berlabuh" in pertanyaan_kecil:

        # Pastikan kapal yang ditanyakan muncul dalam kalimat.
        if "uss renville" not in teks.casefold():
            return None

        pola = (
            r"\bberlabuh\s+di\s+"
            r"([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)"
            r"\s*(?:,|\.|$)"
        )

        hasil = re.search(pola, teks)

        if hasil:
            return hasil.group(1)

        return None

    if "persidangan" in pertanyaan_kecil and "dibuka" in pertanyaan_kecil:

        pola = (
            r"\bpembukaan\s+masa\s+persidangan\b"
            r"[^.]{0,100}?"
            r"\bdi\s+"
            r"(gedung\s+[A-Z][A-Za-z]+"
            r"(?:\s+[A-Z][A-Za-z]+)*"
            r"\s+di\s+[A-Z][a-z]+)"
        )

        hasil = re.search(pola, teks, flags=re.IGNORECASE)

        if hasil:
            lokasi = hasil.group(1).strip()
            return lokasi[0].upper() + lokasi[1:]

        return None

    if "pendaratan" in pertanyaan_kecil and "produk utara" in pertanyaan_kecil:

        pola = (
            r"\bProduk\s+Utara\s+di\s+"
            r"([A-Z][A-Za-z]+\s+[A-Z][A-Za-z]+,\s*"
            r"[A-Z][A-Za-z]+)"
        )

        hasil = re.search(pola, teks, flags=re.IGNORECASE)

        if hasil:
            return hasil.group(1).strip()

        return None

    return None

def ekstrak_angka(pertanyaan, teks):
    """
    Mengekstraksi jumlah numerik berdasarkan kata satuan yang muncul dalam pertanyaan.
    """

    satuan = [
        "negara bagian",
        "anggota",
        "orang",
        "korban",
        "pasukan",
        "hari",
        "bulan",
        "tahun",
    ]

    pertanyaan_kecil = pertanyaan.lower()

    for kata in satuan:
        if re.search(r"\b" + re.escape(kata) + r"\b", pertanyaan_kecil):

            pola = rf"\b(\d+)\s+{re.escape(kata)}\b"

            hasil = re.search(pola, teks, flags=re.IGNORECASE)

            if hasil:
                if kata == "negara bagian":
                    return hasil.group(0)
                
                return hasil.group(1)

    return None

def ekstrak_misc(pertanyaan, teks):
    """
    Mengekstraksi jawaban objek faktual untuk pertanyaan sumber daya alam atau nama kapal.
    """
    pertanyaan_kecil = pertanyaan.casefold()

    # Sumber daya alam yang menjadi sasaran utama
    if "sumber daya alam" in pertanyaan_kecil:

        if not re.search(
            r"\b(?:jepang|hindia belanda)\b",
            teks,
            flags=re.IGNORECASE
        ):
            return None

        pola = (
            r"\bsumber-sumber\s+alam,\s*terutama\s+"
            r"([a-z]+(?:\s+[a-z]+)*)"
            r"\s*,"
        )

        hasil = re.search(pola, teks, flags=re.IGNORECASE)

        if hasil:
            jawaban = hasil.group(1).strip()
            return jawaban[0].upper() + jawaban[1:]

        return None

    # Nama kapal tempat penyerahan Jepang
    if "nama kapal" in pertanyaan_kecil:

        if not re.search(
            r"\bjepang\b.*\bmenyerah\b",
            teks,
            flags=re.IGNORECASE
        ):
            return None

        pola = (
            r"\bmenyerah\s+kepada\s+Sekutu\s+"
            r"di\s+kapal\s+"
            r"(USS\s+[A-Z][A-Za-z]+)"
        )

        hasil = re.search(pola, teks, flags=re.IGNORECASE)

        if hasil:
            return hasil.group(1)

        return None

    return None

def ambil_tokoh_pertanyaan_tanggal(pertanyaan):
    """
    Mengambil nama tokoh dari pertanyaan:
    'Kapan [nama tokoh] lahir?'
    """

    pola = r"^\s*kapan\s+(.+?)\s+lahir\s*\?$"

    hasil = re.search(pola, pertanyaan, flags=re.IGNORECASE)

    if hasil:
        return hasil.group(1).strip()

    return None

def ambil_jawaban(
    info_pertanyaan, 
    kandidat,
    kalimat_korpus=None
):
    """
    Mengambil jawaban dari kandidat hasil passage retrieval.

    Parameter:
        info_pertanyaan: dictionary hasil Question Processing
        kandidat: list hasil Passage Retrieval

    Return:
        dictionary berisi jawaban dan id_kalimat,
        atau None jika belum ditemukan.
    """

    tipe_jawaban = info_pertanyaan.get("answer_type")
    pertanyaan = info_pertanyaan.get("original_question", "")

    for item in kandidat:
        teks = item.get("teks_asli", "")
        id_kalimat = item.get("id_kalimat")

        if tipe_jawaban == "DATE":

            nama_tokoh = ambil_tokoh_pertanyaan_tanggal(pertanyaan)

            if nama_tokoh is not None:

                status_tokoh = validasi_tokoh(nama_tokoh, teks)

                if status_tokoh == "TIDAK_COCOK":
                    continue

                elif status_tokoh == "PERLU_KONTEKS":

                    if kalimat_korpus is None:
                        continue

                    # Cari kalimat dalam blok sumber yang sama.
                    blok_target = id_kalimat.rsplit("-K", 1)[0]

                    kalimat_blok = [
                        item
                        for item in kalimat_korpus
                        if item["id_blok"] == blok_target
                    ]

                    id_pendukung = periksa_konteks_tokoh(
                        nama_tokoh,
                        id_kalimat,
                        kalimat_blok
                    )

                    if id_pendukung is None:
                        continue

                    kalimat_pendukung = next(
                        (
                            item["teks_asli"]
                            for item in kalimat_blok
                            if item["id_kalimat"] == id_pendukung
                        ),
                        None
                    )

                    if kalimat_pendukung is None:
                        continue

                    if validasi_tokoh(
                        nama_tokoh,
                        kalimat_pendukung
                    ) != "COCOK":
                        continue

            jawaban = pilih_tanggal(pertanyaan, teks)

        elif tipe_jawaban == "PER":

            peristiwa = identifikasi_peristiwa_per(pertanyaan)

            if peristiwa is None:
                continue

            jawaban = ekstrak_pelaku(teks, peristiwa)

        elif tipe_jawaban == "LOC":

            # Pertanyaan lokasi kelahiran
            nama_tokoh = ambil_tokoh_pertanyaan(pertanyaan)

            if nama_tokoh is not None:

                status_subjek = cek_subjek_kelahiran(
                    nama_tokoh,
                    teks
                )

                if status_subjek != "COCOK":
                    continue

                jawaban = ekstrak_lokasi(teks)

            # Pertanyaan lokasi peristiwa lain
            else:
                jawaban = ekstrak_lokasi_peristiwa(
                    pertanyaan,
                    teks
                )

        elif tipe_jawaban == "NUM":
            jawaban = ekstrak_angka(pertanyaan, teks)    

        elif tipe_jawaban == "MISC":
            jawaban = ekstrak_misc(pertanyaan, teks)

        else:
            jawaban = None

        if jawaban is not None:
            return {
                "jawaban": jawaban,
                "id_kalimat": id_kalimat
            }

    return None