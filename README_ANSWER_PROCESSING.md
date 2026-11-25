# Answer Processing — QA Sejarah Indonesia

## 1. Tujuan dan posisi modul

Answer Processing merupakan komponen sistem Question Answering (QA) sejarah Indonesia berbasis aturan (rule-based) tanpa LLM. Modul menerima hasil Question Processing dan kandidat kalimat dari Passage Retrieval (BM25), kemudian mengekstraksi serta memeriksa relevansi calon jawaban.

```text
Pertanyaan → Question Processing → BM25 Top-k → Answer Processing
                                                    ↓
                                         Jawaban + ID bukti / None
```

## 2. File dan antarmuka

| File | Tanggung jawab |
|---|---|
| `answer_processing.py` | Analisis kebutuhan informasi, ekstraksi factoid, validasi relevansi, dan pemilihan jawaban. |
| `validasi_tokoh.py` | Pencocokan identitas tokoh dan validasi konteks kelahiran. |
| `question_processing.py` | Klasifikasi pertanyaan, deteksi tipe jawaban, dan fungsi `normalize_question()` yang digunakan sementara untuk normalisasi. |
| `alias.json` | Kamus variasi nama dan istilah bersama. |
| `context_expansion.py` | Utilitas terpisah; tidak dipanggil otomatis oleh fungsi utama Answer Processing. |

Antarmuka integrasi tetap:

```python
ambil_jawaban(info_pertanyaan, kandidat, kalimat_korpus=None)
```

- `info_pertanyaan`: minimal memuat `original_question` dan `answer_type`; `normalized_question` dapat tersedia dari Question Processing.
- `kandidat`: daftar hasil retrieval berisi `id_kalimat` dan `teks_asli`, dengan urutan BM25 yang dipertahankan.
- `kalimat_korpus`: daftar record korpus untuk indeks ID kalimat, blok, dan judul dokumen. Sangat disarankan untuk integrasi karena beberapa aturan membutuhkan konteks.

Hasil berupa dictionary, misalnya:

```python
{"jawaban": "12 Agustus 1902", "id_kalimat": "D08-B0004-K003"}
```

Jika tidak ada kandidat yang memenuhi aturan, hasilnya `None`. Tidak ada pemeringkatan ulang berdasarkan skor jawaban.

## 3. Alur pemrosesan

1. `analisis_pertanyaan()` mengenali tipe jawaban, relasi, entitas, serta ketelitian waktu atau satuan untuk bentuk pertanyaan yang didukung. Analisis dilakukan sekali per pertanyaan.
2. `ambil_jawaban()` membentuk indeks korpus menurut ID kalimat dan blok. Kandidat diperiksa berdasarkan urutan BM25.
3. Ekstraktor sesuai tipe mencari jawaban pada `teks_asli`. Fungsi validasi relevansi memeriksa argumen yang dikenali, dengan konteks terbatas bila diperlukan. Beberapa aturan juga mengikat entitas pada posisi tertentu dalam pola relasi.
4. Kandidat yang tidak memenuhi aturan dilewati. Kandidat valid pertama dikembalikan bersama ID kalimat bukti. Jika tidak ada, kembalikan `None`.

Pencocokan alias memanfaatkan `normalize_question()`; kapitalisasi teks sumber dipertahankan untuk ekstraksi nama dan lokasi. Pencocokan frasa menggunakan batas token; beberapa singkatan juga dapat dikenali secara heuristik. Ini bukan NER atau dependency parsing umum.

## 4. Cakupan ekstraksi

