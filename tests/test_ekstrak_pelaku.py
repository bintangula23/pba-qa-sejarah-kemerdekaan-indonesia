from answer_processing import ekstrak_pelaku

kasus_uji = [
    {
        "nama": "A - Kalimat aktif",
        "teks": "Mohammad Yamin memberikan julukan Piagam Jakarta.",
        "diharapkan": "Mohammad Yamin"
    },
    {
        "nama": "B - Kalimat pasif",
        "teks": "Julukan Piagam Jakarta diberikan oleh Mohammad Yamin.",
        "diharapkan": "Mohammad Yamin"
    },
    {
        "nama": "C - Tidak ada pelaku yang sesuai pola",
        "teks": "Piagam Jakarta merupakan naskah bersejarah.",
        "diharapkan": None
    }
]

for kasus in kasus_uji:
    hasil = ekstrak_pelaku(kasus["teks"])

    status = "PASS" if hasil == kasus["diharapkan"] else "FAIL"

    print(f"\n{kasus['nama']}")
    print("Hasil      :", hasil)
    print("Diharapkan :", kasus["diharapkan"])
    print("Status     :", status)