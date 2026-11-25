from answer_processing import ambil_jawaban

info = {
    "original_question": (
        "Siapa yang memberikan julukan Piagam Jakarta?"
    ),
    "answer_type": "PER"
}

kandidat = [
    {
        "id_kalimat": "TEST-SALAH",
        "teks_asli": (
            "Komandan pasukan Britania, "
            "Brigadir A. W. S. Mallaby "
            "tewas dalam baku tembak."
        )
    },
    {
        "id_kalimat": "TEST-BENAR",
        "teks_asli": (
            "Naskah tersebut diberi julukan "
            "Piagam Jakarta oleh Mohammad Yamin."
        )
    }
]

hasil = ambil_jawaban(info, kandidat)

print("=== UJI NEGATIF PER ===")
print("Pertanyaan :", info["original_question"])
print("Hasil      :", hasil)
print("Diharapkan : Mohammad Yamin")

if hasil and hasil["jawaban"] == "Mohammad Yamin":
    print("Status     : PASS")
else:
    print("Status     : FAIL")

print("\n=== UJI HUBUNGAN PELAKU DAN PERISTIWA ===")

info_kedua = {
    "original_question": (
        "Siapa yang memberikan julukan Piagam Jakarta?"
    ),
    "answer_type": "PER"
}

kandidat_kedua = [
    {
        "id_kalimat": "TEST-DUA-PERISTIWA",
        "teks_asli": (
            "Mohammad Yamin memberikan penjelasan, "
            "sedangkan naskah Piagam Jakarta "
            "diberi julukan oleh Soekarno."
        )
    }
]

hasil_kedua = ambil_jawaban(info_kedua, kandidat_kedua)

print("Hasil      :", hasil_kedua)
print("Diharapkan : Soekarno")

if hasil_kedua and hasil_kedua["jawaban"] == "Soekarno":
    print("Status     : PASS")
else:
    print("Status     : FAIL")

print("\n=== UJI NEGATIF KOMANDAN TEWAS ===")

info_ketiga = {
    "original_question": (
        "Siapa komandan pasukan Britania yang tewas "
        "dalam baku tembak?"
    ),
    "answer_type": "PER"
}

kandidat_ketiga = [
    {
        "id_kalimat": "TEST-HUBUNGAN-AMBIGU",
        "teks_asli": (
            "Komandan pasukan Britania memberikan arahan "
            "kepada pasukan, sedangkan "
            "Brigadir A. W. S. Mallaby tewas "
            "dalam baku tembak."
        )
    }
]

hasil_ketiga = ambil_jawaban(info_ketiga, kandidat_ketiga)

print("Hasil      :", hasil_ketiga)
print("Diharapkan : None")

if hasil_ketiga is None:
    print("Status     : PASS")
else:
    print("Status     : FAIL")