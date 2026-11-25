# Answer Processing — QA Sejarah Indonesia

## 1. Tujuan dan Posisi Modul

Answer Processing merupakan komponen sistem *Question Answering* (QA) sejarah Indonesia berbasis aturan (*rule-based*) tanpa Large Language Model (LLM). Modul ini memproses kandidat kalimat dari Passage Retrieval (BM25) dan mengekstraksi jawaban sesuai `answer_type` yang diberikan Question Processing.

```text
Pertanyaan → Question Processing → Passage Retrieval (BM25)
           → Answer Processing → Jawaban + ID kalimat sumber
```

Ekstraksi menggunakan Regular Expression (RegEx), pencocokan frasa peristiwa, serta validasi subjek dan konteks untuk pola tertentu. Sistem tidak membangkitkan jawaban bebas: jawaban diambil dari teks kandidat yang memenuhi aturan.

## 2. File dan Fungsi yang Digunakan

| File | Fungsi |
|---|---|
| `answer_processing.py` | Implementasi utama ekstraksi `DATE`, `PER`, `LOC`, `NUM`, dan `MISC`. |
| `validasi_tokoh.py` | Validasi tokoh pada kalimat kelahiran, termasuk konteks kalimat sebelumnya dalam blok yang sama dan variasi `Di mana`/`Dimana`. |
| `context_expansion.py` | Utilitas `perluas_konteks()` untuk mengambil kalimat satu blok. **Tidak dipanggil otomatis** oleh `ambil_jawaban()` pada alur evaluasi resmi. |

### Antarmuka utama

```python
ambil_jawaban(info_pertanyaan, kandidat, kalimat_korpus=None)
```

Parameter:

- `info_pertanyaan` (dictionary): setidaknya berisi `original_question` dan `answer_type`.
- `kandidat` (list dictionary): hasil BM25 yang memuat `id_kalimat` dan `teks_asli`; `skor` boleh tersedia, tetapi tidak dipakai untuk menghitung ulang peringkat di modul ini.
- `kalimat_korpus` (opsional): daftar kalimat korpus dengan `id_kalimat`, `id_blok`, dan `teks_asli`. Diperlukan pada kasus validasi konteks antarkalimat, misalnya kata ganti pada kalimat kelahiran Hatta.

Kandidat diperiksa sesuai urutan hasil BM25. Modul mengembalikan **jawaban pertama yang memenuhi aturan**, tanpa pemeringkatan ulang jawaban.

Jika ditemukan jawaban:

```python
{"jawaban": "12 Agustus 1902", "id_kalimat": "D08-B0004-K003"}
```

Jika tidak ada kandidat yang memenuhi aturan, hasilnya `None`.

## 3. Aturan Ekstraksi

### 3.1 DATE — Tanggal, tahun, serta bulan dan tahun

Fungsi terkait antara lain `ekstrak_tanggal()`, `ekstrak_tahun()`, `ekstrak_tahun_pendirian()`, `ekstrak_bulan_tahun()`, dan `pilih_tanggal()`.

- **Tanggal lengkap**: mengenali bentuk seperti `12 Agustus 1902`, dengan pemilihan berdasarkan peristiwa atau klausa pada pola yang didukung.
- **Tahun pendirian organisasi**: untuk bentuk pertanyaan `Pada tahun berapa ... mendirikan [organisasi]?`, kalimat harus menyebut organisasi yang sama dan peristiwa pendiriannya. Contoh D09: `1948` dari `D09-B0002-K001`.
- **Bulan dan tahun**: untuk pertanyaan yang meminta bulan, ekstraksi mengembalikan bentuk seperti `Desember 1948`, bukan tanggal lengkap. Contoh D16: `D16-B0001-K001`.
- **Validasi tokoh kelahiran**: pada pola `Kapan [tokoh] lahir?`, identitas subjek diperiksa. Jika kalimat menggunakan kata ganti seperti *Ia*, modul memeriksa kalimat pendukung dalam blok yang sama melalui `validasi_tokoh.py`.

Contoh D08: `Kapan Mohammad Hatta lahir?` → `12 Agustus 1902` (`D08-B0004-K003`).

### 3.2 PER — Tokoh berdasarkan hubungan peristiwa dan peran

Fungsi `identifikasi_peristiwa_per()` memilih kategori peristiwa yang didukung, lalu `ekstrak_pelaku()` mencari nama pada pola kalimat yang sesuai.

Cakupan pola yang digunakan dalam evaluasi resmi:

| Hubungan dalam kalimat | Contoh ID | Jawaban |
|---|---|---|
| Pemberian julukan | D04 | Mohammad Yamin |
| Komandan pasukan yang tewas | D13 | Brigadir A. W. S. Mallaby |
| Tokoh terpilih menjadi panglima | D12 | Sudirman |
| Pelaku peledakan | D14 | Muhammad Toha |
| Pemimpin pasukan dengan jabatan Letkol | D17 | Letkol Soeharto |
| Tokoh yang bertindak sebagai perantara | D18 | Lord Killearn |
| Kepala delegasi | D20 | Mohamad Roem |
| Pasangan tokoh dan jabatan yang dihubungkan oleh `masing-masing` | D03 | Mohammad Hatta |

Pola memeriksa hubungan nama dengan tindakan atau jabatan, bukan sekadar mengambil nama pertama dari sebuah kalimat. Dukungan bentuk nama dan struktur kalimat tetap terbatas pada pola yang diimplementasikan.

### 3.3 LOC — Lokasi kelahiran dan lokasi peristiwa

Fungsi `ekstrak_lokasi()` menangani lokasi kelahiran; `ekstrak_lokasi_peristiwa()` menangani beberapa jenis lokasi peristiwa. Untuk kelahiran, `ambil_tokoh_pertanyaan()` dan `cek_subjek_kelahiran()` memvalidasi tokoh agar lokasi orang lain tidak terambil.

| Hubungan lokasi | Contoh ID | Jawaban |
|---|---|---|
| Tempat kelahiran | D11 | Bengkulu |
| Lokasi pembukaan persidangan | D02 | Gedung Chuo Sangi In di Jakarta |
| Kota tujuan pengasingan | D07 | Ende |
| Lokasi operasi pendaratan tertentu | D15 | Pasir Poetih, Situbondo |
| Tempat kapal berlabuh | D19 | Teluk Jakarta |

Untuk D15, aturan membedakan lokasi *Produk Utara* dari lokasi operasi lain dalam kalimat yang sama. Untuk D11, bentuk `Di mana` dan `Dimana` sama-sama dikenali.

### 3.4 NUM — Jumlah berbentuk digit dan satuan

Fungsi `ekstrak_angka()` mencari angka digit yang diikuti satuan sesuai pertanyaan, misalnya `anggota`, `orang`, `korban`, `pasukan`, `hari`, `bulan`, `tahun`, dan `negara bagian`.

Pada kasus D21, kalimat `... terdiri dari 16 negara bagian ...` menghasilkan **`16 negara bagian`** (`D21-B0018-K003`). Untuk satuan lain, fungsi dapat mengembalikan angka saja mengikuti aturan yang tersedia.

Bilangan berbentuk kata seperti `enam belas` belum ditangani secara umum.

### 3.5 MISC — Objek faktual dengan pola terbatas

Fungsi `ekstrak_misc()` menangani dua bentuk objek faktual pada evaluasi resmi:

- **Sumber daya alam utama**, dari frasa seperti `sumber-sumber alam, terutama minyak bumi` → `Minyak bumi` (D01, `D01-B0009-K002`).
- **Nama kapal penyerahan**, dari hubungan `menyerah kepada Sekutu di kapal USS Missouri` → `USS Missouri` (D06, `D06-B0007-K001`).

Kategori `MISC` **bukan ekstraksi entitas serbaguna**; hanya pola yang telah diimplementasikan yang dapat dijawab.

## 4. Perilaku Validasi dan Penolakan

Jika kandidat tidak memiliki pola dan hubungan peristiwa yang diperlukan, sistem melewatinya. Misalnya, pertanyaan tentang tahun pendirian Partai Sosialis Indonesia tidak boleh mengambil tanggal pendirian Partai Nasional Indonesia. Untuk beberapa pertanyaan kelahiran, kandidat dengan subjek tokoh berbeda juga ditolak.

Jika seluruh kandidat tidak memenuhi aturan, `ambil_jawaban()` mengembalikan `None`. Hal ini lebih aman daripada mengembalikan tanggal, nama, atau lokasi yang tidak terverifikasi oleh pola.

## 5. Contoh Integrasi

Jalankan dari direktori utama proyek:

```python
import json
from question_processing import process_question
from passage_retrieval import cari
from answer_processing import ambil_jawaban

pertanyaan = "Kapan Mohammad Hatta lahir?"
info_pertanyaan = process_question(pertanyaan)
kandidat = cari(pertanyaan, k=20)

with open("korpus_kalimat_final.json", encoding="utf-8") as file:
    kalimat_korpus = json.load(file)["kalimat"]

hasil = ambil_jawaban(
    info_pertanyaan,
    kandidat,
    kalimat_korpus=kalimat_korpus
)
print(hasil)
```

