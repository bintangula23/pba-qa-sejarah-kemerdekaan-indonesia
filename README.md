# Question Answering System — Sejarah Indonesia

Proyek akhir mata kuliah Pemrosesan Bahasa Alami (PBA).

Sistem Question Answering berbasis Information Retrieval
yang dirancang untuk menjawab pertanyaan factoid mengenai
sejarah Indonesia tanpa menggunakan Large Language Model (LLM).

Sistem mengimplementasikan tiga tahapan utama:
Question Processing, Passage Retrieval menggunakan BM25,
dan Answer Processing berbasis aturan.

Korpus utama terdiri dari 21 artikel sejarah Indonesia
yang telah melalui preprocessing dan menghasilkan
3.140 kalimat untuk proses retrieval.

## 1. Struktur Repository

```text
pba-qa-sejarah-indonesia/
├── preprocessing/
│   ├── Pemecah_Kalimat_Korpus.ipynb
│   ├── Normalisasi_Alias.ipynb
│   ├── Normalisasi_Tanggal_dan_Penanda_Soal.ipynb
│   └── cek_korpus.py
├── question_processing/
│   └── question_processing.py
├── passage_retrieval/
│   ├── passage_retrieval.py
│   └── context_expansion.py
├── answer_processing/
│   ├── answer_processing.py
│   ├── validasi_tokoh.py
│   └── README_ANSWER_PROCESSING.md
├── integration_evaluation/
│   ├── Chatbot_Kerangka.ipynb
│   └── Integrasi_Chatbot_Sejarah.ipynb
├── data/
│   ├── raw/
│   ├── processed/
│   └── dictionary/
├── results/
│   ├── baseline/
│   ├── arsip_pengujian/
│   └── normalized/
├── tests/
│   └── test_evaluasi_resmi.py
├── requirements.txt
├── .gitignore
└── README.md
```

| Folder | Deskripsi |
|---|---|
| preprocessing | Segmentasi kalimat, normalisasi alias, tanggal, dan validasi korpus |
| question_processing | Normalisasi dan klasifikasi pertanyaan |
| passage_retrieval | Tokenisasi, pembobotan BM25, dan ranking passage |
| answer_processing | Ekstraksi dan validasi jawaban |
| integration_evaluation | Integrasi sistem, chatbot, dan evaluasi |
| data | Korpus awal, korpus hasil preprocessing, dan kamus alias |
| results | Hasil pengujian dan eksperimen sistem |
| tests | Pengujian sistem QA |

## 2. Cara membaca korpus final

Struktur teratas berupa objek dengan field `metadata` dan `kalimat`.
Ambil daftar record melalui **`data["kalimat"]`**, bukan langsung dari `data`.

Contoh Python, dijalankan dari folder `NLP`:

```python
import json

with open("data/processed/korpus_kalimat_final.json", encoding="utf-8") as f:
    data = json.load(f)

kalimat = data["kalimat"]
alias = data["metadata"]["aturan_alias"]

print("Jumlah kalimat:", len(kalimat))  # 3140
print(kalimat[0]["id_kalimat"])
print(kalimat[0]["teks_asli"])
print(kalimat[0]["teks_cari"])
```

| Field | Arti/penggunaan |
| --- | --- |
| `id_kalimat` | ID unik, misalnya `D01-B0001-K001`: dokumen D01, blok B0001, potongan K001. Pertahankan saat mengirim kandidat antar modul. |
| `id_dokumen`, `judul_dokumen` | Artikel asal. |
| `id_bagian`, `judul_bagian` | Bagian artikel asal. |
| `id_blok` | Paragraf atau butir daftar asal. |
| `jenis_blok` | `paragraf` atau `butir_daftar`; sebagian potongan daftar bukan kalimat lengkap. |
| **`teks_cari`** | Teks untuk pencarian dan pembobotan. |
| **`teks_asli`** | Teks untuk POS/NER, ekstraksi jawaban, dan tampilan bukti. Kapitalisasi serta penulisan sumber tetap tersedia. |
| `awal_karakter_blok`, `akhir_karakter_blok` | Posisi pada teks blok: indeks Python mulai nol, akhir tidak termasuk. Bukan posisi pada `teks_cari`. |
| `url_sumber` | Pranala artikel sumber untuk ditampilkan bersama jawaban. |
| `layak_retrieval`, `indikasi_ejaan_historis` | Penanda seleksi/pemrosesan; tidak menjamin kebenaran fakta sejarah. |

`teks_asli` adalah teks blok hasil penyiapan korpus, bukan salinan mentah seluruh
halaman Wikipedia. Jangan menimpanya dengan hasil normalisasi.

## 3. Normalisasi pertanyaan

Pertanyaan pengguna perlu melalui aturan yang sama dengan `teks_cari`:

1. Jadikan huruf kecil dan rapikan spasi.
2. Terapkan kamus alias dari `data/dictionary/alias.json` atau `metadata.aturan_alias`.
3. Normalisasikan tanggal menjadi **`d bulan yyyy`**, misalnya `16/08/1945`
   dan `1945-08-16` menjadi `16 agustus 1945`.

