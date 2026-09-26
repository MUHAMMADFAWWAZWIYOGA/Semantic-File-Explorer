import os
import csv
import math
import docx
import re
import json
from collections import Counter

class SandboxSafetyError(Exception):
    pass

class SemanticFileExplorer:
    def __init__(self, root_dir, index_file="semantic_index.json"):
        self.root_dir = os.path.abspath(root_dir)
        self.index_file = os.path.join(self.root_dir, index_file)
        
        # State Indeks
        self.documents = {}
        self.vocab = set()
        self.idf = {}
        
        self.build_incremental_index()

    def _is_safe_path(self, path):
        abs_path = os.path.abspath(os.path.join(self.root_dir, path))
        return abs_path.startswith(self.root_dir)

    def tokenize(self, text):
        text = text.lower()
        text = re.sub(r'[^a-z0-9\s]', ' ', text)
        return [word for word in text.split() if len(word) > 1]

    def tool_read_file(self, path):
        if not self._is_safe_path(path):
            return {"error": "Akses ditolak: di luar sandbox."}
        full_path = os.path.join(self.root_dir, path)
        if not os.path.isfile(full_path):
            return {"error": "File tidak ditemukan."}
            
        try:
            if full_path.endswith(".docx"):
                doc = docx.Document(full_path)
                return "\n".join([p.text for p in doc.paragraphs])
            elif full_path.endswith(".csv"):
                with open(full_path, "r", encoding="utf-8") as f:
                    reader = csv.reader(f)
                    return "\n".join([", ".join(row) for row in reader])
            else:
                with open(full_path, 'r', encoding='utf-8') as f:
                    return f.read()
        except UnicodeDecodeError:
            return {"error": "Format file tidak didukung."}
        except Exception as e:
            return {"error": str(e)}

    def load_cached_index(self):
        """Memuat state indeks sebelumnya jika ada."""
        if os.path.exists(self.index_file):
            try:
                with open(self.index_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception:
                return {}
        return {}

    def save_cached_index(self):
        """Menyimpan state indeks ke disk."""
        # Kita hanya simpan metadata esensial untuk menghemat ruang
        cache_data = {}
        for path, data in self.documents.items():
            cache_data[path] = {
                "mtime": data["mtime"],
                "tf": data["tf"],
                "length": data["length"],
                "content": data["content"] # Disimpan untuk evidence post-check
            }
        try:
            with open(self.index_file, 'w', encoding='utf-8') as f:
                json.dump(cache_data, f)
        except Exception as e:
            print(f"Gagal menyimpan cache: {e}")

    def build_incremental_index(self):
        """
        Membangun Indeks Secara Inkremental (Hanya memproses file yang berubah/baru).
        Sangat efisien untuk skala 10.000+ dokumen.
        """
        cached_index = self.load_cached_index()
        doc_freqs = {} 
        
        current_files = set()
        updated_count = 0

        # Pass 1: Scanning dan Deteksi Perubahan
        for root, _, files in os.walk(self.root_dir):
            for file in files:
                if file == os.path.basename(self.index_file):
                    continue # Skip file indeks itu sendiri
                    
                if file.endswith(('.txt', '.md', '.py', '.csv', '.docx')):
                    rel_path = os.path.relpath(os.path.join(root, file), self.root_dir).replace("\\", "/")
                    full_path = os.path.join(root, file)
                    current_files.add(rel_path)
                    
                    try:
                        mtime = os.path.getmtime(full_path)
                    except:
                        continue

                    # Cek apakah file baru atau dimodifikasi
                    needs_update = True
                    if rel_path in cached_index:
                        if cached_index[rel_path]["mtime"] == mtime:
                            needs_update = False
                            
                    if needs_update:
                        # File berubah atau baru, kita baca ulang kontennya
                        content = self.tool_read_file(rel_path)
                        if isinstance(content, str) and content.strip():
                            tokens = self.tokenize(content)
                            if tokens:
                                self.documents[rel_path] = {
                                    "mtime": mtime,
                                    "content": content,
                                    "tf": dict(Counter(tokens)),
                                    "length": len(tokens),
                                    "vector": {}
                                }
                                updated_count += 1
                    else:
                        # File tidak berubah, muat dari cache langsung tanpa I/O disk berat
                        self.documents[rel_path] = {
                            "mtime": cached_index[rel_path]["mtime"],
                            "content": cached_index[rel_path]["content"],
                            "tf": cached_index[rel_path]["tf"],
                            "length": cached_index[rel_path]["length"],
                            "vector": {}
                        }

        # Menghapus file dari index jika sudah dihapus secara fisik
        for path in list(self.documents.keys()):
            if path not in current_files:
                del self.documents[path]
                updated_count += 1

        if not self.documents:
            return

        # Pass 2: Re-kalkulasi Global Term Frequency (Karena ada dokumen yg nambah/hilang)
        doc_count = len(self.documents)
        for path, data in self.documents.items():
            for word in data["tf"].keys():
                doc_freqs[word] = doc_freqs.get(word, 0) + 1
                self.vocab.add(word)

        # Pass 3: Hitung IDF & Vektor akhir
        for word, count in doc_freqs.items():
            self.idf[word] = math.log(doc_count / count)

        for path, data in self.documents.items():
            length = data["length"]
            for word, count in data["tf"].items():
                tf_val = count / length
                data["vector"][word] = tf_val * self.idf[word]
                
        # Simpan kembali ke cache jika ada modifikasi
        if updated_count > 0:
            print(f"[Indexer] Mendeteksi {updated_count} perubahan dokumen. Menyimpan indeks terbaru...")
            self.save_cached_index()
        else:
            print(f"[Indexer] Tidak ada perubahan dokumen. Menggunakan cache seutuhnya secara kilat.")

    def tool_semantic_search(self, query):
        query_tokens = self.tokenize(query)
        if not query_tokens:
            return []

        query_tf = Counter(query_tokens)
        query_vec = {}
        for word, count in query_tf.items():
            if word in self.idf:
                tf_val = count / len(query_tokens)
                query_vec[word] = tf_val * self.idf[word]

        mag_query = math.sqrt(sum(val**2 for val in query_vec.values()))
        if mag_query == 0: return []

        results = []
        for path, data in self.documents.items():
            doc_vec = data["vector"]
            dot_product = sum(query_vec.get(word, 0) * doc_vec.get(word, 0) for word in query_vec.keys())
            mag_doc = math.sqrt(sum(val**2 for val in doc_vec.values()))
            
            cosine_sim = dot_product / (mag_query * mag_doc) if mag_doc > 0 else 0
                
            if cosine_sim > 0.05:
                best_word = max(query_tokens, key=lambda w: query_vec.get(w, 0))
                content_lower = data["content"].lower()
                idx = content_lower.find(best_word)
                if idx == -1: idx = 0
                start = max(0, idx - 40)
                end = min(len(data["content"]), idx + 100)
                span = data["content"][start:end].strip()
                
                results.append({
                    "path": path,
                    "span": span,
                    "score": cosine_sim
                })

        results.sort(key=lambda x: x["score"], reverse=True)
        return results

    def post_check_evidence(self, path, evidence_span):
        content = self.tool_read_file(path)
        if isinstance(content, dict) and "error" in content:
            return "low"
            
        clean_span = " ".join(evidence_span.split())
        clean_content = " ".join(content.split())
        
        if clean_span in clean_content:
            return "high"
        return "low"

    def tool_list_dir(self, path=""):
        if not self._is_safe_path(path):
            return {"error": "Akses ditolak: di luar sandbox."}
        full_path = os.path.join(self.root_dir, path)
        if not os.path.exists(full_path):
            return {"error": "Path tidak ditemukan."}
        try:
            return os.listdir(full_path)
        except Exception as e:
            return {"error": str(e)}

    def query(self, user_query):
        search_results = self.tool_semantic_search(user_query)
        
        if not search_results:
            folders = self.tool_list_dir()
            return {
                "path": None,
                "relevance_reason": f"Gagal pencarian cosinus. Eksplorasi folder: {folders}",
                "evidence_span": None,
                "confidence": "low"
            }
            
        best_candidate = search_results[0]
        path = best_candidate["path"]
        span = best_candidate["span"]
        score = best_candidate["score"]
        
        confidence = self.post_check_evidence(path, span)
        
        return {
            "path": path,
            "relevance_reason": f"Agen menggunakan Incremental TF-IDF. Similarity: {score:.4f}",
            "evidence_span": span,
            "confidence": confidence
        }

if __name__ == "__main__":
    print("==========================================================")
    print(" 🤖 SEMANTIC FILE EXPLORER AI - (INCREMENTAL INDEXING)    ")
    print("==========================================================")
    
    explorer = SemanticFileExplorer("synthetic_dataset")
    print(f"[Sistem] Indeks Aktif: {len(explorer.documents)} dokumen.")
    
    while True:
        try:
            q = input("\n[Anda] Masukkan query pencarian (atau 'exit'): ")
            if q.lower() in ['exit', 'quit']:
                break
                
            res = explorer.query(q)
            print("\n[Agen AI] Hasil Temuan:")
            print(f" 📂 Path    : {res['path']}")
            print(f" 💡 Alasan  : {res['relevance_reason']}")
            print(f" 🔍 Bukti   : \"{res['evidence_span']}\"")
            print(f" 🛡️  Tingkat : {res['confidence']}")
        except KeyboardInterrupt:
            break
