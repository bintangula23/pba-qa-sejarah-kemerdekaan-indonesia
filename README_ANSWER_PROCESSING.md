# Answer Processing — QA Sejarah Indonesia

## 1. Tujuan Modul

Modul Answer Processing merupakan salah satu komponen dalam sistem *Question Answering* (QA) berbasis aturan (*rule-based*) untuk menjawab pertanyaan mengenai sejarah Indonesia.

Modul ini bertugas mengolah kalimat kandidat yang diperoleh dari Passage Retrieval menggunakan BM25, kemudian mengekstraksi jawaban sesuai tipe jawaban yang dihasilkan oleh Question Processing.

Modul Answer Processing dikembangkan tanpa menggunakan Large Language Model (LLM). Proses ekstraksi jawaban menggunakan Regular Expression (RegEx), pencocokan pola kalimat, serta validasi hubungan antara pertanyaan, tokoh, peristiwa, dan konteks kalimat.

Secara umum, alur sistem adalah:

```text
Pertanyaan Pengguna
        ↓
Question Processing
        ↓
Passage Retrieval (BM25)
        ↓
Answer Processing
        ↓
Jawaban dan ID Kalimat Sumber
```

## 2. File Utama

Modul Answer Processing terdiri dari tiga file utama:

### 2.1 `answer_processing.py`

Berisi fungsi utama untuk mengekstraksi jawaban dari kandidat kalimat berdasarkan tipe jawaban.

Tipe jawaban yang sudah diimplementasikan adalah:

- `DATE`: tanggal peristiwa.
- `PER`: nama orang atau tokoh.
- `LOC`: lokasi, khususnya lokasi kelahiran.
- `NUM`: jumlah atau angka berdasarkan satuan tertentu.

### 2.2 `validasi_tokoh.py`

Berisi fungsi pendukung untuk memeriksa kecocokan identitas tokoh antara pertanyaan dan kalimat sumber.

Modul ini juga menyediakan pemeriksaan konteks antarkalimat untuk membantu menangani pertanyaan kelahiran ketika kalimat sumber menggunakan kata ganti seperti *Ia*.

### 2.3 `context_expansion.py`

Berisi fungsi `perluas_konteks()` untuk memperluas kandidat hasil retrieval menggunakan kalimat-kalimat dari blok dokumen yang sama.

Fungsi ini merupakan komponen pendukung dan belum dipanggil secara otomatis oleh fungsi utama `ambil_jawaban()`.

## 3. Fungsi Utama

Fungsi utama modul Answer Processing adalah:

`ambil_jawaban(info_pertanyaan, kandidat, kalimat_korpus=None)`

Fungsi ini berada pada file `answer_processing.py`.

Fungsi tersebut menerima hasil Question Processing, kandidat kalimat dari BM25, dan data korpus opsional untuk validasi konteks.

Fungsi akan memeriksa kandidat berdasarkan urutan yang diterima, kemudian menjalankan aturan ekstraksi sesuai tipe jawaban.

Jika ditemukan jawaban yang memenuhi aturan, fungsi mengembalikan jawaban dan ID kalimat sumber. Jika tidak ditemukan jawaban yang sesuai, fungsi mengembalikan `None`.

## 4. Format Input

### 4.1 `info_pertanyaan`

Parameter `info_pertanyaan` berupa dictionary dari modul Question Processing.

Contoh:

```python
{
    "original_question": "Kapan Mohammad Hatta lahir?",
    "answer_type": "DATE"
}
```

Keterangan:

- `original_question`: pertanyaan asli dari pengguna.
- `answer_type`: tipe jawaban yang diharapkan, misalnya `DATE`, `PER`, `LOC`, atau `NUM`.

### 4.2 `kandidat`

Parameter `kandidat` berupa list dictionary hasil Passage Retrieval menggunakan BM25.

Contoh:

```python
[
    {
        "id_kalimat": "D08-B0004-K003",
        "skor": 35.0,
        "teks_asli": (
            "Ia lahir dengan nama Muhammad Athar "
            "pada tanggal 12 Agustus 1902."
        )
    }
]
```

Keterangan:

- `id_kalimat`: identitas kalimat dalam korpus.
- `skor`: skor relevansi BM25. Nilai pada contoh hanya ilustrasi.
- `teks_asli`: teks kalimat yang akan diproses untuk ekstraksi jawaban.

