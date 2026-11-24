import json

from validasi_tokoh import periksa_konteks_tokoh

nama_tokoh = "Mohammad Hatta"
id_target = "D08-B0004-K003"
blok_target = "D08-B0004"

with open("korpus_kalimat_final.json", encoding="utf-8") as file:
    data = json.load(file)

kalimat_korpus = data["kalimat"]

# Ambil kalimat dari blok yang sama
kalimat_blok = [
    item
    for item in kalimat_korpus
    if item["id_blok"] == blok_target
]

# Periksa penyebutan tokoh dalam kalimat sebelumnya
id_pendukung = periksa_konteks_tokoh(
    nama_tokoh,
    id_target,
    kalimat_blok
)

print("=== UJI KONTEKS DATE HATTA ===")
print("Tokoh             :", nama_tokoh)
print("Kalimat target    :", id_target)
print("Kalimat pendukung :", id_pendukung)

if id_pendukung is not None:
    for item in kalimat_blok:
        if item["id_kalimat"] == id_pendukung:
            print("Teks pendukung   :", item["teks_asli"])
            break

print(
    "Status            :",
    "PASS" if id_pendukung == "D08-B0004-K001" else "FAIL"
)