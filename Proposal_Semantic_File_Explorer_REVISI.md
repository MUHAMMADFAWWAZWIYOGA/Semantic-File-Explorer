**PROPOSAL PENELITIAN**

**Evidence-Grounded AI Agents for Semantic File Retrieval on Local Systems**

*Judul kerja (Bahasa Indonesia):*

*Penjelajah Berkas Semantik: Agen AI Berbasis Bukti untuk Memahami Makna dan Menemukan File pada Sistem Berkas Lokal*

Status: Proyek Selesai & Terimplementasi |  September 2026  |  Eksperimen & Benchmark Tersedia

# 1. Latar Belakang

Pengguna komputer sehari-hari menyimpan ratusan hingga puluhan ribu berkas dalam struktur folder yang sering tidak rapi: nama file acak, duplikat, versi bercampur, dan hierarki yang tidak konsisten. Cara klasik mencari file—berdasarkan nama atau kata kunci—gagal ketika pengguna hanya mengingat makna atau konteks (“laporan keuangan Q3 yang sudah direvisi”, “file presentasi klien A versi final”).

Kemajuan large language models (LLM) dan agen AI memungkinkan sistem membaca isi berkas, menafsirkan struktur folder, dan menjawab pertanyaan dalam bahasa alami. Namun, sebagian besar solusi saat ini terpecah: (1) pencarian semantik berbasis embedding tanpa eksplorasi folder yang adaptif; (2) agen tool-use (ls, read, grep) yang belum wajib menyertakan bukti; atau (3) asisten cloud yang mengorbankan privasi data lokal.

Penelitian ini mengusulkan Semantic File Explorer: agen AI yang memahami makna berkas dalam konteks sistem berkas lokal, menjawab query bahasa alami dengan path dan kutipan bukti, serta beroperasi secara aman (read-only / gated). Keluaran yang diharapkan adalah sistem yang dapat dievaluasi secara kuantitatif, bukan sekadar demonstrasi.

# 2. Rumusan Masalah

Berdasarkan latar belakang di atas, penelitian ini merumuskan masalah sebagai berikut:

Bagaimana membangun dan mengevaluasi agen AI yang dapat memahami makna berkas dan struktur folder lokal, lalu menemukan berkas yang relevan terhadap query bahasa alami, dengan jawaban yang dilengkapi bukti (path dan span teks) serta kontrol keamanan yang memadai?

# 3. Pertanyaan Penelitian

* Seberapa akurat agen berbasis LLM menemukan berkas relevan dari query bahasa alami pada folder nyata (bukan hanya pencocokan nama atau kata kunci)?

* Apakah penggabungan struktur folder, metadata, isi berkas, dan relasi antar berkas meningkatkan precision/recall dibandingkan pure semantic search atau pure tool-use (ls/grep saja)?

* Jenis kesalahan apa yang paling sering muncul: salah path, salah tafsir makna, gagal multimodal (PDF scan/gambar), atau klaim tanpa dukungan bukti?

* Apakah kewajiban menyertakan evidence (path + span) mengurangi jawaban yang tidak dapat diverifikasi tanpa menurunkan recall secara signifikan?

* (Opsional) Seberapa baik pendekatan ini bertahan pada skala folder besar (10.000–100.000 berkas) dengan indeks lokal dan pembaruan incremental?

# 4. Tujuan Penelitian

* Merancang arsitektur agen AI untuk pemahaman makna dan navigasi semantik atas sistem berkas lokal.

* Membangun pipeline yang menggabungkan eksplorasi folder (tool-use) dengan retrieval semantik dan kewajiban evidence grounding.

* Menyusun dataset evaluasi kecil–sedang (query → berkas target + alasan) dari folder sintetis dan subset folder nyata.

* Membandingkan metode usulan terhadap baseline (keyword, vector RAG, agent tool-only) dengan metrik retrieval dan faithfulness.