Answer Processing menggunakan urutan kandidat dari BM25. Modul belum melakukan pemeringkatan ulang kandidat secara terpisah.

### 4.3 `kalimat_korpus`

Parameter `kalimat_korpus` bersifat opsional dan berisi daftar kalimat dari korpus.

Contoh struktur satu item:

```python
{
    "id_kalimat": "D08-B0004-K001",
    "id_blok": "D08-B0004",
    "teks_asli": (
        "Mohammad Hatta lahir dari pasangan "
        "Muhammad Djamil dan Siti Saleha."
    )
}
```

Parameter ini diperlukan untuk pemeriksaan konteks tertentu, khususnya ketika kalimat jawaban menggunakan kata ganti seperti *Ia*.

Contohnya, pertanyaan kelahiran Mohammad Hatta memerlukan kalimat pendukung dari blok dokumen yang sama untuk membantu mengidentifikasi subjek.

Jika parameter tidak diberikan, kandidat yang membutuhkan validasi konteks dapat ditolak.

## 5. Format Output

Jika jawaban ditemukan, fungsi mengembalikan dictionary dengan dua informasi:

```python
{
    "jawaban": "12 Agustus 1902",
    "id_kalimat": "D08-B0004-K003"
}
```

Keterangan:

- `jawaban`: hasil ekstraksi sesuai tipe jawaban.
- `id_kalimat`: ID kalimat yang digunakan sebagai sumber jawaban.

Jika tidak ada kandidat yang memenuhi aturan ekstraksi dan validasi, fungsi mengembalikan:

```python
None
```

Nilai `None` dapat terjadi

## 6. Aturan Ekstraksi Jawaban

Modul Answer Processing menggunakan pendekatan *rule-based* untuk mengekstraksi jawaban dari kandidat kalimat hasil BM25.

Pemilihan aturan didasarkan pada nilai `answer_type` dari Question Processing. Setiap tipe jawaban memiliki pola ekstraksi dan pemeriksaan yang berbeda.

### 6.1 DATE — Ekstraksi Tanggal

Ekstraksi tanggal dilakukan menggunakan Regular Expression (RegEx) untuk mengenali tanggal lengkap dalam format hari, nama bulan, dan tahun.

Contoh:

`12 Agustus 1902`

Fungsi utama yang digunakan adalah `ekstrak_tanggal()` dan `pilih_tanggal()`.

Proses ekstraksi meliputi:

1. Mencari tanggal lengkap dalam kalimat kandidat.
2. Mengidentifikasi peristiwa yang ditanyakan, seperti kelahiran, kematian, atau pelantikan.
3. Memilih tanggal berdasarkan kesesuaian peristiwa dan klausa.
4. Untuk pertanyaan kelahiran tokoh yang dikenali, memvalidasi identitas subjek menggunakan `validasi_tokoh()`.
5. Jika kalimat menggunakan kata ganti seperti *Ia*, memeriksa kalimat pendukung dalam blok dokumen yang sama menggunakan `periksa_konteks_tokoh()`.

Contoh:

**Pertanyaan:** Kapan Mohammad Hatta lahir?

**Kalimat sumber:** Ia lahir dengan nama Muhammad Athar pada tanggal 12 Agustus 1902.

**Jawaban:** 12 Agustus 1902.

**ID sumber:** `D08-B0004-K003`

Validasi konteks menggunakan kalimat `D08-B0004-K001` yang menyebut Mohammad Hatta sebagai subjek kelahiran.

### 6.2 PER — Ekstraksi Nama Tokoh

Ekstraksi `PER` digunakan untuk menemukan nama orang yang berkaitan dengan peristiwa dalam pertanyaan.

Fungsi yang digunakan adalah `identifikasi_peristiwa_per()` dan `ekstrak_pelaku()`.

Implementasi saat ini mengenali dua kategori peristiwa utama:

- `PEMBERIAN_JULUKAN`: mencari tokoh yang memberikan julukan.
- `KOMANDAN_TEWAS`: mencari nama komandan yang berkaitan secara eksplisit dengan peristiwa kematian.

Proses ekstraksi meliputi:

1. Mengidentifikasi kategori peristiwa dari pertanyaan.
2. Memeriksa kesesuaian pola peristiwa pada kalimat kandidat.
3. Mengekstraksi nama tokoh berdasarkan pola aktif atau pasif yang didukung.
4. Menolak kandidat jika hubungan antara peristiwa dan nama tidak memenuhi aturan.

