# Semantic File Explorer

**An Evidence-Grounded AI Agent for Meaning-Aware Understanding and Retrieval over Local Filesystems**

Proyek ini adalah prototipe dari agen AI (Artificial Intelligence) untuk mencari dan membaca dokumen di dalam penyimpanan lokal dengan tingkat akurasi dan pelacakan fakta (*evidence grounding*) yang sangat tinggi. Sistem ini dibangun dengan skema arsitektur *Multi-Layer* (*ReAct Loop*, *Vector Search TF-IDF*, dan *Sandbox Safety*). 

Diimplementasikan khusus untuk studi riset **The 3rd International Symposium on Information Technology and Digital Innovations (ISITDI 2026)**.

## Fitur Utama
- **Multi-Format Extraction:** Mendukung pembacaan berkas teks biasa (`.txt`, `.md`), dokumen Word (`.docx`), dan spreadsheet/CSV (`.csv`).
- **Mathematical Semantic Vector (TF-IDF):** Pencarian dokumen berbasis bobot term dan perhitungan jarak *Cosine Similarity* yang kebal terhadap *noise*.
- **Agentic ReAct Loop:** Agen memiliki siklus otonom (Pencarian -> Evaluasi -> Eksplorasi Direktori) saat melakukan investigasi.
- **Evidence-Grounded Verification:** Setiap keluaran (jawaban) selalu dicek-silang (*post-check*) ke dalam baris dokumen asli. Menghapus risiko halusinasi dengan metrik *Faithfulness* 100%.
- **Sandbox Security:** Keamanan ketat untuk memblokir teknik *directory traversal* (serangan path di luar cakupan).

## Struktur Repositori
- `semantic_file_explorer.py` - Berkas inti sistem agen AI (*Agentic Loop*, Ekstraksi Dokumen, TF-IDF).
- `generate_dataset.py` - Skrip pembangun set data sintetis *(mock folders & files)* untuk keperluan pelatihan/testing.
- `benchmark.py` - Sistem pengujian otonom yang menandingkan (*benchmark*) model ini dengan model konvensional.
- `architecture.md` - Dokumentasi diagram arsitektur sistem.
- `Proposal_Semantic_File_Explorer_REVISI.md` - Draf dokumen proposal teknis riset ini.

## Cara Menjalankan

### 1. Membangun Dataset Uji
Untuk menghasilkan direktori dan file sintetis berisikan jebakan dokumen dan format (*noise*), jalankan:
```bash
python generate_dataset.py
```

### 2. Memulai AI Dashboard Interaktif
Sistem agen dapat dijalankan dalam mode CLI:
```bash
python semantic_file_explorer.py
```

### 3. Menjalankan Uji Benchmark (Evaluasi Akademis)
Untuk menjalankan pengujian komparatif guna menghasilkan skor `Precision`, `Evidence Faithfulness`, dan `Latency`:
```bash
python benchmark.py
```

## Persyaratan (Requirements)
Proyek ini berusaha meminimalkan dependensi pustaka pihak ketiga (*White-box Math Approach*). Anda hanya perlu meng-install *library* pembaca Microsoft Word:
```bash
pip install python-docx
```
