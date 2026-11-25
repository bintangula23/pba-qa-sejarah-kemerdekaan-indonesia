import json

from question_processing import process_question
from answer_processing import ambil_jawaban

# baca korpus untuk validasi konteks
with open("korpus_kalimat_final.json", encoding="utf-8") as file:
    data = json.load(file)

kalimat_korpus = data["kalimat"]
kasus_uji = [
    {
        "tipe": "DATE",
        "pertanyaan": "Kapan Mohammad Hatta lahir?",
        "kandidat": [
            {
                "id_kalimat": "D08-B0004-K003",
                "teks_asli": (
                    "Ia lahir dengan nama Muhammad Athar "
                    "pada tanggal 12 Agustus 1902."
                )
            }
        ],
        "diharapkan": "12 Agustus 1902"
    },
    {
        "tipe": "PER",
        "pertanyaan": (
            "Siapa yang memberikan julukan Piagam Jakarta "
            "kepada naskah usulan Mukadimah Undang-Undang Dasar Indonesia?"
        ),
        "kandidat": [
            {
                "id_kalimat": "D04-B0017-K001",
                "teks_asli": (
                    'Naskah tersebut diberi julukan '
                    '"Piagam Jakarta" oleh Mohammad Yamin.'
                )
            }
        ],
        "diharapkan": "Mohammad Yamin"
    },
    {
        "tipe": "LOC",
        "pertanyaan": "Di mana Fatmawati dilahirkan?",
        "kandidat": [
            {
                "id_kalimat": "D11-B0002-K001",
                "teks_asli": (
                    "Fatmawati lahir pada 5 Februari 1923 "
                    "di Bengkulu dari pasangan Hasan Din dan Siti Chadijah."
                )
            }
        ],
        "diharapkan": "Bengkulu"
    },
    {
        "tipe": "NUM",
        "pertanyaan": "Berapa jumlah anggota panitia?",
        "kandidat": [
            {
                "id_kalimat": "TEST-K002",
                "teks_asli": "Panitia tersebut terdiri dari 9 anggota."
            }
        ],
        "diharapkan": "9"
    }
]

jumlah_pass = 0

for kasus in kasus_uji:
    info = process_question(kasus["pertanyaan"])

    hasil = ambil_jawaban(
        info,
        kasus["kandidat"],
        kalimat_korpus=kalimat_korpus
    )

    jawaban = hasil["jawaban"] if hasil else None

    status = "PASS" if jawaban == kasus["diharapkan"] else "FAIL"

    if status == "PASS":
        jumlah_pass += 1

    print(f"\n=== {kasus['tipe']} ===")
    print("Jawaban    :", jawaban)
    print("Diharapkan :", kasus["diharapkan"])
    print("Status     :", status)

print(f"\nTOTAL: {jumlah_pass}/{len(kasus_uji)} PASS")