* Menganalisis tipologi kesalahan dan batasan sistem, termasuk aspek privasi dan keamanan akses berkas.

# 5. Kontribusi yang Diusulkan

* Arsitektur Semantic File Explorer yang memadukan tree folder, metadata, parsing multi-format, dan agen tool-use dengan kewajiban bukti.

* Protokol evaluasi dan dataset anotasi untuk tugas “natural-language file finding” dengan evidence grounding.

* Perbandingan kuantitatif terhadap baseline dan analisis kesalahan yang dapat direproduksi.

* Prinsip keamanan praktis: sandbox path, read-only default, dan tidak ada write tanpa konfirmasi pengguna.

# 6. Studi Terkait dan Posisi Kebaruan

## 6.1 Agen dengan Filesystem Tools

Agen modern sering diberi tool mirip shell (ls, read, grep, glob, parse_file). Karya seperti fs-explorer (LlamaIndex), agentic file search, dan deep agents (LangChain) menunjukkan bahwa eksplorasi folder dapat mengungguli pure RAG pada beberapa skenario karena model dapat menavigasi struktur dan membaca selektif. Letta Filesystem merepresentasikan dokumen sebagai folder/file dengan tool open, grep, dan semantic_search.

## 6.2 Semantic File Search

Sistem desktop dan open-source (misalnya File Brain, directory-indexer, FilePilot AI, pdf-mcp) mengindeks isi berkas secara lokal dan mendukung query berdasarkan makna. Fokusnya umumnya retrieval, bukan agen yang merencanakan eksplorasi multi-langkah dengan bukti wajib.

## 6.3 Semantic / Agent-Native File System

LSFS mengusulkan file system berbasis makna untuk AIOS. YoloFS (arah SOSP 2026) menekankan kontrol: introspect effects, undo mutations, dan gate accesses agar agen tidak merusak berkas. Agent FS dan penelitian filesystem-based memory mengkaji filesystem sebagai medium memori jangka panjang agen.

## 6.4 Gap yang Ditargetkan

* Pemahaman makna lintas format yang terintegrasi dengan hierarki folder dan relasi antar berkas (versi, draft vs final) masih lemah.

* Jarang ada kewajiban evidence grounding (path + span) pada jawaban “file finding”.

* Benchmark standar untuk natural-language file retrieval pada folder nyata masih terbatas.

* Evaluasi robustness terhadap folder berantakan (nama acak, duplikat, nested tidak konsisten) jarang dilakukan.

* Dukungan konteks multibahasa / pola penamaan lokal (termasuk Bahasa Indonesia) hampir tidak ada.

* Trade-off privasi on-device, skala indeks, dan latency belum banyak diukur bersama akurasi.

Kebaruan yang diuji dalam penelitian ini bukan sekadar “memakai LLM untuk mencari file”, melainkan evaluasi sistematis agen yang memahami makna berkas dalam konteks filesystem lokal dengan evidence grounding dan perbandingan baseline yang jelas.

## 6.5 Perbandingan dengan Perangkat Pencarian Komersial

Selain sistem riset di atas, sejumlah produk komersial sudah menawarkan pencarian berkas berbasis makna pada perangkat konsumen, misalnya fitur pencarian berbasis AI pada Windows (Copilot/Recall), Spotlight yang diperkaya AI pada macOS, dan pencarian semantik bawaan Google Drive. Proposal ini membedakan diri dari produk tersebut dalam tiga hal: (1) produk komersial umumnya tertutup (closed-source) sehingga metode dan metrik evaluasinya tidak dapat diperiksa ulang secara independen; (2) belum ada laporan publik yang menunjukkan kewajiban evidence grounding (path + span kutipan) pada jawabannya; dan (3) benchmark yang dipakai vendor bersifat internal dan tidak dapat dibandingkan langsung dengan baseline akademik. Jika akses tersedia, penelitian ini akan menyertakan minimal satu produk komersial sebagai titik referensi kualitatif — bukan sebagai baseline kuantitatif utama — mengingat keterbatasan akses ke sistem internalnya.

