# Question Answering System — Sejarah Indonesia

Proyek akhir mata kuliah **Pemrosesan Bahasa Alami (PBA)**: sistem tanya jawab
faktual tentang sejarah Indonesia tanpa Large Language Model (LLM).

Sistem mencari informasi dalam korpus, kemudian mengekstraksi jawaban menggunakan
aturan bahasa. Jawaban yang ditemukan disertai ID kalimat sumber.

## 1. Gambaran sistem

Alur pemrosesan:

1. **Question Processing:** menormalisasi pertanyaan, mengklasifikasikan kata
   tanya, dan menentukan tipe jawaban.
2. **Passage Retrieval:** memberi peringkat kalimat kandidat menggunakan BM25.
3. **Answer Processing:** memeriksa pola, identitas entitas, dan hubungan
   peristiwa yang didukung, lalu mengambil jawaban dari teks asli.
4. **Integrasi dan evaluasi:** menjalankan percakapan serta membandingkan
   keluaran sistem dengan jawaban acuan.

Tipe jawaban yang ditangani modul ekstraksi adalah orang (`PER`), lokasi
(`LOC`), waktu (`DATE`), jumlah (`NUM`), dan objek faktual tertentu (`MISC`).
Dukungan setiap tipe dibatasi oleh pola yang telah diimplementasikan.
Sistem dapat mengembalikan `None` jika tidak menemukan kandidat yang memenuhi aturan.

## 2. Ringkasan korpus

| Komponen | Jumlah |
| --- | ---: |
| Artikel sumber | 21 |
| Blok sumber aktif | 1.133 |
| Kata pada field `teks` korpus artikel | 59.332 |
| Kalimat/potongan | 3.140 |
| Aturan alias | 17 |

Sumber data adalah artikel Wikipedia bahasa Indonesia tentang persiapan
kemerdekaan, tokoh, revolusi, dan diplomasi. Sebagian record berasal dari butir
daftar sehingga tidak semuanya berupa kalimat lengkap.

**Gunakan `data/processed/korpus_kalimat_final.json` sebagai masukan retrieval.**
JSON tahap sebelumnya disimpan untuk penelusuran proses; jangan menggabungkannya
ke indeks yang sama karena isinya akan terduplikasi.

## 3. Struktur repository

| Lokasi | Isi |
| --- | --- |
| `preprocessing/` | Notebook pemecah kalimat, normalisasi alias, normalisasi tanggal, dan skrip pemeriksaan korpus. |
| `question_processing/` | Modul normalisasi, klasifikasi pertanyaan, dan deteksi tipe jawaban. |
| `passage_retrieval/` | Modul tokenisasi, indeks BM25, pemeringkatan kandidat, dan utilitas perluasan konteks. |
| `answer_processing/` | Modul ekstraksi jawaban, validasi tokoh, dan dokumentasi modul jawaban. |
| `integration_evaluation/` | Notebook percakapan chatbot dan evaluasi sistem. |
| `data/raw/` | Korpus artikel yang sudah diseleksi dan dibersihkan. |
| `data/processed/` | Korpus hasil pemecahan kalimat, normalisasi alias, dan normalisasi tanggal. |
| `data/dictionary/` | Kamus `alias.json`. |
| `results/baseline/` | Hasil evaluasi yang tersimpan untuk baseline. |
| `results/arsip_pengujian/` | Arsip pengujian terdahulu. |
| `tests/` | Skrip pengujian 21 pertanyaan kelompok. |
| `requirements.txt` | Dependensi lingkungan notebook dan visualisasi. |

Nama folder `data/raw/` mengikuti struktur repository. Isinya merupakan korpus
artikel hasil penyiapan, bukan salinan mentah seluruh halaman Wikipedia.

Notebook integrasi membuat folder `results/normalized/` ketika menyimpan
eksperimen dengan `USE_NORMALIZED_QUERY = True`. Folder tersebut dapat belum
terlihat sebelum hasilnya disimpan.

## 4. Persiapan dan cara menjalankan

Gunakan Python 3. Unduh atau clone branch yang memuat struktur folder di atas,
kemudian buka **folder utama repository** di terminal atau VS Code.

Pasang dependensi:

```bash
python -m pip install -r requirements.txt
```

