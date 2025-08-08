# src/chunker.py
import os
import json
from tqdm import tqdm
from sentence_transformers import SentenceTransformer
import faiss
import numpy as np

model = SentenceTransformer("all-MiniLM-L6-v2")

def chunk_text(text, max_tokens=100):
    words = text.split()
    chunks = []
    for i in range(0, len(words), max_tokens):
        chunk = " ".join(words[i:i+max_tokens])
        if chunk:
            chunks.append(chunk)
    return chunks

def build_index(parsed_dir="parsed", index_dir="index"):
    os.makedirs(index_dir, exist_ok=True)
    all_chunks = []
    metadata = []

    print("[*] Loading and chunking parsed filings...")
    for file in tqdm(os.listdir(parsed_dir)):
        if not file.endswith(".json"):
            continue
        path = os.path.join(parsed_dir, file)
        with open(path, "r", encoding="utf-8") as f:
            sections = json.load(f)
        for section in sections:
            chunks = chunk_text(section["section_text"])
            for chunk in chunks:
                all_chunks.append(chunk)
                metadata.append({
                    "ticker": section["ticker"],
                    "type": section["type"],
                    "date": section["date"],
                    "section_title": section["section_title"],
                    "text": chunk
                })

    print(f"[✓] Total chunks: {len(all_chunks)}")
    
    # Embedding
    print("[*] Embedding all chunks...")
    embeddings = model.encode(all_chunks, show_progress_bar=True)
    dim = embeddings.shape[1]

    print("[*] Building FAISS index...")
    index = faiss.IndexFlatL2(dim)
    index.add(np.array(embeddings).astype("float32"))

    # Save index
    faiss.write_index(index, os.path.join(index_dir, "faiss.index"))

    # Save metadata
    with open(os.path.join(index_dir, "metadata.json"), "w") as f:
        json.dump(metadata, f, indent=2)

    print("[✓] Vector index + metadata saved in index/")

if __name__ == "__main__":
    build_index()
