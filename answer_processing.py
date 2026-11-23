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
    cek_subjek_kelahiran
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

def pilih_tanggal(pertanyaan, teks):
    """
    Memilih tanggal berdasarkan peristiwa dan konteks klausa dalam kalimat sumber.
    """

    tanggal_ditemukan = ekstrak_tanggal(teks)

    if not tanggal_ditemukan:
        return None

    kata_peristiwa = [
        "lahir",
        "meninggal",
        "dilantik",
        "dibentuk",
        "didirikan",
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

def ekstrak_pelaku(teks):
    """
    Mengekstraksi kandidat nama pelaku dari kalimat aktif atau pasif sederhana.
    """

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

def ekstrak_angka(pertanyaan, teks):
    """
    Mengekstraksi jumlah numerik berdasarkan kata satuan yang muncul dalam pertanyaan.
    """

    satuan = [
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
                return hasil.group(1)

    return None

def ambil_jawaban(info_pertanyaan, kandidat):
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
            jawaban = pilih_tanggal(pertanyaan, teks)

        elif tipe_jawaban == "PER":
            jawaban = ekstrak_pelaku(teks)

        elif tipe_jawaban == "LOC":
            nama_tokoh = ambil_tokoh_pertanyaan(pertanyaan)

            if nama_tokoh is None:
                continue

            status_subjek = cek_subjek_kelahiran(nama_tokoh, teks)

            if status_subjek != "COCOK":
                continue

            jawaban = ekstrak_lokasi(teks)

        elif tipe_jawaban == "NUM":
            jawaban = ekstrak_angka(pertanyaan, teks)    

        else:
            jawaban = None

        if jawaban is not None:
            return {
                "jawaban": jawaban,
                "id_kalimat": id_kalimat
            }

    return None