# 7. Metode

## 7.1 Gambaran Arsitektur

Sistem terdiri dari empat lapisan:

* Lapisan representasi — pohon folder, metadata (nama, ukuran, tanggal, tipe), dan konten ter-parse (teks, PDF, Office).

* Lapisan indeks — opsional: full-text + embedding untuk semantic search; pembaruan incremental.

* Lapisan agen — LLM dengan tools: list_dir, read_file, grep, semantic_search, parse_document; loop perencanaan–aksi–observasi.

* Lapisan evidence & safety — setiap jawaban wajib path + evidence span; akses dibatasi sandbox; write dinonaktifkan secara default.

## 7.2 Alur Kerja

* Pengguna mengajukan query bahasa alami.

* Agen merencanakan langkah: menelusuri folder relevan, mencari secara semantik, membaca cuplikan berkas.

* Agen mengumpulkan kandidat berkas beserta span pendukung.

* Agen menyusun jawaban terstruktur: daftar berkas, alasan singkat, path, dan evidence span.

* Post-check: verifikasi bahwa path ada dan evidence span berasal dari isi berkas; tandai unsupported jika gagal.

## 7.3 Format Keluaran

Setiap hasil direpresentasikan sebagai objek terstruktur, misalnya:

*{ "path": "...", "relevance_reason": "...", "evidence_span": "...", "confidence": "high|medium|low" }*

Nilai confidence tidak diklaim sebagai probabilitas terkalibrasi. Nilai ini dipetakan dari sinyal yang dapat diverifikasi pasca-hoc: high — evidence span lolos post-check (path valid dan span ditemukan verbatim dalam isi berkas) serta didukung lebih dari satu sinyal independen (mis. metadata dan isi berkas sejalan); medium — evidence span valid tetapi hanya didukung satu sinyal; low — post-check gagal namun jawaban tetap ditampilkan dengan peringatan unsupported. Skema pemetaan ini akan divalidasi terpisah lewat reliability diagram yang membandingkan label confidence dengan ketepatan aktual pada set uji (§9.3).

## 7.4 Baseline Pembanding

## 7.5 Spesifikasi Teknis (Kandidat)

Kandidat komponen teknis berikut akan diuji pada fase prototipe (Fase 1–2, §11) dan difinalisasi setelah audit ketersediaan API dan anggaran (§11.2):

* Model LLM utama — kandidat model kelas frontier dengan kemampuan tool-use kuat untuk eksperimen inti, ditambah minimal satu model open-weight untuk menekan biaya pada eksperimen skala dan ablasi (lihat mitigasi biaya, §13).

* Model embedding — model embedding multibahasa (mendukung Bahasa Indonesia) untuk indeks semantic_search, dipilih berdasarkan benchmark retrieval publik sebelum implementasi.

* Vector store / indeks — pustaka indeks lokal ringan yang konsisten dengan prinsip pemrosesan on-device (§10).

* Strategi chunking untuk baseline Vector RAG — ukuran chunk dan overlap ditentukan lewat uji coba kecil sebelum eksperimen utama dan dilaporkan demi reproduksibilitas.

* Kerangka agent loop — dibangun di atas pustaka orkestrasi tool-use yang mendukung logging langkah demi langkah, agar setiap keputusan (folder dibuka, berkas dibaca) dapat direkonstruksi untuk analisis kesalahan (§9.2).

## 7.6 Manajemen Skala dan Context Window

