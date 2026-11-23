from question_processing import process_question
from passage_retrieval import cari
from answer_processing import ambil_jawaban

kasus_uji = [
    {
        "tipe": "DATE",
        "pertanyaan": "Kapan Mohammad Hatta lahir?",
        "jawaban_acuan": "12 Agustus 1902",
        "id_acuan": "D08-B0004-K003"
    },
    {
        "tipe": "PER",
        "pertanyaan": (
            "Siapa yang memberikan julukan Piagam Jakarta "
            "kepada naskah usulan Mukadimah Undang-Undang Dasar Indonesia?"
        ),
        "jawaban_acuan": "Mohammad Yamin",
        "id_acuan": "D04-B0017-K001"
    },
    {
        "tipe": "LOC",
        "pertanyaan": "Di mana Fatmawati dilahirkan?",
        "jawaban_acuan": "Bengkulu",
        "id_acuan": "D11-B0002-K001"
    }
]

for kasus in kasus_uji:
    pertanyaan = kasus["pertanyaan"]

    info = process_question(pertanyaan)
    kandidat = cari(pertanyaan, k=20)
    hasil = ambil_jawaban(info, kandidat)

    jawaban = hasil["jawaban"] if hasil else None
    id_sumber = hasil["id_kalimat"] if hasil else None

    status = (
        "PASS"
        if (
            jawaban == kasus["jawaban_acuan"]
            and id_sumber == kasus["id_acuan"]
        )
        else "FAIL"
    )

    print(f"\n=== {kasus['tipe']} ===")
    print("Pertanyaan :", pertanyaan)
    print("Jawaban    :", jawaban)
    print("ID sumber  :", id_sumber)
    print("Acuan      :", kasus["jawaban_acuan"])
    print("Status     :", status)