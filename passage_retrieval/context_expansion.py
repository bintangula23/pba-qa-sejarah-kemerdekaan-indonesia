def perluas_konteks(kandidat, kalimat_korpus):
    """
    Memperluas kandidat BM25 menggunakan kalimat yang berasal dari blok dokumen yang sama.
    """

    # Buat indeks ID kalimat
    indeks_kalimat = {
        item["id_kalimat"]: item
        for item in kalimat_korpus
    }

    # Kumpulkan ID blok dari kandidat BM25
    blok_terpilih = []

    for item in kandidat:
        id_kalimat = item["id_kalimat"]

        if id_kalimat not in indeks_kalimat:
            continue

        id_blok = indeks_kalimat[id_kalimat]["id_blok"]

        if id_blok not in blok_terpilih:
            blok_terpilih.append(id_blok)

    # Tambahkan kalimat dari blok yang terpilih
    hasil = []
    id_sudah_dipakai = set()

    for id_blok in blok_terpilih:
        for item in kalimat_korpus:
            if item["id_blok"] != id_blok:
                continue

            id_kalimat = item["id_kalimat"]

            if id_kalimat in id_sudah_dipakai:
                continue

            hasil.append({
                "id_kalimat": id_kalimat,
                "teks_asli": item["teks_asli"]
            })

            id_sudah_dipakai.add(id_kalimat)

    return hasil