Contoh alias: `sukarno` → `soekarno`, `syahrir` → `sjahrir`, dan
`moh. hatta` → `mohammad hatta`. Cocokkan alias panjang lebih dulu, dengan batas
token agar tidak mengganti bagian di dalam kata lain. Penulisan pada bukti jawaban
tetap mengikuti `teks_asli`.

Aturan tanggal saat ini:

- Tanggal angka dengan urutan hari-bulan-tahun dan ISO dikenali.
- Nama bulan, singkatan, serta variasi yang terdaftar disamakan.
- Tanggal tanpa tahun tidak diberi tahun tambahan.
- Bentuk bulan-tahun tanpa hari, seperti `des 1941`, belum diperluas oleh fungsi ini.
- Rentang yang dikenali, jam, dan angka ribuan dipertahankan.
- Tanggal yang tidak sah secara kalender dipertahankan untuk ditinjau.

**Kode fungsi pemecah kalimat dan normalisasi belum disertakan dalam ZIP ini.**
Gunakan notebook terbaru milik Namel untuk menyambungkan fungsi normalisasi
pertanyaan. Pastikan format keluarannya `d bulan yyyy` seperti korpus final.

## 4. Bagian kerja anggota

| Anggota | Bagian kerja dan penggunaan data |
| --- | --- |
| Namel | Korpus, preprocessing, fungsi normalisasi bersama, dan kerangka chatbot. |
| Saskia | Memproses pertanyaan: klasifikasi pertanyaan dan deteksi tipe jawaban. Gunakan normalisasi bersama untuk teks pencarian. |
| Raisya | Mencari dan memberi peringkat kandidat memakai `teks_cari`. Sertakan ID dan `teks_asli` kandidat pada keluaran. |
| Kak Bintang | Mengambil jawaban sesuai tipe dari `teks_asli` kandidat; sertakan ID kalimat bukti. |
| Kak Belva | Mengintegrasikan modul dan mengevaluasi jawaban sistem terhadap jawaban acuan. |

Format keluaran fungsi antar anggota perlu disepakati sebelum integrasi.
Pertanyaan, jawaban acuan, dan ID bukti evaluasi dikelola terpisah dari indeks
pencarian. Jawaban acuan tidak dipakai sebagai petunjuk untuk memilih jawaban bot.

## 5. Pemeriksaan data

- JSON dapat dibaca dan berisi 21 dokumen dengan 1.133 blok asal.
- Ada 3.140 ID kalimat unik.
- Posisi karakter cocok dengan blok sumber. Teks blok tidak hilang saat dipecah,
  setelah mengabaikan spasi pemisah.
- Pemotongan keliru pada `dr.`, `Lt.`, dan `har.` sudah diperbaiki.
- Normalisasi alias mengubah `teks_cari` pada 140 record.
- Normalisasi tanggal mengubah dua record: `october` → `oktober` dan
  `maart` → `maret`. Tanggal lain yang sudah sesuai format tetap sama.
- ID, teks asli, dan field record selain `teks_cari` tetap antar tiga tahap JSON kalimat.

Dua perubahan tanggal bukan jumlah tanggal dalam korpus; itu hanya jumlah record
yang penulisannya berubah pada tahap tersebut. Data uji 22 contoh tanggal
memeriksa perilaku fungsi, terpisah dari pertanyaan evaluasi chatbot.

## 6. Sumber dan catatan penggunaan

Sumber artikel: para kontributor Wikipedia bahasa Indonesia. URL sumber tersedia
pada record; pranala revisi permanen dan URL lisensi CC BY-SA 4.0 tersedia pada
metadata korpus artikel. Informasi lisensi:
https://creativecommons.org/licenses/by-sa/4.0/.
Isi telah diseleksi dan diproses untuk proyek ini.

Pemeriksaan struktur dan keutuhan teks tidak sama dengan verifikasi sejarah.
Masih ada peringatan fakta sumber yang perlu ditinjau sebelum dipakai sebagai
soal/jawaban acuan. Status serta catatan validasi rinci dikelola terpisah dan tidak
tersedia dalam paket ini. Kode yang memanggil `status_evaluasi`,
`catatan_validasi`, `bukti_soal`, atau `tanggal_akses` tidak boleh mengasumsikan
field tersebut tersedia pada record final.

Penyiapan korpus dan kode preprocessing dibantu AI. Kontribusi anggota dan
bantuan yang dipakai perlu dicatat sesuai proses sebenarnya.

Untuk memeriksa jumlah kata pada korpus artikel, jalankan dari folder `NLP`:

```bash
python3 cek_korpus.py
```

Hasil yang diharapkan: 21 dokumen dan total 59.332 kata. Skrip ini menghitung
korpus artikel; ia tidak memeriksa seluruh fungsi chatbot.
