import json

with open("korpus_sejarah_indonesia_aktif.json", encoding="utf-8") as f:
        data = json.load(f)

print("Jumlah dokumen:", len(data))
for d in data:
    jumlah_kata = len(d["teks"].split())
    print(d["id"], d["judul"], "-", jumlah_kata, "kata")

print("Total kata:", sum(len(d["teks"].split()) for d in data))