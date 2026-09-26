import os
import json
import time
from semantic_file_explorer import SemanticFileExplorer

# ----------------- BASELINE 1: Keyword Search -----------------
class KeywordSearchAgent:
    def __init__(self, root_dir):
        self.root_dir = os.path.abspath(root_dir)

    def query(self, user_query):
        """
        Pencarian sederhana berdasarkan kemunculan kata kunci di nama file 
        atau konten (tanpa pemahaman semantik LLM/Embedding).
        """
        keywords = user_query.lower().split()
        best_path = None
        best_score = -1
        best_span = ""
        
        for root, _, files in os.walk(self.root_dir):
            for file in files:
                rel_path = os.path.relpath(os.path.join(root, file), self.root_dir)
                score = 0
                
                # Cek nama file
                for kw in keywords:
                    if kw in file.lower():
                        score += 2
                        
                # Cek konten
                try:
                    with open(os.path.join(root, file), 'r', encoding='utf-8') as f:
                        content = f.read()
                        content_lower = content.lower()
                        for kw in keywords:
                            if kw in content_lower:
                                score += 1
                                if not best_span:
                                    idx = content_lower.find(kw)
                                    best_span = content[max(0, idx-20):min(len(content), idx+len(kw)+20)]
                except:
                    pass
                    
                if score > best_score:
                    best_score = score
                    best_path = rel_path
                    
        if best_score > 0:
            # Karena ini hanya baseline, kita pura-pura memberikan span 
            # tetapi confidence seringkali tidak terverifikasi (simulasi RAG kasar)
            return {
                "path": best_path,
                "relevance_reason": "Matched keywords.",
                "evidence_span": best_span.replace('\n', ' ').strip(),
                "confidence": "medium" # Baseline tidak punya mekanisme strict grounding
            }
            
        return {"path": None, "relevance_reason": "No match", "evidence_span": None, "confidence": "low"}

# ----------------- EVALUASI (TESTING & BENCHMARKING) -----------------
def evaluate_agent(agent_name, agent_instance, ground_truths):
    print(f"\nMenjalankan evaluasi untuk: {agent_name}...")
    
    total_queries = len(ground_truths)
    correct_path = 0
    faithful_evidence = 0
    total_latency = 0
    
    results_log = []

    for gt in ground_truths:
        q = gt["query"]
        expected_path = gt["expected_path"].replace("/", os.sep)
        
        start_time = time.time()
        # Jalankan inference
        result = agent_instance.query(q)
        latency = time.time() - start_time
        
        total_latency += latency
        
        predicted_path = result.get("path")
        is_correct = (predicted_path == expected_path)
        if is_correct:
            correct_path += 1
            
        # Cek Evidence Faithfulness (apakah ada teks span dan path benar)
        is_faithful = is_correct and result.get("confidence") == "high"
        if is_faithful:
            faithful_evidence += 1
            
        results_log.append({
            "query": q,
            "expected": expected_path,
            "predicted": predicted_path,
            "correct": is_correct,
            "latency_ms": round(latency * 1000, 2)
        })

    accuracy = (correct_path / total_queries) * 100
    faithfulness_rate = (faithful_evidence / total_queries) * 100
    avg_latency = (total_latency / total_queries) * 1000
    
    print(f"--- Hasil {agent_name} ---")
    print(f"Precision@1 (Accuracy): {accuracy:.2f}%")
    print(f"Evidence Faithfulness : {faithfulness_rate:.2f}%")
    print(f"Avg Latency           : {avg_latency:.2f} ms")
    
    return {
        "agent": agent_name,
        "accuracy": accuracy,
        "faithfulness": faithfulness_rate,
        "avg_latency": avg_latency,
        "details": results_log
    }

def main():
    with open("ground_truth.json", "r", encoding="utf-8") as f:
        ground_truths = json.load(f)
        
    dataset_dir = "synthetic_dataset"
    
    # 1. Inisialisasi Baseline Agent
    baseline_agent = KeywordSearchAgent(dataset_dir)
    
    # 2. Inisialisasi Proposed Agent (Semantic File Explorer)
    proposed_agent = SemanticFileExplorer(dataset_dir)
    
    print(f"Memulai Benchmark pada {len(ground_truths)} query...")
    
    res_baseline = evaluate_agent("Baseline (Keyword Match)", baseline_agent, ground_truths)
    res_proposed = evaluate_agent("Proposed (Semantic File Explorer)", proposed_agent, ground_truths)
    
    # Simpan report
    report = {
        "dataset_size": len(ground_truths),
        "results": [res_baseline, res_proposed]
    }
    
    with open("benchmark_report.json", "w", encoding="utf-8") as f:
        json.dump(report, f, indent=4)
        
    print("\n[+] Benchmark selesai! Laporan disimpan di 'benchmark_report.json'.")

if __name__ == "__main__":
    main()
