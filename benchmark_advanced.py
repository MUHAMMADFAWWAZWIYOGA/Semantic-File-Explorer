import os
import json
import time
from semantic_file_explorer_advanced import SemanticFileExplorerAdvanced

# Baseline: Keyword Search
class KeywordSearchAgent:
    def __init__(self, root_dir):
        self.root_dir = os.path.abspath(root_dir)

    def query(self, user_query):
        keywords = user_query.lower().split()
        best_path = None
        best_score = -1
        best_span = ""
        
        for root, _, files in os.walk(self.root_dir):
            for file in files:
                rel_path = os.path.relpath(os.path.join(root, file), self.root_dir).replace("\\", "/")
                score = 0
                
                try:
                    with open(os.path.join(root, file), 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read()
                        content_lower = content.lower()
                        for kw in keywords:
                            if kw in content_lower:
                                score += 1
                                if not best_span:
                                    idx = content_lower.find(kw)
                                    best_span = content[max(0, idx-20):min(len(content), idx+50)]
                except:
                    pass
                    
                if score > best_score:
                    best_score = score
                    best_path = rel_path
                    
        if best_score > 0:
            return {
                "path": best_path,
                "evidence_span": best_span.replace('\n', ' ').strip(),
                "confidence": "medium"
            }
            
        return {"path": None, "evidence_span": None, "confidence": "low"}

def evaluate_agent(agent_name, agent_instance, ground_truths):
    print(f"\nMenjalankan Evaluasi: {agent_name}...")
    
    total_queries = len(ground_truths)
    correct_path = 0
    faithful_evidence = 0
    total_latency = 0
    
    for gt in ground_truths:
        q = gt["query"]
        expected_path = gt["expected_path"]
        
        start_time = time.time()
        result = agent_instance.query(q)
        latency = time.time() - start_time
        
        total_latency += latency
        predicted_path = result.get("path")
        
        is_correct = (predicted_path == expected_path)
        if is_correct:
            correct_path += 1
            
        is_faithful = is_correct and result.get("confidence") == "high"
        if is_faithful:
            faithful_evidence += 1

    accuracy = (correct_path / total_queries) * 100 if total_queries > 0 else 0
    faithfulness_rate = (faithful_evidence / total_queries) * 100 if total_queries > 0 else 0
    avg_latency = (total_latency / total_queries) * 1000 if total_queries > 0 else 0
    
    print(f"--- Hasil {agent_name} ---")
    print(f"Precision@1 (Accuracy): {accuracy:.2f}%")
    print(f"Evidence Faithfulness : {faithfulness_rate:.2f}%")
    print(f"Avg Latency           : {avg_latency:.2f} ms")

def main():
    with open("real_ground_truth.json", "r", encoding="utf-8") as f:
        ground_truths = json.load(f)
        
    dataset_dir = "real_world_dataset"
    
    baseline = KeywordSearchAgent(dataset_dir)
    proposed = SemanticFileExplorerAdvanced(dataset_dir)
    
    print(f"Memulai Benchmark pada {len(ground_truths)} real-world query...")
    
    evaluate_agent("Baseline (Keyword Match)", baseline, ground_truths)
    evaluate_agent("Proposed (Advanced ML + Chunking RAG)", proposed, ground_truths)

if __name__ == "__main__":
    main()
