import json
from pathlib import Path


def muat_data(nama_file):
    with open(nama_file, encoding="utf-8") as f:
        data = json.load(f)
    return data["kalimat"], data["metadata"]["aturan_alias"]


def proses_pertanyaan(pertanyaan, alias):
    # Penampung modul Saskia.
    # Sambungkan normalisasi bersama, klasifikasi, dan tipe jawaban.
    raise NotImplementedError("Modul pemrosesan pertanyaan belum disambungkan.")


def cari_kandidat(info_pertanyaan, korpus):
    # Penampung modul Raisya.
    # Cari pada teks_cari; pertahankan ID dan teks_asli kandidat.
    raise NotImplementedError("Modul pencarian belum disambungkan.")


def ambil_jawaban(info_pertanyaan, kandidat):
    # Penampung modul Kak Bintang.
    # Ambil jawaban dari teks_asli kandidat.
    # Keluaran: {"jawaban": "...", "id_kalimat": "..."} atau None.
    raise NotImplementedError("Modul pengambilan jawaban belum disambungkan.")


def jawab_pertanyaan(pertanyaan, korpus, alias):
    info = proses_pertanyaan(pertanyaan, alias)
    kandidat = cari_kandidat(info, korpus)

    if not kandidat:
        return None

    return ambil_jawaban(info, kandidat)


def main():
    folder = Path(__file__).resolve().parent
    korpus, alias = muat_data(folder / "korpus_kalimat_final.json")

    print("Chatbot QA Sejarah Indonesia")
    print("Jumlah kalimat:", len(korpus))
    print("Ketik 'keluar' untuk berhenti.")

    while True:
        try:
            pertanyaan = input("\nKamu: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nSelesai.")
            break

        if pertanyaan.lower() in {"keluar", "exit", "quit"}:
            print("Selesai.")
            break

        if not pertanyaan:
            continue

        try:
            hasil = jawab_pertanyaan(pertanyaan, korpus, alias)
        except NotImplementedError as pesan:
            print("Bot:", pesan)
            continue

        if hasil and hasil.get("jawaban"):
            print("Bot:", hasil["jawaban"])
            print("ID bukti:", hasil.get("id_kalimat"))
        else:
            print("Bot: Jawaban belum ditemukan dalam korpus.")


if __name__ == "__main__":
    main()
