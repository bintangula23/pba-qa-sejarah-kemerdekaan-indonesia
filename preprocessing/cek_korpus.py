import json
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[1]

CORPUS_FILE = (
    BASE_DIR / "data" / "raw" / "korpus_sejarah_indonesia_aktif.json"
)

with open(CORPUS_FILE, encoding="utf-8") as f:
        data = json.load(f)

print("Jumlah dokumen:", len(data))
for d in data:
    jumlah_kata = len(d["teks"].split())
    print(d["id"], d["judul"], "-", jumlah_kata, "kata")

print("Total kata:", sum(len(d["teks"].split()) for d in data))