Pada macOS/Linux, gunakan `python3` jika perintah Python 3 di perangkatmu adalah
`python3`.

### Pemeriksaan korpus artikel

Dari folder utama repository:

```bash
python -m preprocessing.cek_korpus
```

Hasil yang diharapkan: **21 dokumen dan 59.332 kata**. Skrip ini menghitung
dokumen dan kata, bukan menguji jawaban chatbot.

### Evaluasi melalui terminal

```bash
python -m tests.test_evaluasi_resmi
```

Skrip menjalankan Question Processing, BM25 dengan `k=20`, dan Answer Processing.
Setiap soal menampilkan pertanyaan, tipe jawaban, jawaban sistem, jawaban acuan,
ID sumber, dan status kecocokan. Status diperiksa dari keluaran setiap soal;
skrip ini tidak memakai assertion untuk menggagalkan proses saat jawaban berbeda.

### Percakapan chatbot

1. Buka [Chatbot_Kerangka.ipynb](integration_evaluation/Chatbot_Kerangka.ipynb)
   menggunakan lingkungan notebook, misalnya VS Code dengan kernel Python.
2. Jalankan sel dari atas ke bawah.
3. Jalankan sel percakapan dan masukkan pertanyaan.
4. Ketik `keluar`, `exit`, atau `quit` untuk berhenti.

Walaupun nama filenya masih “Kerangka”, notebook tersebut sudah memanggil
modul pertanyaan, retrieval, dan jawaban.

Contoh pertanyaan:

- Kapan Mohammad Hatta lahir?
- Ke kota manakah Soekarno diasingkan bersama keluarganya pada tahun 1934?
- Siapa kepala delegasi Republik Indonesia dalam perundingan Roem-Roijen?

### Notebook evaluasi

Buka [Integrasi_Chatbot_Sejarah.ipynb](integration_evaluation/Integrasi_Chatbot_Sejarah.ipynb)
dan jalankan sel secara berurutan. Konfigurasi yang tersedia:

- `K = 20`: jumlah kandidat pada pengujian utama.
- `K_VALUES = [1, 3, 5, 10, 20]`: variasi jumlah kandidat.
- `USE_NORMALIZED_QUERY = True`: memakai hasil normalisasi pertanyaan untuk BM25.

Notebook menghitung Exact Match, MRR berdasarkan blok acuan, Hit@k berdasarkan
blok acuan, dan kecocokan blok sumber jawaban. Hasil dapat disimpan dalam CSV
dan JSON pada folder eksperimen yang dipilih.

### Penggunaan Google Colab

Notebook chatbot dan evaluasi memerlukan seluruh modul serta korpus dalam
struktur folder repository. Membuka file `.ipynb` saja belum menyiapkan
dependensinya.

Siapkan salinan repository yang dapat diakses di runtime Colab, pindahkan
direktori kerja ke folder utama repository, lalu jalankan sel secara berurutan.
File dan runtime setiap pengguna Colab terpisah.

## 5. Tahapan preprocessing

Penyiapan awal mencakup seleksi isi artikel, pembersihan bagian yang tidak
digunakan, perapian teks, dan pengubahan tabel terpilih menjadi kalimat.
Korpus artikel tersebut disimpan di
`data/raw/korpus_sejarah_indonesia_aktif.json`.

Notebook berikut memakai unggah/unduh file dari Google Colab:

| Urutan | Notebook | Masukan | Keluaran |
| --- | --- | --- | --- |
| 1 | [Pemecah_Kalimat_Korpus.ipynb](preprocessing/Pemecah_Kalimat_Korpus.ipynb) | `korpus_sejarah_indonesia_aktif.json` | `korpus_kalimat.json` |
| 2 | [Normalisasi_Alias.ipynb](preprocessing/Normalisasi_Alias.ipynb) | `korpus_kalimat.json` dan `alias.json` | `korpus_kalimat_alias.json` |
| 3 | [Normalisasi_Tanggal_dan_Penanda_Soal.ipynb](preprocessing/Normalisasi_Tanggal_dan_Penanda_Soal.ipynb) | `korpus_kalimat_alias.json` | `korpus_kalimat_final.json` |

Unduh keluaran setiap tahap untuk diunggah pada tahap berikutnya. Jika hasil
akan dipakai repository, tempatkan JSON kalimat pada `data/processed/` dan
kamus alias pada `data/dictionary/`.

