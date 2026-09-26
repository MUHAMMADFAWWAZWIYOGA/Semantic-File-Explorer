import os
import csv
import math
import docx
import re
from collections import Counter

class SandboxSafetyError(Exception):
    pass

class SemanticFileExplorer:
    def __init__(self, root_dir):
        self.root_dir = os.path.abspath(root_dir)
        self.documents = {}
        self.vocab = set()
        self.idf = {}
        self.build_tfidf_index()

    def _is_safe_path(self, path):
        abs_path = os.path.abspath(os.path.join(self.root_dir, path))
        return abs_path.startswith(self.root_dir)

    def tokenize(self, text):
        """Membersihkan dan memecah teks menjadi token (kata dasar)."""
        text = text.lower()
        # Mengganti karakter non-alfanumerik dengan spasi
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
            return {"error": "Format file tidak didukung (bukan teks murni)."}
        except Exception as e:
            return {"error": str(e)}

    def build_tfidf_index(self):
        """Memindai seluruh folder dan membangun indeks TF-IDF (Matematis)."""
        doc_count = 0
        doc_freqs = {} # freq kata -> jumlah dokumen yang mengandung kata
        
        # Pass 1: Baca dokumen dan hitung frekuensi term
        for root, _, files in os.walk(self.root_dir):
            for file in files:
                if file.endswith(('.txt', '.md', '.py', '.csv', '.docx')):
                    rel_path = os.path.relpath(os.path.join(root, file), self.root_dir)
                    content = self.tool_read_file(rel_path)
                    
                    if isinstance(content, str) and content.strip():
                        tokens = self.tokenize(content)
                        if not tokens: continue
                        
                        doc_count += 1
                        tf = Counter(tokens)
                        
                        self.documents[rel_path] = {
                            "content": content,
                            "tokens": tokens,
                            "tf": tf,
                            "length": len(tokens),
                            "vector": {} # akan diisi di Pass 2
                        }
                        
                        for word in tf.keys():
                            doc_freqs[word] = doc_freqs.get(word, 0) + 1
                            self.vocab.add(word)

        if doc_count == 0: return

        # Pass 2: Hitung nilai IDF dan Vektor Dokumen
        for word, count in doc_freqs.items():
            # IDF = log(N / df)
            self.idf[word] = math.log(doc_count / count)

        for path, data in self.documents.items():
            length = data["length"]
            for word, count in data["tf"].items():
                tf_val = count / length
                data["vector"][word] = tf_val * self.idf[word]

    def tool_semantic_search(self, query):
        """
        Pencarian berbasis Vektor Semantik menggunakan TF-IDF dan Cosine Similarity.
        Sangat akademis dan tahan terhadap noise/frekuensi kata umum.
        """
        query_tokens = self.tokenize(query)
        if not query_tokens:
            return []

        # Hitung vektor query
        query_tf = Counter(query_tokens)
        query_vec = {}
        for word, count in query_tf.items():
            if word in self.idf:
                tf_val = count / len(query_tokens)
                query_vec[word] = tf_val * self.idf[word]

        # Menghitung magnitudo query
        mag_query = math.sqrt(sum(val**2 for val in query_vec.values()))
        if mag_query == 0: return []

        results = []
        for path, data in self.documents.items():
            doc_vec = data["vector"]
            
            # Hitung dot product
            dot_product = sum(query_vec.get(word, 0) * doc_vec.get(word, 0) for word in query_vec.keys())
            
            # Hitung magnitudo dokumen
            mag_doc = math.sqrt(sum(val**2 for val in doc_vec.values()))
            
            # Cosine similarity
            if mag_doc > 0:
                cosine_sim = dot_product / (mag_query * mag_doc)
            else:
                cosine_sim = 0
                
            if cosine_sim > 0.05: # Threshold sensitivitas
                # Ekstrak span cerdas (mencari kalimat yang mengandung kata berbobot tertinggi)
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

        # Urutkan berdasarkan similarity tertinggi
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
        """Agen Berbasis ReAct dan TF-IDF"""
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
            "relevance_reason": f"Agen menggunakan TF-IDF & Cosine Sim. Kesamaan Vektor: {score:.4f}",
            "evidence_span": span,
            "confidence": confidence
        }

if __name__ == "__main__":
    print("==========================================================")
    print(" 🤖 SEMANTIC FILE EXPLORER AI - (ADVANCED TF-IDF VERSION) ")
    print("==========================================================")
    
    print("[Sistem] Mengindeks dokumen dan menghitung pembobotan vektor...")
    explorer = SemanticFileExplorer("synthetic_dataset")
    print(f"[Sistem] Berhasil mengindeks {len(explorer.documents)} dokumen. Kosakata term: {len(explorer.vocab)}")
    
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
