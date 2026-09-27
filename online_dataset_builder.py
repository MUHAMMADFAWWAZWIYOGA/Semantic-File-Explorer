import os
import json
import re
import random
from sklearn.datasets import fetch_20newsgroups

DATASET_DIR = "real_world_dataset"
GROUND_TRUTH_FILE = "real_ground_truth.json"

def clean_filename(title):
    # Remove any non-alphanumeric character (except spaces) for absolute Windows safety
    clean = re.sub(r'[^a-zA-Z0-9 ]', "", title)
    return clean[:50].strip().replace(" ", "_")

def build_dataset():
    print("[1/3] Mengunduh dataset nyata secara online (20 Newsgroups subset)...")
    # Fetch a subset of categories to keep it manageable but realistic (e.g., Space, Graphics, Med)
    categories = ['sci.space', 'comp.graphics', 'sci.med', 'talk.politics.mideast']
    newsgroups = fetch_20newsgroups(subset='train', categories=categories, remove=('headers', 'footers', 'quotes'))
    
    if not os.path.exists(DATASET_DIR):
        os.makedirs(DATASET_DIR)
        
    print(f"[2/3] Membangun struktur direktori lokal untuk {len(newsgroups.data)} dokumen...")
    
    ground_truths = []
    
    for i, (text, category_id) in enumerate(zip(newsgroups.data, newsgroups.target)):
        # Limit to 500 documents for this benchmark to save processing time during demo
        if i >= 500:
            break
            
        category_name = newsgroups.target_names[category_id]
        folder_path = os.path.join(DATASET_DIR, category_name)
        
        if not os.path.exists(folder_path):
            os.makedirs(folder_path)
            
        if len(text.strip()) < 50:
            continue # Skip very short files
            
        # Extract a pseudo-title from the first few words to use as filename
        words = text.split()
        title = " ".join(words[:5])
        filename = clean_filename(title) + f"_{i}.txt"
        file_path = os.path.join(folder_path, filename)
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(text)
            
        # Create a few ground truth queries randomly (e.g., 20 test queries)
        if len(ground_truths) < 20 and len(words) > 50:
            # Pick a random 5-7 word sentence from the middle of the document as the user's "remembered context"
            start_idx = random.randint(10, len(words) - 20)
            query = " ".join(words[start_idx:start_idx+6])
            
            # Clean query
            query = re.sub(r'[^a-zA-Z0-9\s]', '', query).lower()
            
            ground_truths.append({
                "query": query,
                "expected_path": os.path.join(category_name, filename).replace("\\", "/")
            })
            
    with open(GROUND_TRUTH_FILE, 'w', encoding='utf-8') as f:
        json.dump(ground_truths, f, indent=4)
        
    print(f"[3/3] Selesai! Dataset berhasil diunduh dan dipetakan ke lokal (Total: {i} files).")
    print(f"Ground truth queries dibuat sebanyak: {len(ground_truths)}")

if __name__ == "__main__":
    build_dataset()