Untuk menjawab RQ5 (§3) tentang skala folder besar, agen tidak diberi seluruh pohon folder sekaligus dalam konteks. Empat strategi akan diuji: (1) eksplorasi bertingkat — list_dir hanya menampilkan direktori teratas, agen memilih submasuk secara adaptif; (2) ringkasan folder (folder summary) yang di-cache dan diperbarui secara incremental agar agen dapat menilai relevansi folder tanpa membuka seluruh isi; (3) batas keras jumlah langkah (max iterations) dan token per query untuk mencegah loop tak terkendali sekaligus membatasi biaya; (4) fallback ke pure semantic search bila anggaran langkah agen habis sebelum jawaban ditemukan. Keempatnya dibandingkan pada eksperimen bersyarat skala 10.000–100.000 berkas (§10), dengan latency dan biaya token dilaporkan sebagai metrik utama, bukan hanya akurasi.

# 8. Data dan Anotasi

* Folder sintetis — disusun dengan skenario terkontrol (versi dokumen, duplikat, nama ambigu, multi-format).

* Subset folder nyata — dokumen kerja/kuliah/proyek dengan izin; data dianonimkan bila perlu.

* Query set — 80–200 query bahasa alami (dan opsional Bahasa Indonesia) yang dipetakan ke satu atau lebih berkas target.

* Anotasi — untuk setiap query: path target, alasan relevansi, dan (jika memungkinkan) span bukti. Sebagian dianotasi ganda untuk inter-annotator agreement.

* Variasi kesulitan — query mudah (nama mirip), sedang (makna tanpa nama), sulit (multi-hop, versi, relasi antar file).

* Protokol inter-annotator agreement (IAA) — minimal 20% query dianotasi oleh dua anotator independen; kesepakatan diukur dengan Cohen’s kappa (target κ ≥ 0,6, setara "substantial agreement"); ketidaksepakatan diselesaikan lewat diskusi terdokumentasi atau anotator ketiga.

## 8.1 Tata Kelola Data dan Persetujuan Etik

Penggunaan folder nyata milik peserta memerlukan: (1) formulir informed consent tertulis yang menjelaskan data apa yang diakses, bagaimana dianonimkan, dan berapa lama disimpan; (2) tinjauan oleh komite/unit etik penelitian institusi sebelum pengumpulan data dimulai, jika disyaratkan; (3) opsi bagi peserta untuk menarik datanya kapan pun sebelum publikasi; dan (4) penghapusan data mentah (bukan hasil agregat) paling lambat pada akhir masa penelitian, dengan jadwal retensi eksplisit dicantumkan pada formulir consent.

# 9. Evaluasi

## 9.1 Metrik

* Precision@k dan Recall@k (k = 1, 3, 5) terhadap berkas target.

* MRR (Mean Reciprocal Rank) jika peringkat penting.

* Evidence faithfulness — proporsi jawaban dengan path valid dan span yang benar-benar mendukung klaim.

* Unsupported claim rate — jawaban tanpa bukti atau bukti tidak cocok.

* Latency dan biaya token per query.

* Error typology — salah path, salah makna, gagal parse, overconfidence, dll.

* Kepuasan pengguna (opsional, jika sumber daya memungkinkan) — studi kecil (n ≈ 10–15) memakai kuesioner ringkas (mis. adaptasi System Usability Scale) untuk menilai kepercayaan pengguna terhadap jawaban agen, sebagai pelengkap metrik otomatis di atas.

## 9.2 Protokol

Pisahkan set development (penyusunan prompt/tool) dan set uji.

Laporkan hasil per tingkat kesulitan query dan per tipe berkas (teks, PDF, Office).

Analisis kualitatif contoh sukses dan gagal yang dapat diperiksa ulang.

## 9.3 Analisis Statistik

Perbandingan antar metode (usulan vs. setiap baseline) diuji signifikansinya, bukan hanya dilaporkan sebagai selisih rata-rata. Untuk metrik per-query (precision@k, faithfulness), digunakan bootstrap resampling (≥ 1.000 iterasi) untuk interval kepercayaan 95%, dan uji berpasangan (mis. Wilcoxon signed-rank) antar metode pada query set yang sama, mengingat ukuran sampel (80–200 query) tidak selalu memenuhi asumsi normalitas. Ukuran efek (mis. rank-biserial correlation) dilaporkan berdampingan dengan p-value untuk menghindari overclaiming pada sampel kecil. Set development dan set uji dijaga terpisah secara ketat (§9.2) agar hasil signifikansi tidak bias oleh tuning berulang.

