from question_processing import process_question
from passage_retrieval import cari
from answer_processing import ambil_jawaban

pertanyaan = (
    "Siapa komandan pasukan Britania yang tewas "
    "dalam baku tembak pada 30 Oktober 1945 di Surabaya?"
)

jawaban_acuan = "Brigadir A. W. S. Mallaby"
id_acuan = "D13-B0002-K002"

print("=== EVALUASI TERPADU PERTEMPURAN SURABAYA ===")

# Tahap 1: Question Processing
info = process_question(pertanyaan)

print("\n1. QUESTION PROCESSING")
print("Pertanyaan :", pertanyaan)
print("Tipe       :", info.get("answer_type"))

# Tahap 2: Passage Retrieval
kandidat = cari(pertanyaan, k=20)

print("\n2. PASSAGE RETRIEVAL")
print("Jumlah kandidat:", len(kandidat))

peringkat_sumber = None

for peringkat, item in enumerate(kandidat, start=1):
    if item["id_kalimat"] == id_acuan:
        peringkat_sumber = peringkat
        break

print("Peringkat sumber acuan:", peringkat_sumber)

print("\n3. KANDIDAT TERATAS")

for peringkat, item in enumerate(kandidat[:5], start=1):
    print(f"\nRank {peringkat}")
    print("ID    :", item["id_kalimat"])
    print("Skor  :", item.get("skor"))
    print("Teks  :", item["teks_asli"])

# Tahap 3: Answer Processing
hasil = ambil_jawaban(info, kandidat)

print("\n4. ANSWER PROCESSING")
print("Hasil :", hasil)
print("Acuan :", jawaban_acuan)

if hasil is not None:
    jawaban = hasil.get("jawaban")
    id_sumber = hasil.get("id_kalimat")
else:
    jawaban = None
    id_sumber = None

print("\n5. HASIL EVALUASI")

if jawaban == jawaban_acuan:
    print("Jawaban : PASS")
else:
    print("Jawaban : FAIL")

if id_sumber == id_acuan:
    print("Sumber  : PASS")
else:
    print("Sumber  : FAIL")