Pada notebook tanggal versi saat ini, tambahkan penentuan nama file setelah
`unggahan = files.upload()`, sebelum membaca JSON:

```python
nama_input = next(iter(unggahan))
```

Tanpa baris tersebut, runtime baru dapat mengalami `NameError` karena
`nama_input` belum didefinisikan. Nama notebook memuat “Penanda_Soal”, tetapi
alur kode yang tersedia melakukan normalisasi tanggal; jangan mengasumsikan
field `bukti_soal` ditambahkan oleh notebook tersebut.

### Pemecahan kalimat

Pemecah menggunakan RegEx untuk menandai bagian yang dilindungi, kemudian
memindai tanda akhir kalimat. Aturannya menangani singkatan, inisial, titik
di antara angka, URL, penomoran daftar tertentu, dan beberapa bentuk kutipan.

Setiap potongan menyimpan ID serta posisi karakter pada blok sumber.
Pemeriksaan memastikan ID unik, posisi cocok, dan isi blok tidak hilang
setelah mengabaikan whitespace.

### Alias dan tanggal pada korpus

Normalisasi mengubah `teks_cari`, sementara `teks_asli` dan ID dipertahankan.

- Huruf dijadikan kecil dan whitespace berlebih dirapikan.
- Variasi nama dipetakan memakai kamus 17 aturan alias.
- Alias panjang didahulukan dan dicocokkan pada batas token.
- Tanggal dibakukan menjadi `d bulan yyyy`, misalnya
  `16/08/1945` dan `1945-08-16` menjadi `16 agustus 1945`.
- Tanggal tanpa tahun tidak diberi tahun tambahan.
- Rentang yang dikenali, jam, dan angka ribuan dipertahankan.
- Tanggal yang tidak sah secara kalender dipertahankan.
- Bulan-tahun tanpa hari, seperti `des 1941`, belum diperluas.

Stemming dan stopword removal belum diterapkan pada korpus final.

## 6. Format data dan penggunaan antar modul

Struktur teratas korpus final adalah objek dengan `metadata` dan `kalimat`.
Contoh berikut dijalankan dari folder utama repository:

```python
import json
from pathlib import Path

lokasi = Path("data/processed/korpus_kalimat_final.json")
with lokasi.open(encoding="utf-8") as file:
    data = json.load(file)

kalimat = data["kalimat"]
alias = data["metadata"]["aturan_alias"]

print("Jumlah kalimat:", len(kalimat))
print(kalimat[0]["id_kalimat"])
print(kalimat[0]["teks_asli"])
print(kalimat[0]["teks_cari"])
```

| Field | Penggunaan |
| --- | --- |
| `id_kalimat` | ID unik seperti `D01-B0001-K001`: dokumen, blok, dan potongan. |
| `id_dokumen`, `judul_dokumen` | Identitas artikel asal. |
| `id_bagian`, `judul_bagian` | Identitas bagian artikel. |
| `id_blok`, `jenis_blok` | Blok asal dan jenisnya, misalnya paragraf atau butir daftar. |
| `teks_cari` | Teks yang dipakai untuk indeks dan pencarian. |
| `teks_asli` | Teks hasil penyiapan korpus yang dipakai untuk ekstraksi dan bukti jawaban. |
| `awal_karakter_blok`, `akhir_karakter_blok` | Posisi pada blok asli: indeks mulai nol, akhir tidak termasuk. |
| `url_sumber` | Pranala artikel sumber. |
| `layak_retrieval`, `indikasi_ejaan_historis` | Penanda pemrosesan; bukan jaminan kebenaran fakta. |

Contoh pemanggilan modul dari folder utama repository:

```python
import json
from pathlib import Path

from question_processing.question_processing import process_question
from passage_retrieval.passage_retrieval import cari
from answer_processing.answer_processing import ambil_jawaban

with Path("data/processed/korpus_kalimat_final.json").open(
    encoding="utf-8"
) as file:
    korpus = json.load(file)["kalimat"]

info = process_question("Kapan Mohammad Hatta lahir?")
kandidat = cari(info["normalized_question"], k=20)
hasil = ambil_jawaban(info, kandidat, kalimat_korpus=korpus)

print(hasil)
```