# 10. Ruang Lingkup dan Batasan

* Fokus pada read dan retrieval, bukan otomatisasi pemindahan/penghapusan berkas tanpa konfirmasi.

* Format prioritas: teks, Markdown, PDF, DOCX, XLSX, PPTX; gambar/scan sebagai perluasan bertahap.

* Skala pilot: ratusan hingga ribuan berkas; skala 100k sebagai eksperimen bersyarat.

* Privasi: desain mendukung pemrosesan lokal; cloud API hanya jika diizinkan dan dicatat dalam eksperimen.

* Penelitian ini menghasilkan peta kemampuan dan batasan sistem, bukan klaim produk siap pasar.

# 11. Anggaran, Tim, dan Sumber Daya

## 11.1 Tim dan Peran

Peran minimum yang dibutuhkan agar rencana kerja pada §12 realistis untuk dijalankan:

## 11.2 Estimasi Anggaran

Rincian berikut adalah kerangka anggaran yang perlu diisi dengan angka riil sesuai skala eksperimen final, kurs, dan penyedia API yang dipilih (§7.5):

## 11.3 Sumber Daya Komputasi dan Akses

Kebutuhan komputasi diperkirakan moderat pada skala pilot (§10): inference LLM per query, indeksasi embedding untuk ratusan–ribuan berkas, dan penyimpanan lokal untuk log evaluasi. Eksperimen skala besar (10.000–100.000 berkas, RQ5) bersifat bersyarat dan baru dijalankan bila anggaran kompute pada §11.2 mencukupi; jika tidak, penelitian akan melaporkan proyeksi skala berdasarkan hasil pilot alih-alih eksperimen penuh.

# 12. Rencana Kerja (Timeline Indikatif)

*Total estimasi durasi ≈ 24 minggu (≈ 6 bulan), dengan asumsi anotasi (Fase 3) dapat berjalan paralel dengan penyempurnaan pipeline (akhir Fase 2). Jadwal ini bergantung pada lamanya proses persetujuan etik (§8.1), yang sebaiknya diajukan sejak awal Fase 1 agar tidak menjadi hambatan kritis pada Fase 3.*

# 13. Risiko dan Mitigasi

* Akurasi parse PDF/scan rendah → prioritaskan format teks dulu; OCR sebagai modul terpisah.

* Dataset terlalu kecil → prioritaskan kualitas anotasi; laporkan sebagai pilot study.

* Biaya API tinggi → gunakan model open-weight lokal untuk sebagian eksperimen; catat biaya.

* Isu privasi folder nyata → anonimisasi, sandbox, dan informed consent jika melibatkan data pihak lain.

* Agent salah path / merusak data → read-only default, path allowlist, tidak ada write otomatis.

# 14. Hasil yang Diharapkan

Prototipe Semantic File Explorer yang dapat dijalankan pada folder lokal dengan jawaban berbukti.

Dataset evaluasi dan protokol anotasi yang dapat dibagikan (selama tidak melanggar privasi).

Hasil kuantitatif perbandingan metode beserta tipologi kesalahan.

Naskah ilmiah (konferensi/jurnal) yang menekankan evaluasi dan gap, bukan sekadar demo.

# 15. Struktur Makalah yang Direncanakan

* Introduction dan pertanyaan penelitian

* Related work (filesystem agents, semantic search, agent-native FS, safety)

* System design (arsitektur, tools, evidence protocol, safety)

* Dataset dan annotation protocol

* Experiments and results

* Error analysis and discussion

