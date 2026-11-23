from answer_processing import ekstrak_lokasi

kasus_uji = [
    {
        "nama": "A - Tempat tinggal bukan tempat lahir",
        "teks": (
            "Fatmawati lahir pada 5 Februari 1923 "
            "dan kemudian tinggal di Jakarta."
        ),
        "diharapkan": None
    },
    {
        "nama": "B - Lokasi kelahiran dan tempat tinggal",
        "teks": (
            "Fatmawati lahir di Bengkulu "
            "dan kemudian tinggal di Jakarta."
        ),
        "diharapkan": "Bengkulu"
    },
    {
        "nama": "C - Lokasi kelahiran tidak disebutkan",
        "teks": (
            "Fatmawati lahir pada 5 Februari 1923."
        ),
        "diharapkan": None
    },
    {
        "nama": "D - Kalimat dari korpus asli",
        "teks": (
            "Fatmawati lahir pada 5 Februari 1923 "
            "di Bengkulu dari pasangan Hasan Din dan Siti Chadijah."
        ),
        "diharapkan": "Bengkulu"
    }
]

for kasus in kasus_uji:
    hasil = ekstrak_lokasi(kasus["teks"])

    status = "PASS" if hasil == kasus["diharapkan"] else "FAIL"

    print(f"\n{kasus['nama']}")
    print("Hasil      :", hasil)
    print("Diharapkan :", kasus["diharapkan"])
    print("Status     :", status)