| Tipe | Mekanisme | Contoh perubahan |
|---|---|---|
| DATE | Ekstraksi tanggal lengkap, tahun, atau bulan-tahun sesuai relasi dan argumen pertanyaan. | Menyamakan `lahir` dan `dilahirkan`, menolak fallback tanggal yang tidak relevan, memeriksa entitas pendirian. |
| PER | Kumpulan pola pelaku, jabatan, dan peran. | Variasi `dipilih`/`terpilih`, `kepala`/`pemimpin delegasi`, pemisahan presiden dan wakil presiden. |
| LOC | Ekstraksi lokasi berdasarkan relasi dan entitas dinamis. | Kelahiran, pengasingan, kapal berlabuh, pembukaan persidangan, operasi pendaratan; mendukung pola lokasi bertingkat tertentu. |
| NUM | Ekstraksi digit dan satuan, termasuk pemisah ribuan berupa titik. | Mengikat jumlah pada entitas melalui pola yang didukung, bukan sekadar kecocokan satuan. |
| MISC | Ekstraksi objek faktual dengan pola terbatas. | Sumber daya alam dan nama kapal terkait penyerahan. |

`REASON`, `DESCRIPTION`, dan tipe yang tidak memiliki aturan ekstraksi belum didukung. Cakupan setiap tipe masih terbatas pada struktur pertanyaan dan kalimat yang dikenali.

### Validasi konteks

Validasi kelahiran pada DATE dan LOC menggunakan implementasi bersama melalui `validasi_tokoh()`. Identitas dibandingkan setelah normalisasi alias. Untuk kata ganti yang ambigu, `periksa_konteks_tokoh()` mencari bukti identitas pada maksimal tiga kalimat sebelumnya dalam blok yang sama. Pencarian dihentikan jika menemukan subjek kelahiran yang bertentangan atau penanda ambiguitas tertentu.

Untuk beberapa relasi, judul dokumen atau kalimat sebelumnya membantu memeriksa topik (misalnya nama perundingan). Judul bukan sumber jawaban pengganti kalimat bukti. Validasi ini merupakan heuristik; tidak membuktikan kesesuaian semantik semua kalimat secara umum.

## 5. Contoh integrasi

Jalankan dari direktori utama repository:

```python
import json
from question_processing import process_question
from passage_retrieval import cari
from answer_processing import ambil_jawaban

pertanyaan = "Kapan Mohammad Hatta lahir?"
info = process_question(pertanyaan)
kandidat = cari(info["normalized_question"], k=20)

with open("korpus_kalimat_final.json", encoding="utf-8") as f:
    korpus = json.load(f)["kalimat"]

print(ambil_jawaban(info, kandidat, kalimat_korpus=korpus))
```

Hasil pada contoh pengujian diagnostik:

```python
{'jawaban': '12 Agustus 1902', 'id_kalimat': 'D08-B0004-K003'}
```

Contoh ini menggunakan query ternormalisasi sebagai rekomendasi integrasi. Evaluator resmi yang sudah tersedia masih menggunakan query asli. `k=20` adalah konfigurasi pengujian, bukan nilai optimal untuk semua pertanyaan.

## 6. Evaluasi pengembangan (25 November 2026)

### 6.1 Regresi 21 pertanyaan resmi

Perintah dari direktori repository di PowerShell:

```powershell
$env:PYTHONPATH = (Get-Location).Path
python tests/test_evaluasi_resmi.py
```

Konfigurasi: Question Processing → BM25 (query asli, k=20) → Answer Processing. Exact Match menggunakan perbandingan teks jawaban dengan acuan setelah `strip()` dan `casefold()`.

| Tipe | Sebelum | Sesudah |
|---|---:|---:|
| DATE | 5/5 | 5/5 |
| PER | 8/8 | 8/8 |
| LOC | 5/5 | 5/5 |
| NUM | 1/1 | 1/1 |
| MISC | 2/2 | 2/2 |
| **Total** | **21/21** | **21/21** |

Seluruh ID sumber yang ditampilkan pada 21 pertanyaan juga tetap sama dengan baseline. Exact Match tidak mengukur akurasi bukti secara terpisah. Hasil 100% ini merupakan hasil end-to-end pada set pengembangan yang digunakan dalam penyesuaian aturan, bukan akurasi generalisasi atau kinerja AP secara terisolasi.

### 6.2 Pengujian diagnostik 14 pertanyaan