Pola nama juga mendukung bentuk tertentu yang menggunakan gelar dan inisial, seperti `Brigadir A. W. S. Mallaby`.

**Contoh 1**

Pertanyaan: Siapa yang memberikan julukan Piagam Jakarta?

Jawaban: Mohammad Yamin.

ID sumber: `D04-B0017-K001`

**Contoh 2**

Pertanyaan: Siapa komandan pasukan Britania yang tewas dalam baku tembak pada 30 Oktober 1945 di Surabaya?

Jawaban: Brigadir A. W. S. Mallaby.

ID sumber: `D13-B0002-K002`

### 6.3 LOC — Ekstraksi Lokasi

Ekstraksi `LOC` saat ini difokuskan pada pertanyaan mengenai lokasi kelahiran tokoh.

Fungsi yang digunakan adalah `ambil_tokoh_pertanyaan()`, `cek_subjek_kelahiran()`, dan `ekstrak_lokasi()`.

Proses ekstraksi meliputi:

1. Mengambil nama tokoh dari pertanyaan lokasi kelahiran.
2. Memeriksa apakah subjek kelahiran dalam kandidat sesuai dengan tokoh yang ditanyakan.
3. Mencari lokasi yang mengikuti pola kelahiran, seperti `lahir ... di [lokasi]`.
4. Membatasi pencarian agar tidak mengambil lokasi dari peristiwa lain yang dipisahkan oleh penanda tertentu.
5. Mengembalikan `None` jika lokasi atau identitas tokoh tidak memenuhi aturan.

Contoh:

**Pertanyaan:** Di mana Fatmawati dilahirkan?

**Kalimat sumber:** Fatmawati lahir pada 5 Februari 1923 di Bengkulu dari pasangan Hasan Din dan Siti Chadijah.

**Jawaban:** Bengkulu.

**ID sumber:** `D11-B0002-K001`

### 6.4 NUM — Ekstraksi Angka

Ekstraksi `NUM` digunakan untuk mengambil angka berdasarkan satuan yang disebutkan dalam pertanyaan.

Fungsi yang digunakan adalah `ekstrak_angka()`.

Satuan yang dikenali dalam implementasi saat ini meliputi:

- anggota
- orang
- korban
- pasukan
- hari
- bulan
- tahun

Proses ekstraksi meliputi:

1. Mengidentifikasi kata satuan pada pertanyaan.
2. Mencari bilangan berbentuk digit yang diikuti satuan sesuai.
3. Mengembalikan bilangan yang ditemukan.
4. Mengembalikan `None` jika tidak ditemukan pasangan angka dan satuan yang sesuai.

Contoh:

**Pertanyaan:** Berapa jumlah anggota panitia?

**Kalimat:** Panitia tersebut terdiri dari 9 anggota.

**Jawaban:** 9.

Contoh `NUM` ini menggunakan kalimat pengujian buatan, bukan kutipan dari korpus sejarah.

Implementasi saat ini belum mendukung bilangan yang ditulis menggunakan kata, misalnya `sembilan anggota`.

## 7. Contoh Penggunaan Modul

Berikut contoh penggunaan Answer Processing bersama Question Processing dan Passage Retrieval (BM25).

```python
import json

from question_processing import process_question
from passage_retrieval import cari
from answer_processing import ambil_jawaban

# Pertanyaan pengguna
pertanyaan = "Kapan Mohammad Hatta lahir?"

# Tahap 1: Question Processing
info_pertanyaan = process_question(pertanyaan)

# Tahap 2: Passage Retrieval
kandidat = cari(pertanyaan, k=20)

# Membaca korpus untuk validasi konteks
with open("korpus_kalimat_final.json", encoding="utf-8") as file:
    data = json.load(file)

kalimat_korpus = data["kalimat"]

# Tahap 3: Answer Processing
hasil = ambil_jawaban(
    info_pertanyaan,
    kandidat,
    kalimat_korpus=kalimat_korpus
)

print(hasil)
```

Hasil yang diperoleh pada pengujian:

```python
{
    "jawaban": "12 Agustus 1902",
    "id_kalimat": "D08-B0004-K003"
}
```

**Catatan integrasi:** Parameter `kalimat_korpus` sebaiknya diberikan ketika tersedia karena digunakan untuk memvalidasi konteks pada pertanyaan tertentu. Nilai `k=20` adalah konfigurasi yang digunakan pada pengujian ini, bukan nilai optimal yang sudah dibuktikan untuk seluruh pertanyaan.

