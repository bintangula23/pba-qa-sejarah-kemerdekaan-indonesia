import json

from question_processing import process_question
from passage_retrieval import cari
from answer_processing import ambil_jawaban

kasus_uji = [
    {
        "id": "D01",
        "pertanyaan": (
            "Sumber daya alam apakah yang menjadi sasaran utama "
            "Jepang dalam pendudukannya di Hindia Belanda?"
        ),
        "acuan": "Minyak bumi"
    },
    {
        "id": "D02",
        "pertanyaan": "Dimana masa persidangan pertama BPUPK dibuka?",
        "acuan": "Gedung Chuo Sangi In di Jakarta"
    },
        {
        "id": "D03",
        "pertanyaan": "Siapa yang ditunjuk PPKI sebagai wakil presiden pertama Indonesia?",
        "acuan": "Mohammad Hatta"
    },
    {
        "id": "D04",
        "pertanyaan": (
            'Siapa yang memberikan julukan "Piagam Jakarta" kepada '
            'naskah usulan Mukadimah Undang-Undang Dasar Indonesia?'
        ),
        "acuan": "Mohammad Yamin"
    },
    {
        "id": "D05",
        "pertanyaan": "Pada tanggal berapa Soekarno dan Mohammad Hatta dibawa ke Rengasdengklok?",
        "acuan": "16 Agustus 1945"
    },
    {
        "id": "D06",
        "pertanyaan": "Apa nama kapal tempat Jepang secara resmi menyerah kepada Sekutu?",
        "acuan": "USS Missouri"
    },
    {
        "id": "D07",
        "pertanyaan": "Ke kota manakah Soekarno diasingkan bersama keluarganya pada tahun 1934?",
        "acuan": "Ende"
    },
    {
        "id": "D08",
        "pertanyaan": "Kapan Mohammad Hatta lahir?",
        "acuan": "12 Agustus 1902"
    },
    {
        "id": "D09",
        "pertanyaan": "Pada tahun berapa Sutan Sjahrir mendirikan Partai Sosialis Indonesia?",
        "acuan": "1948"
    },
    {
        "id": "D10",
        "pertanyaan": (
            "Pada tanggal berapa Soebardjo dilantik sebagai "
            "Menteri Luar Negeri pada Kabinet Presidensial?"
        ),
        "acuan": "18 Agustus 1945"
    },
    {
        "id": "D11",
        "pertanyaan": "Dimana Fatmawati dilahirkan?",
        "acuan": "Bengkulu"
    },
    {
        "id": "D12",
        "pertanyaan": "Siapa yang terpilih menjadi panglima Tentara Keamanan Rakyat?",
        "acuan": "Sudirman"
    },
    {
        "id": "D13",
        "pertanyaan": (
            "Siapa komandan pasukan Britania yang tewas dalam "
            "baku tembak pada 30 Oktober 1945 di Surabaya?"
        ),
        "acuan": "Brigadir A. W. S. Mallaby"
    },
    {
        "id": "D14",
        "pertanyaan": (
            "Siapa anggota milisi BRI yang meledakkan gudang "
            "amunisi di Dayeuhkolot dengan dinamit?"
        ),
        "acuan": "Muhammad Toha"
    },
    {
        "id": "D15",
        "pertanyaan": (
            "Di daerah mana pasukan Belanda melakukan "
            "pendaratan dalam Operasi Produk Utara?"
        ),
        "acuan": "Pasir Poetih, Situbondo"
    },
    {
        "id": "D16",
        "pertanyaan": (
            "Operasi militer Belanda yang dikenal dengan sebutan "
            "Operasi Gagak dilancarkan pada bulan apa?"
        ),
        "acuan": "Desember 1948"
    },
    {
        "id": "D17",
        "pertanyaan": (
            "Siapakah Letkol yang memimpin pasukan dari sektor barat "
            "hingga ke batas Malioboro dalam Serangan Umum 1 Maret 1949?"
        ),
        "acuan": "Letkol Soeharto"
    },
    {
        "id": "D18",
        "pertanyaan": (
            "Siapa yang bertindak sebagai perantara pada "
            "tahap awal Perundingan Linggajati?"
        ),
        "acuan": "Lord Killearn"
    },
    {
        "id": "D19",
        "pertanyaan": (
            "Dimana kapal USS Renville berlabuh saat "
            "negosiasi Perjanjian Renville berlangsung?"
        ),
        "acuan": "Teluk Jakarta"
    },
    {
        "id": "D20",
        "pertanyaan": (
            "Siapa kepala delegasi Republik Indonesia "
            "dalam perundingan Roem-Roijen?"
        ),
        "acuan": "Mohamad Roem"
    },
    {
        "id": "D21",
        "pertanyaan": "Berapa jumlah negara bagian Republik Indonesia Serikat?",
        "acuan": "16 negara bagian"
    }
]

with open("korpus_kalimat_final.json", encoding="utf-8") as file:
    data = json.load(file)

kalimat_korpus = data["kalimat"]

print("=== EVALUASI RESMI ANSWER PROCESSING ===")

for kasus in kasus_uji:

    pertanyaan = kasus["pertanyaan"]

    info = process_question(pertanyaan)
    kandidat = cari(pertanyaan, k=20)

    hasil = ambil_jawaban(
        info,
        kandidat,
        kalimat_korpus=kalimat_korpus
    )

    jawaban = hasil["jawaban"] if hasil else None
    id_sumber = hasil["id_kalimat"] if hasil else None

    if jawaban is None:
        status = "TIDAK DIJAWAB"
    elif str(jawaban).strip().casefold() == kasus["acuan"].strip().casefold():
        status = "COCOK PERSIS"
    else:
        status = "PERLU CEK VARIASI"

    print(f"\n=== {kasus['id']} ===")
    print("Pertanyaan :", pertanyaan)
    print("Tipe       :", info.get("answer_type"))
    print("Jawaban    :", jawaban)
    print("Acuan      :", kasus["acuan"])
    print("ID Sumber  :", id_sumber)
    print("Status     :", status)