# Arsitektur Semantic File Explorer (Terimplementasi)

Berdasarkan proposal ISITDI 2026, berikut adalah arsitektur teknis dari proyek **Semantic File Explorer** yang telah berhasil dibangun.

```mermaid
flowchart TD
    User([Pengguna]) -->|Query Bahasa Alami| CLI[Interactive Dashboard / CLI]
    CLI --> AgentLayer[Lapisan Agen (ReAct Loop)]
    
    subgraph SystemArchitecture [Sistem Semantic File Explorer]
        AgentLayer -->|Plan: Cari File / List Folder| Tools[Filesystem Tools]
        
        Tools -->|Multi-Format Reader (.txt, .md, .docx, .csv)| RepLayer[Lapisan Representasi]
        Tools -->|Semantic Search| IndexLayer[Lapisan Indeks Semantik]
        
        RepLayer -->|Konten Ekstrak| IndexLayer
        RepLayer -->|Pohon Folder, Metadata| Safety[Lapisan Evidence & Safety]
        IndexLayer -->|Kandidat Berkas| Safety
        
        Safety -->|Sandbox Anti-Traversal| Tools
        Safety -->|Verifikasi Path & Span (Post-Check)| AgentLayer
    end
    
    AgentLayer -->|Format Keluaran JSON| Output([Output Berbukti / Evidence-Grounded])
    
    %% Keterangan Komponen
    classDef layer fill:#f9f,stroke:#333,stroke-width:2px;
    class RepLayer,IndexLayer,AgentLayer,Safety layer;
```

## Detail Lapisan (Layers):
1. **Lapisan Representasi (Multi-Format)**: Memetakan hierarki pohon folder dan mem-*parsing* konten file `.txt`, `.md`, `.docx`, dan `.csv` menggunakan library bawaan Python dan ekstensi.
2. **Lapisan Indeks**: Indeks lokal menggunakan *Vector RAG mock* (berbasis similiaritas dan penalaran konteks spesifik, termasuk *noise filtering*).
3. **Lapisan Agen (ReAct Loop)**: Menggunakan alur *Reasoning and Acting*. Jika pencarian pertama gagal, agen melakukan evaluasi ulang (re-plan) untuk menelusuri direktori dengan `tool_list_dir`.
4. **Lapisan Evidence & Safety**: Menyediakan *sandbox* keamanan mutlak, operasi *read-only*, dan fungsi verifikasi *post-check* untuk memastikan jawaban agen 100% berlandaskan data.