Dijalankan pada versi revisi dengan BM25 Top-20 menggunakan query asli dan query ternormalisasi. Kedua konfigurasi menghasilkan jawaban dan ID sumber yang sama pada seluruh 14 kasus.

| Pertanyaan (ringkas) | Jawaban versi revisi | Interpretasi |
|---|---|---|
| Wakil presiden yang ditunjuk PPKI | Mohammad Hatta | Benar |
| Wakil presiden pertama Indonesia | Mohammad Hatta | Benar |
| Presiden pertama Indonesia | Soekarno | Benar |
| Kapan Mohammad Hatta lahir? | 12 Agustus 1902 | Benar |
| Kapan Moh. Hatta lahir? | 12 Agustus 1902 | Benar |
| Pada tanggal berapa Mohammad Hatta lahir? | 12 Agustus 1902 | Benar |
| Kapan Soekarno lahir? | None | Belum terjawab |
| Kapan Indonesia merdeka? | None | Belum terjawab |
| Jumlah negara bagian Amerika Serikat | None | Penolakan kandidat sesuai target diagnostik |
| Kepala delegasi RI dalam perundingan fiktif | None | Penolakan kandidat sesuai target diagnostik |
| Kapan Universitas Brawijaya didirikan? | None | Penolakan kandidat sesuai target diagnostik |
| Mengapa Jepang menyerah? | None | Di luar cakupan |
| Dipilih sebagai panglima TKR | Sudirman | Benar |
| Pemimpin delegasi RI dalam Perundingan Roem-Roijen | Mohamad Roem | Benar |

Ringkasan: 8 dari 10 pertanyaan factoid yang ditargetkan memiliki jawaban berhasil dijawab; 2 belum terjawab; 3 kasus negatif ditolak; 1 di luar cakupan. Tidak ditemukan jawaban faktual yang salah dalam kumpulan ini. `None` pada pertanyaan yang sebenarnya bisa dijawab tidak dihitung sebagai jawaban benar. Ini yang masih 80%, akan diperbaiki secara berkala.

### 6.3 Analisis kegagalan dan keterbatasan evaluasi

- Pertanyaan kelahiran Soekarno: bukti menggunakan `dilahirkan` atau format biografi, sedangkan query menggunakan `lahir`. Audit peringkat BM25 menunjukkan dua bukti relevan berada di luar Top-20. Ekstraksi format biografi belum didukung secara umum.
- Pertanyaan kemerdekaan Indonesia: variasi `merdeka` dan `memproklamasikan kemerdekaan` membuat pencarian berbasis token terbatas. Bukti yang ditelusuri berada di luar Top-20; aturan predikat kemerdekaan juga belum lengkap. Penolakan tanggal peringatan lebih baik daripada jawaban salah, tetapi belum merupakan jawaban benar.
- Pengujian diagnostik telah digunakan untuk merancang revisi, sehingga bukan held-out test. Daftar asli 15 pertanyaan tambahan tim belum dievaluasi ulang secara lengkap dalam hasil ini.
- Pengujian unit dan regresi lain pada versi lama tidak otomatis dianggap lulus pada versi revisi. Belum ada hasil pelaksanaan ulang seluruh suite tersebut.

## 7. Keterbatasan dan tindak lanjut integrasi

Normalisasi dari modul yang sudah dibuat menjadi solusi sementara sambil menunggu modul normalisasi terupdate. Alias `Bung Hatta` belum tersedia pada kamus yang diperiksa. Pencocokan entitas, relasi, singkatan, dan rujukan antarkalimat tetap berbasis pola; tidak mencakup semua konstruksi bahasa Indonesia. Validasi lebih ketat dapat menolak jawaban benar. Bilangan dalam bentuk kata, variasi penulisan tanggal, dan bentuk objek lain masih terbatas.

Koordinasi berikutnya: menyatukan normalisasi korpus dan pertanyaan, meneruskan `normalized_question` ke BM25 pada notebook integrasi, menguji perluasan query untuk variasi kosakata, dan melakukan evaluasi independen beserta analisis kesalahan. Antarmuka `ambil_jawaban()` tetap sama.
