import re

def validasi_tokoh(nama_tokoh, kalimat):
    pola = r"\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*|Ia)\s+lahir\b"

    hasil = re.search(pola, kalimat)

    if hasil is None:
        return "PERLU_KONTEKS"

    subjek = hasil.group(1)

    if subjek.lower() == nama_tokoh.lower():
        return "COCOK"

    if subjek.lower() in ["ia", "dia", "beliau"]:
        return "PERLU_KONTEKS"

    return "TIDAK_COCOK"

def periksa_konteks_tokoh(nama_tokoh, id_kalimat, kalimat_blok):
    """
    Mencari penyebutan nama tokoh pada kalimat sebelumnya dalam blok yang sama.

    Return:
        ID kalimat pendukung jika ditemukan, atau None jika tidak ditemukan.
    """

    indeks_target = None

    # Cari posisi kalimat target
    for indeks, item in enumerate(kalimat_blok):
        if item["id_kalimat"] == id_kalimat:
            indeks_target = indeks
            break

    if indeks_target is None:
        return None

    # Periksa maksimal 3 kalimat sebelumnya
    awal = max(0, indeks_target - 3)

    for sebelumnya in reversed(kalimat_blok[awal:indeks_target]):
        teks = sebelumnya["teks_asli"]

        if nama_tokoh.lower() in teks.lower():
            return sebelumnya["id_kalimat"]

    return None

def cek_subjek_kelahiran(nama_tokoh, teks):
    """
    Memeriksa apakah subjek peristiwa kelahiran
    sesuai dengan nama tokoh yang ditanyakan.

    Return:
        COCOK, TIDAK_COCOK, atau PERLU_KONTEKS.
    """

    pola = (
        r"\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)"
        r"\s+(?:lahir|dilahirkan)\b"
    )

    hasil = re.search(pola, teks)

    if hasil is None:
        return "PERLU_KONTEKS"

    subjek = hasil.group(1)

    if subjek.lower() == nama_tokoh.lower():
        return "COCOK"

    if subjek.lower() in ["ia", "dia", "beliau"]:
        return "PERLU_KONTEKS"

    return "TIDAK_COCOK"

def ambil_tokoh_pertanyaan(pertanyaan):
    """
    Mengambil nama tokoh dari pertanyaan lokasi kelahiran dengan susunan 'Di mana [tokoh] lahir/dilahirkan?'.
    """

    pola = (
        r"^\s*di\s+mana\s+(.+?)\s+"
        r"(?:lahir|dilahirkan)\s*\?$"
    )

    hasil = re.search(pola, pertanyaan, flags=re.IGNORECASE)

    if hasil:
        return hasil.group(1).strip()

    return None