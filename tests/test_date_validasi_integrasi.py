from answer_processing import ambil_jawaban

info = {
    "original_question": "Kapan Mohammad Hatta lahir?",
    "answer_type": "DATE"
}

kandidat = [
    {
        "id_kalimat": "TEST-TOKOH-LAIN",
        "teks_asli": "Rafiah lahir pada 5 Januari 1900."
    },
    {
        "id_kalimat": "TEST-TOKOH-BENAR",
        "teks_asli": "Mohammad Hatta lahir pada 12 Agustus 1902."
    }
]

hasil = ambil_jawaban(info, kandidat)

print("=== UJI VALIDASI DATE TERPADU ===")
print("Hasil:", hasil)

jawaban_diharapkan = {
    "jawaban": "12 Agustus 1902",
    "id_kalimat": "TEST-TOKOH-BENAR"
}

print("Diharapkan:", jawaban_diharapkan)

if hasil == jawaban_diharapkan:
    print("Status: PASS")
else:
    print("Status: FAIL")

import json

from question_processing import process_question
from passage_retrieval import cari

print("\n=== UJI DATE DENGAN KONTEKS KORPUS ===")

with open("korpus_kalimat_final.json", encoding="utf-8") as file:
    data = json.load(file)

kalimat_korpus = data["kalimat"]

pertanyaan_hatta = "Kapan Mohammad Hatta lahir?"

info_hatta = process_question(pertanyaan_hatta)
kandidat_hatta = cari(pertanyaan_hatta, k=20)

hasil_hatta = ambil_jawaban(
    info_hatta,
    kandidat_hatta,
    kalimat_korpus=kalimat_korpus
)

print("Pertanyaan :", pertanyaan_hatta)
print("Hasil      :", hasil_hatta)

jawaban_acuan = {
    "jawaban": "12 Agustus 1902",
    "id_kalimat": "D08-B0004-K003"
}

print("Diharapkan :", jawaban_acuan)

if hasil_hatta == jawaban_acuan:
    print("Status     : PASS")
else:
    print("Status     : FAIL")