Hasil pada pengujian resmi:

```python
{'jawaban': '12 Agustus 1902', 'id_kalimat': 'D08-B0004-K003'}
```

Nilai `k=20` adalah konfigurasi yang digunakan pada pengujian ini, bukan nilai optimal yang dibuktikan untuk semua pertanyaan.

## 6. Evaluasi

### 6.1 Evaluasi resmi D01–D21

Evaluasi dijalankan melalui `tests/test_evaluasi_resmi.py`, menggunakan 21 pertanyaan dari daftar resmi kelompok, alur Question Processing → BM25 (`k=20`) → Answer Processing, dan jawaban acuan yang telah disiapkan.

Perintah dari direktori proyek:

```powershell
$env:PYTHONPATH = (Get-Location).Path
python tests/test_evaluasi_resmi.py
```

**Hasil verifikasi terakhir selama pengembangan:** semua 21 baris status menunjukkan `COCOK PERSIS`.

| Tipe | Cocok persis | Total |
|---|---:|---:|
| DATE | 5 | 5 |
| PER | 8 | 8 |
| LOC | 5 | 5 |
| MISC | 2 | 2 |
| NUM | 1 | 1 |
| **Total** | **21** | **21** |

**Exact Match pada 21 pertanyaan resmi: 21/21 (100%).** Angka ini merupakan hasil *end-to-end* pada daftar yang juga dipakai selama pengembangan dan penyesuaian aturan; bukan evaluasi generalisasi pada pertanyaan baru maupun pengukuran kinerja Answer Processing secara terisolasi. Status cocok persis didasarkan pada perbandingan teks jawaban dengan acuan dalam evaluator. ID sumber juga ditampilkan, tetapi status tersebut tidak menghitung akurasi ID sumber secara terpisah.

### 6.2 Pengujian regresi

Pengujian yang dijalankan setelah pembaruan mencakup:

- Validasi dan konteks DATE (`tests/test_date_validasi_integrasi.py`, `tests/test_konteks_date_hatta.py`): PASS pada hasil terminal.
- Uji negatif dan integrasi PER (`tests/test_per_negatif.py`, `tests/test_integrasi_surabaya.py`): PASS pada hasil terminal.
- Uji negatif dan validasi subjek LOC (`tests/test_lokasi_negatif.py`, `tests/test_validasi_subjek_loc.py`): seluruh 7 kasus PASS pada hasil terminal.

Pengujian regresi menunjukkan perilaku pada kasus yang diuji tetap terjaga setelah perluasan aturan; ini bukan bukti mencakup semua variasi kalimat bahasa Indonesia.

## 7. Keterbatasan

- **Ketergantungan pada pola:** fungsi belum memahami makna kalimat secara umum. Perubahan susunan kata, variasi istilah, atau relasi yang tidak tercakup dapat menghasilkan `None`.
- **Generalisasi terbatas:** beberapa pola mengandalkan istilah peristiwa, jabatan, atau entitas yang spesifik. Hasil 21/21 adalah hasil pada set yang telah digunakan untuk mengembangkan aturan.
- **Tipe di luar cakupan:** `REASON` dan `DESCRIPTION` belum ditangani oleh fungsi utama. `MISC` hanya memiliki pola objek tertentu.
- **Bilangan dan waktu:** `NUM` belum secara umum mengekstraksi bilangan berbentuk kata; `DATE` juga belum mencakup semua variasi penulisan waktu atau seluruh jenis peristiwa.
- **Rujukan antarkalimat:** validasi kata ganti menggunakan heuristik dalam blok yang sama, bukan *coreference resolution* umum.
- **Ketergantungan pada retrieval:** jika sumber jawaban tidak masuk kandidat BM25, Answer Processing tidak dapat mengambil jawaban tersebut. Modul mengembalikan hasil pertama yang lolos aturan, tanpa pemeringkatan ulang kandidat secara global.

## 8. Catatan Integrasi Kelompok

Modul utama dapat dipanggil melalui `ambil_jawaban(info_pertanyaan, kandidat, kalimat_korpus=kalimat_korpus)` dan akan mengembalikan dictionary `jawaban`/`id_kalimat` atau `None`. Berkas `validasi_tokoh.py` merupakan dependensi langsung. `context_expansion.py` adalah utilitas terpisah dan tidak wajib dipanggil oleh jalur integrasi evaluasi resmi.

Perubahan pada modul ini dilakukan untuk kebutuhan 21 pertanyaan resmi; penerapan pada data dan pertanyaan baru perlu evaluasi tambahan oleh tim.