Keluaran jawaban berupa dictionary `jawaban` dan `id_kalimat`, atau `None`
jika tidak ditemukan. Rincian modul tersedia pada
[README Answer Processing](answer_processing/README_ANSWER_PROCESSING.md).

Utilitas `passage_retrieval/context_expansion.py` tersedia terpisah.
Keberadaan utilitas tersebut tidak berarti ia dipanggil dalam setiap alur.
Modul jawaban juga memiliki pemeriksaan konteksnya sendiri.

## 7. Evaluasi dan batas interpretasi

Dataset kelompok memuat **21 pertanyaan**. Pengujian ulang skrip evaluasi
pada branch ini dengan query ternormalisasi dan BM25 `k=20` menghasilkan
**21/21 jawaban cocok persis (100%)**.

Soal tersebut juga digunakan selama pengembangan aturan. Hasil ini menjelaskan
kinerja pada daftar yang diuji dan belum membuktikan kemampuan menjawab semua
variasi pertanyaan atau pertanyaan baru.

| Metrik pada notebook | Definisi |
| --- | --- |
| Exact Match | Proporsi jawaban akhir yang cocok dengan acuan setelah normalisasi perbandingan evaluator. |
| MRR@k berbasis blok | Rata-rata kebalikan peringkat kalimat pertama dari blok acuan; bernilai nol jika tidak ditemukan dalam Top-k. |
| Hit@k berbasis blok | Proporsi soal yang salah satu kandidatnya berasal dari blok acuan. |
| Evidence Accuracy berbasis blok | Proporsi soal yang ID sumber jawaban akhirnya berasal dari blok acuan. |

Kecocokan blok belum memastikan bahwa setiap kalimat dalam blok tersebut
merupakan bukti jawaban yang tepat; bukti tetap perlu ditinjau.

Pertanyaan, jawaban acuan, dan blok acuan digunakan oleh evaluator, bukan
sebagai petunjuk pada fungsi pencarian dan ekstraksi jawaban.

## 8. Pembagian tanggung jawab

| Anggota | Tanggung jawab |
| --- | --- |
| Namel | Penyiapan korpus, preprocessing, normalisasi alias dan tanggal, serta kerangka chatbot. |
| Saskia | Normalisasi dan klasifikasi pertanyaan serta deteksi tipe jawaban. |
| Raisya | Tokenisasi, indeks BM25, dan pemeringkatan kandidat kalimat. |
| Kak Bintang | Ekstraksi jawaban serta validasi tokoh, entitas, dan hubungan peristiwa yang didukung. |
| Kak Belva | Integrasi modul, eksperimen, evaluasi, dan dokumentasi hasil sistem. |

## 9. Keterbatasan saat ini

- Cakupan jawaban bergantung pada korpus dan pola ekstraksi yang tersedia.
  Parafrase atau hubungan yang belum dikenali masih dapat gagal.
- Pemecah kalimat bersifat heuristik. Singkatan di luar daftar, inisial di akhir
  kalimat, dan kutipan kompleks masih memerlukan peninjauan.
- Notebook integrasi sudah meneruskan `normalized_question` ke BM25. Namun,
  normalisasi tanggal pada modul pertanyaan belum mencakup seluruh aturan
  notebook preprocessing, termasuk format ISO dan validasi kalender.
- POS tagging, dependency parsing, dan embedding belum digunakan oleh alur utama.
- Pemeriksaan struktur, posisi karakter, dan keutuhan teks bukan verifikasi
  kebenaran sejarah.
- Record final tidak menyediakan `status_evaluasi`, `catatan_validasi`,
  `bukti_soal`, atau `tanggal_akses`; kode lain tidak boleh mengasumsikannya ada.

## 10. Sumber data dan lisensi

Sumber teks adalah para kontributor **Wikipedia bahasa Indonesia**. URL sumber
tersedia pada record kalimat; pranala revisi permanen dan URL lisensi tersedia
pada metadata korpus artikel.

Teks telah diseleksi dan diproses untuk kebutuhan proyek. Rujukan lisensi
teks sumber: [Creative Commons Attribution-ShareAlike 4.0](https://creativecommons.org/licenses/by-sa/4.0/).
Informasi tersebut merujuk pada teks sumber, bukan penetapan lisensi seluruh
kode repository.
