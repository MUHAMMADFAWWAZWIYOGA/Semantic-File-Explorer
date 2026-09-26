import os
import json
import csv
import docx

DATASET_DIR = "synthetic_dataset"
GROUND_TRUTH_FILE = "ground_truth.json"

dataset = {
    "finance": {
        "Q3_report_v1.txt": "Laporan keuangan Q3. Pendapatan menurun 10%. Perlu revisi oleh Budi.",
        "Q3_report_FINAL.docx": "Laporan keuangan Q3 FINAL. Pendapatan menurun 5% setelah audit. Dokumen ini yang sudah direvisi secara resmi.",
        "Q4_report_draft.txt": "Draf awal untuk laporan keuangan Q4. Estimasi laba naik 20%.",
        "budget_2027.csv": [["Item", "Cost"], ["Server", "5000"], ["Marketing", "2000"]]
    },
    "clients": {
        "client_A_presentation.md": "# Presentasi Klien A\nIni adalah versi final dari materi pitch deck untuk klien A terkait proyek infrastruktur AI.",
        "client_B_notes.txt": "Catatan meeting client B tanggal 12 September. Membahas kontrak Semantic Explorer."
    },
    "personal": {
        "diary.txt": "Hari ini saya mulai menulis agen AI untuk mencari file."
    },
    "archive_noise": {
        "old_Q3.txt": "Laporan keuangan Q3 lama. Jangan gunakan ini.",
        "junk.txt": "",
        "random_notes.txt": "Hanya catatan acak tentang laporan."
    }
}

queries = [
    {
        "query": "laporan keuangan Q3 yang sudah direvisi",
        "expected_path": "finance/Q3_report_FINAL.docx"
    },
    {
        "query": "file presentasi klien A versi final",
        "expected_path": "clients/client_A_presentation.md"
    },
    {
        "query": "catatan meeting client B",
        "expected_path": "clients/client_B_notes.txt"
    },
    {
        "query": "draf laporan keuangan kuartal 4",
        "expected_path": "finance/Q4_report_draft.txt"
    },
    {
        "query": "berapa biaya server untuk budget 2027",
        "expected_path": "finance/budget_2027.csv"
    }
]

def generate():
    if not os.path.exists(DATASET_DIR):
        os.makedirs(DATASET_DIR)
        
    for folder, files in dataset.items():
        folder_path = os.path.join(DATASET_DIR, folder)
        if not os.path.exists(folder_path):
            os.makedirs(folder_path)
            
        for filename, content in files.items():
            file_path = os.path.join(folder_path, filename)
            
            if filename.endswith(".docx"):
                doc = docx.Document()
                doc.add_paragraph(content)
                doc.save(file_path)
            elif filename.endswith(".csv"):
                with open(file_path, "w", newline="", encoding="utf-8") as f:
                    writer = csv.writer(f)
                    writer.writerows(content)
            else:
                with open(file_path, "w", encoding="utf-8") as f:
                    f.write(content)
                
    with open(GROUND_TRUTH_FILE, "w", encoding="utf-8") as f:
        json.dump(queries, f, indent=4)
        
    print(f"Dataset sintetis (Teks, DOCX, CSV, + Noise) dibuat di '{DATASET_DIR}'.")

if __name__ == "__main__":
    generate()
