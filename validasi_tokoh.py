"""Validasi identitas dan konteks kelahiran berbasis pola
"""
import re
from question_processing import normalize_question

POLA_NAMA = r"(?:[A-Z][a-z]+|[A-Z]{2,}|[A-Z][a-z]*\.)(?:\s+(?:[A-Z][a-z]+|[A-Z]{2,}|[A-Z][a-z]*\.))*"
POLA_KELAHIRAN = r"\b(?:lahir|dilahirkan)\b"

def nama_sesuai(nama_pertanyaan, nama_sumber):
    return normalize_question(nama_pertanyaan) == normalize_question(nama_sumber)

def validasi_tokoh(nama_tokoh, kalimat):
    pola = rf"\b((?i:ia|dia|beliau)|{POLA_NAMA})\s+(?i:lahir|dilahirkan)\b"
    subjek = [m.group(1) for m in re.finditer(pola, kalimat)]
    if not subjek:
        return "PERLU_KONTEKS"
    status = [
        "PERLU_KONTEKS" if s.casefold() in {"ia", "dia", "beliau"}
        else "COCOK" if nama_sesuai(nama_tokoh, s) else "TIDAK_COCOK"
        for s in subjek
    ]
    if "TIDAK_COCOK" in status:
        return "TIDAK_COCOK"
    return "COCOK" if "COCOK" in status else "PERLU_KONTEKS"

def cek_subjek_kelahiran(nama_tokoh, teks):
    """Antarmuka lama untuk LOC; memakai implementasi yang sama dengan DATE."""
    return validasi_tokoh(nama_tokoh, teks)

def periksa_konteks_tokoh(nama_tokoh, id_kalimat, kalimat_blok):
    """Cari bukti identitas pada maksimal tiga kalimat sebelumnya, satu blok."""
    posisi = next((i for i, item in enumerate(kalimat_blok)
                   if item["id_kalimat"] == id_kalimat), None)
    if posisi is None:
        return None
    for item in reversed(kalimat_blok[max(0, posisi - 3):posisi]):
        teks = item["teks_asli"]
        if re.search(r"\b(?:bertemu(?:\s+dengan)?|menemui)\b", teks, re.I):
            return None
        status = validasi_tokoh(nama_tokoh, teks)
        if status == "TIDAK_COCOK":
            return None
        if status == "COCOK":
            return item["id_kalimat"]
    return None

def ambil_tokoh_pertanyaan(pertanyaan):
    """Nama dari pertanyaan lokasi kelahiran."""
    m = re.fullmatch(r"\s*di\s*mana(?:kah)?\s+(.+?)\s+(?:lahir|dilahirkan)\s*\??\s*", pertanyaan, re.I)
    return m.group(1).strip() if m else None