## 8. Hasil Pengujian

Pengujian dilakukan menggunakan kalimat buatan untuk menguji aturan tertentu dan kalimat asli dari korpus sejarah Indonesia.

### 8.1 Pengujian Ekstraksi Dasar

| Tipe | Contoh jawaban | Hasil |
|---|---|---|
| DATE | 12 Agustus 1902 | PASS |
| PER | Mohammad Yamin | PASS |
| LOC | Bengkulu | PASS |
| NUM | 9 | PASS |

Hasil `tests/test_semua_tipe.py`: **4/4 PASS**.

### 8.2 Pengujian Integrasi dengan BM25

| Pertanyaan | Jawaban | ID Sumber | Hasil |
|---|---|---|---|
| Kapan Mohammad Hatta lahir? | 12 Agustus 1902 | D08-B0004-K003 | PASS |
| Siapa pemberi julukan Piagam Jakarta? | Mohammad Yamin | D04-B0017-K001 | PASS |
| Di mana Fatmawati dilahirkan? | Bengkulu | D11-B0002-K001 | PASS |
| Siapa komandan pasukan Britania yang tewas di Surabaya? | Brigadir A. W. S. Mallaby | D13-B0002-K002 | PASS |

Keempat pertanyaan tersebut merupakan contoh yang digunakan selama proses pengembangan dan pengujian. Hasilnya tidak dapat dianggap sebagai akurasi keseluruhan sistem.

### 8.3 Pengujian Negatif dan Validasi

Pengujian negatif digunakan untuk memeriksa kemampuan modul menolak jawaban yang tidak sesuai dengan pertanyaan.

Hasil yang diperoleh:

- Tiga pengujian negatif `PER` berhasil, termasuk penolakan kandidat dengan hubungan jabatan yang ambigu.
- Validasi `DATE` berhasil menolak tanggal milik tokoh lain dan menggunakan konteks pada contoh Mohammad Hatta.
- Pengujian lokasi negatif: 4/4 PASS.
- Pengujian validasi subjek lokasi: 3/3 PASS.
- Pengujian ekstraksi angka: 5/5 PASS.
- Pengujian konteks ambigu yang dibuat: nama tokoh tidak langsung diterima sebagai rujukan kata ganti.

Pengujian tersebut memverifikasi perilaku pada contoh yang diuji, bukan membuktikan bahwa seluruh

## 9. Keterbatasan Sistem

Beberapa keterbatasan implementasi Answer Processing saat ini adalah:

Cakupan tipe jawaban. Ekstraksi baru diterapkan pada DATE, PER, LOC, dan NUM. Tipe MISC, REASON, dan DESCRIPTION belum didukung.

Format tanggal. Ekstraksi DATE terutama mengenali tanggal lengkap dengan format hari, nama bulan, dan tahun. Tahun tunggal dan variasi penulisan tanggal lainnya belum ditangani secara menyeluruh.

Cakupan nama tokoh. Ekstraksi PER menggunakan pola peristiwa tertentu, terutama pemberian julukan dan komandan yang tewas. Pola ini belum dapat digunakan untuk seluruh jenis pertanyaan tentang tokoh sejarah.

Cakupan lokasi. Ekstraksi LOC masih berfokus pada lokasi kelahiran tokoh dan belum mendukung seluruh jenis pertanyaan lokasi.

Format bilangan. Ekstraksi NUM mengenali digit yang diikuti satuan tertentu. Bilangan berbentuk kata seperti sembilan belum didukung.

Ambiguitas kata ganti. Validasi konteks antarkalimat masih menggunakan heuristik. Sistem belum memiliki mekanisme coreference resolution umum dan dapat mengembalikan None ketika identitas subjek belum dapat dipastikan.

Pemilihan kandidat. Answer Processing memeriksa kandidat berdasarkan urutan dari BM25 dan mengambil jawaban pertama yang memenuhi aturan. Modul belum menerapkan pemeringkatan ulang jawaban secara menyeluruh.

Ketergantungan pada pola kalimat. Jawaban yang sebenarnya terdapat dalam korpus dapat tidak ditemukan jika struktur kalimat belum sesuai dengan aturan ekstraksi.

Keterbatasan tersebut menjadi pertimbangan untuk pengembangan sistem dan evaluasi lebih lanjut.