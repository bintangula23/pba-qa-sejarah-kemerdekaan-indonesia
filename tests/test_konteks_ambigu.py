from validasi_tokoh import periksa_konteks_tokoh

kalimat_blok = [
    {
        "id_kalimat": "TEST-B001-K001",
        "teks_asli": "Mohammad Hatta bertemu dengan Rafiah."
    },
    {
        "id_kalimat": "TEST-B001-K002",
        "teks_asli": "Ia lahir pada 5 Januari 1900."
    }
]

hasil = periksa_konteks_tokoh(
    nama_tokoh="Mohammad Hatta",
    id_kalimat="TEST-B001-K002",
    kalimat_blok=kalimat_blok
)

print("Kalimat pendukung ditemukan:", hasil)

if hasil is not None:
    print("PERINGATAN: Nama ditemukan, tetapi rujukan 'Ia' masih ambigu.")
else:
    print("Tidak ditemukan konteks pendukung.")