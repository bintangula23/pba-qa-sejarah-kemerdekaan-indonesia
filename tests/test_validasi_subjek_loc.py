from validasi_tokoh import cek_subjek_kelahiran
from answer_processing import ekstrak_lokasi

pertanyaan_tokoh = "Fatmawati"

kasus_uji = [
    {
        "nama": "A - Tokoh yang berbeda",
        "teks": "Achmad Soebardjo dilahirkan di Teluk Jambe.",
        "diharapkan": None
    },
    {
        "nama": "B - Tokoh yang sesuai",
        "teks": "Fatmawati lahir pada 5 Februari 1923 di Bengkulu.",
        "diharapkan": "Bengkulu"
    },
    {
        "nama": "C - Tokoh lain",
        "teks": "Soekarno dilahirkan di Surabaya.",
        "diharapkan": None
    }
]

for kasus in kasus_uji:
    status = cek_subjek_kelahiran(
        pertanyaan_tokoh,
        kasus["teks"]
    )

    if status == "COCOK":
        jawaban = ekstrak_lokasi(kasus["teks"])
    else:
        jawaban = None

    hasil = "PASS" if jawaban == kasus["diharapkan"] else "FAIL"

    print(f"\n{kasus['nama']}")
    print("Status subjek :", status)
    print("Jawaban      :", jawaban)
    print("Diharapkan   :", kasus["diharapkan"])
    print("Hasil uji    :", hasil)