import os
import json
import re
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
import docx
import csv

class SandboxSafetyError(Exception):
    pass

class SemanticFileExplorerAdvanced:
    def __init__(self, root_dir, index_file="semantic_index_adv.json"):
        self.root_dir = os.path.abspath(root_dir)
        self.index_file = os.path.join(self.root_dir, index_file)
        
        self.chunk_size = 150 # Ukuran potongan (RAG Advanced Chunking)
        
        self.chunks = []      # Menyimpan metadata chunk
        self.corpus = []      # Menyimpan teks chunk
        self.vectorizer = TfidfVectorizer(ngram_range=(1, 2), stop_words='english', sublinear_tf=True)
        self.tfidf_matrix = None
        
        self.build_advanced_index()

    def _is_safe_path(self, path):
        abs_path = os.path.abspath(os.path.join(self.root_dir, path))
        return abs_path.startswith(self.root_dir)

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
                with open(full_path, "r", encoding="utf-8", errors='ignore') as f:
                    reader = csv.reader(f)
                    return "\n".join([", ".join(row) for row in reader])
            else:
                with open(full_path, 'r', encoding='utf-8', errors='ignore') as f:
                    return f.read()
        except Exception as e:
            return {"error": str(e)}

    def chunk_text(self, text):
        """Memecah dokumen besar menjadi potongan kecil (Advanced RAG)"""
        words = text.split()
        chunks = []
        for i in range(0, len(words), self.chunk_size):
            chunk = " ".join(words[i:i+self.chunk_size])
            chunks.append(chunk)
        return chunks

    def build_advanced_index(self):
        """Membangun Indeks dengan Machine Learning (Scikit-Learn) dan Chunking"""
        print("[Sistem] Memulai pemindaian dan Advanced Chunking...")
        
        for root, _, files in os.walk(self.root_dir):
            for file in files:
                if file.endswith(('.txt', '.md', '.py', '.csv', '.docx')):
                    rel_path = os.path.relpath(os.path.join(root, file), self.root_dir).replace("\\", "/")
                    content = self.tool_read_file(rel_path)
                    
                    if isinstance(content, str) and len(content.strip()) > 10:
                        file_chunks = self.chunk_text(content)
                        for chunk_idx, chunk_text in enumerate(file_chunks):
                            self.corpus.append(chunk_text)
                            self.chunks.append({
                                "path": rel_path,
                                "chunk_idx": chunk_idx,
                                "original_content": chunk_text
                            })
                            
        if not self.corpus:
            return
            
        print(f"[Sistem] Mengindeks {len(self.corpus)} chunks dengan Scikit-Learn TfidfVectorizer...")
        self.tfidf_matrix = self.vectorizer.fit_transform(self.corpus)
        print("[Sistem] Indeks Machine Learning Selesai dibangun.")

    def tool_semantic_search(self, query):
        """Pencarian Semantik Tingkat Lanjut dengan Cosine Similarity ML"""
        if self.tfidf_matrix is None or not self.corpus:
            return []
            
        # Transform kueri ke dalam ruang vektor ML
        query_vec = self.vectorizer.transform([query])
        
        # Hitung cosinus secara matriks (Sangat Cepat & Skalabel)
        sim_scores = cosine_similarity(query_vec, self.tfidf_matrix).flatten()
        
        # Ambil Top 5 Chunk teratas
        top_indices = sim_scores.argsort()[-5:][::-1]
        
        results = []
        for idx in top_indices:
            score = sim_scores[idx]
            if score > 0.02: # Threshold sensitivitas
                chunk_meta = self.chunks[idx]
                results.append({
                    "path": chunk_meta["path"],
                    "span": chunk_meta["original_content"],
                    "score": score
                })
        return results

    def post_check_evidence(self, path, evidence_span):
        content = self.tool_read_file(path)
        if isinstance(content, dict) and "error" in content:
            return "low"
            
        # Normalisasi
        clean_span = re.sub(r'\s+', ' ', evidence_span.strip())
        clean_content = re.sub(r'\s+', ' ', content.strip())
        
        if clean_span in clean_content:
            return "high"
        return "low"

    def query(self, user_query):
        search_results = self.tool_semantic_search(user_query)
        
        if not search_results:
            return {
                "path": None,
                "relevance_reason": "Gagal pencarian matriks. Tidak ada chunk relevan.",
                "evidence_span": None,
                "confidence": "low"
            }
            
        best_candidate = search_results[0]
        path = best_candidate["path"]
        
        # Mengekstrak snippet 30 kata terbaik dari chunk
        words = best_candidate["span"].split()
        snippet = " ".join(words[:40]) if len(words) > 40 else best_candidate["span"]
        
        confidence = self.post_check_evidence(path, best_candidate["span"])
        
        return {
            "path": path,
            "relevance_reason": f"Scikit-Learn TF-IDF (N-Grams) Cosine Sim: {best_candidate['score']:.4f}",
            "evidence_span": snippet,
            "confidence": confidence
        }
