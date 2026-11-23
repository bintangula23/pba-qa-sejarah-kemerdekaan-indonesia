from answer_processing import ekstrak_angka

kasus_uji = [
    {
        "nama": "A - Jumlah anggota",
        "pertanyaan": "Berapa jumlah anggota panitia?",
        "teks": "Panitia terdiri dari 9 anggota pada tahun 1945.",
        "diharapkan": "9"
    },
    {
        "nama": "B - Jumlah korban",
        "pertanyaan": "Berapa korban yang tercatat?",
        "teks": "Peristiwa tersebut mengakibatkan 25 korban.",
        "diharapkan": "25"
    },
    {
        "nama": "C - Durasi hari",
        "pertanyaan": "Berapa hari pertempuran berlangsung?",
        "teks": "Pertempuran berlangsung selama 3 hari.",
        "diharapkan": "3"
    },
    {
        "nama": "D - Angka tahun bukan jumlah anggota",
        "pertanyaan": "Berapa jumlah anggota panitia?",
        "teks": "Panitia dibentuk pada tahun 1945.",
        "diharapkan": None
    },
    {
        "nama": "E - Bilangan ditulis dengan huruf",
        "pertanyaan": "Berapa jumlah anggota panitia?",
        "teks": "Panitia terdiri dari sembilan anggota.",
        "diharapkan": None
    }
]

for kasus in kasus_uji:
    hasil = ekstrak_angka(
        kasus["pertanyaan"],
        kasus["teks"]
    )

    status = "PASS" if hasil == kasus["diharapkan"] else "FAIL"

    print(f"\n{kasus['nama']}")
    print("Hasil      :", hasil)
    print("Diharapkan :", kasus["diharapkan"])
    print("Status     :", status)