* Limitations and conclusion

# 16. Referensi Awal (untuk dilengkapi)

* Srivatsan, S. et al. "Don’t Let AI Agents YOLO Your Files: Information and Control in Agent-Native Filesystems." arXiv:2604.13536, 2026. Studi sistematis atas 290 laporan publik kegagalan agen pada filesystem; memperkenalkan primitif introspect/undo/gate yang relevan langsung dengan lapisan evidence & safety pada §7.1.

* Zhou, S., Yu, S., Wei, H., Wu, J., Ouyang, S., Jiao, Y., Pan, S., McAuley, J., Zhang, Y., Yu, T., & Han, J. "Filesystem-Based Memory for LLM Agents: Organization, Evolution, and Sustainability." arXiv:2607.26637, 2026. Temuan relevan: organisasi folder oleh agen menekan biaya retrieval namun tidak otomatis meningkatkan akurasi jawaban — argumen tambahan bagi penelitian ini untuk mengukur faithfulness dan akurasi secara terpisah dari efisiensi (§9.1), bukan mengasumsikan keduanya berkorelasi.

* Shi, Z., Mei, K., et al. "From Commands to Prompts: LLM-based Semantic File System for AIOS." arXiv:2410.11843, 2024 (dipresentasikan di ICLR 2025). Melaporkan peningkatan akurasi retrieval semantik ≥ 15% dan kecepatan 2,1× dibanding filesystem tradisional — menjadi salah satu acuan target performa kuantitatif untuk baseline Vector RAG pada §7.4.

*Catatan metodologis: seluruh entri di atas telah diverifikasi ulang lewat pencarian per September 2026 dan dilengkapi identitas penulis/identifier (arXiv) bila tersedia. Entri yang masih ditandai "[perlu diverifikasi ulang]" adalah sumber non-akademik (blog/repo vendor) yang perlu dicantumkan dengan tautan dan tanggal akses eksplisit sebelum proposal difinalisasi, mengikuti konvensi sitasi sumber web pada bidang ilmu komputer.*

* LlamaIndex "fs-explorer" dan studi perbandingan vector search vs. filesystem tools. [Perlu diverifikasi ulang sebelum draf final: cantumkan tautan repo/dokumentasi resmi dan tanggal akses, karena sumber ini berupa proyek/blog developer, bukan makalah yang di-peer-review.]

* LangChain, "How agents can use filesystems for context engineering" (blog engineering). [Perlu diverifikasi ulang: cantumkan URL dan tanggal akses; sumber non-akademik, gunakan hanya sebagai konteks industri, bukan klaim yang diuji secara empiris.]

* Letta Filesystem — antarmuka folder/file (open_file, grep_file, search_file) untuk agen dokumen. Catatan penting: per dokumentasi resmi, Letta Filesystem sejak itu dinyatakan "deprecated" dan digantikan oleh akses filesystem langsung serta context repositories (docs.letta.com, diakses September 2026) — relevan sebagai pelajaran desain: solusi berbasis chunk/embedding murni ditinggalkan demi akses file langsung, mendukung argumen §6.4 bahwa eksplorasi folder adaptif tetap dibutuhkan di samping semantic search.

* pdf-mcp, agentic file search, Agent FS, dan sistem semantic desktop search terkait. [Perlu diverifikasi ulang satu per satu sebelum draf final: masing-masing memerlukan tautan sumber resmi, versi, dan tanggal akses agar dapat disitasi secara akademik.]

*Catatan. Draf ini merupakan konsep awal untuk ditinjau. Belum ada pengumpulan data, eksperimen, atau hasil. Judul, ruang lingkup wilayah data, dan target venue dapat disesuaikan setelah audit ketersediaan folder uji dan sumber daya komputasi. Keberhasilan metode usulan tidak diasumsikan; jika tidak unggul terhadap baseline, temuan tersebut tetap menjawab pertanyaan penelitian.*
