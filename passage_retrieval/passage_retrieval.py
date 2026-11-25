import json
import math
import re
from collections import Counter
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[1]

CORPUS_FILE = (
    BASE_DIR / "data" / "processed" / "korpus_kalimat_final.json"
)

# 1. Baca korpus final
with open(CORPUS_FILE, encoding="utf-8") as f:
    data = json.load(f)

kalimat = data["kalimat"]

# 2. Tokenisasi: huruf kecil, ambil huruf dan angka, buang tanda baca
def tokenisasi(teks):
    return re.findall(r"[a-z0-9]+", teks.lower())


# 3. Bangun index BM25 (sekali saja saat file dijalankan)
dokumen_token = [tokenisasi(k["teks_cari"]) for k in kalimat]
N = len(dokumen_token)
panjang = [len(t) for t in dokumen_token]
rata_panjang = sum(panjang) / N
tf = [Counter(t) for t in dokumen_token]

df = Counter()
for t in dokumen_token:
    df.update(set(t))
idf = {kata: math.log(1 + (N - n + 0.5) / (n + 0.5)) for kata, n in df.items()}

K1 = 1.5
B = 0.75


# 4. Skor BM25 satu kalimat terhadap satu pertanyaan
def skor_bm25(token_pertanyaan, i):
    skor = 0.0
    for kata in token_pertanyaan:
        if kata not in tf[i]:
            continue
        f = tf[i][kata]
        pembilang = f * (K1 + 1)
        penyebut = f + K1 * (1 - B + B * panjang[i] / rata_panjang)
        skor += idf[kata] * pembilang / penyebut
    return skor


# 5. Fungsi utama: cari k kalimat paling relevan
def cari(pertanyaan, k=5):
    token = tokenisasi(pertanyaan)
    hasil = []
    for i in range(N):
        s = skor_bm25(token, i)
        if s > 0:
            hasil.append((s, i))
    hasil.sort(reverse=True)
    return [
        {
            "id_kalimat": kalimat[i]["id_kalimat"],
            "skor": round(s, 4),
            "teks_asli": kalimat[i]["teks_asli"],
        }
        for s, i in hasil[:k]
    ]


# 6. Tes dengan soal-soal
if __name__ == "__main__":
    soal = [
        "Ke kota manakah Soekarno diasingkan bersama keluarganya pada tahun 1934?",
        "Pada tanggal berapa Soebardjo dilantik sebagai Menteri Luar Negeri pada Kabinet Presidensial?",
        "Siapa anggota milisi BRI yang meledakkan gudang amunisi di Dayeuhkolot dengan dinamit?",
        "Siapa kepala delegasi Republik Indonesia dalam perundingan Roem-Roijen?",
    ]
    for s in soal:
        print("\nPERTANYAAN:", s)
        for h in cari(s, k=3):
            print(" ", h["id_kalimat"], h["skor"], "|", h["teks_asli"][:110])