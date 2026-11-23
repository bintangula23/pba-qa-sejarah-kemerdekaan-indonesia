from answer_processing import ekstrak_lokasi

kasus_uji = [
    {
        "nama": "A - Lokasi satu kata",
        "teks": "Fatmawati lahir pada 5 Februari 1923 di Bengkulu.",
        "diharapkan": "Bengkulu"
    },
    {
        "nama": "B - Lokasi dua kata",
        "teks": "Tokoh tersebut lahir di Sumatera Barat.",
        "diharapkan": "Sumatera Barat"
    },
    {
        "nama": "C - Variasi kata dilahirkan",
        "teks": "Tokoh tersebut dilahirkan di Jawa Timur.",
        "diharapkan": "Jawa Timur"
    },
    {
        "nama": "D - Tidak ada lokasi",
        "teks": "Fatmawati lahir pada 5 Februari 1923.",
        "diharapkan": None
    }
]

for kasus in kasus_uji:
    hasil = ekstrak_lokasi(kasus["teks"])

    status = (
        "PASS"
        if hasil == kasus["diharapkan"]
        else "FAIL"
    )

    print(f"\n{kasus['nama']}")
    print("Hasil      :", hasil)
    print("Diharapkan :", kasus["diharapkan"])
    print("Status     :", status)