# src/embed_and_store.py

import os
import json
from tqdm import tqdm
from sentence_transformers import SentenceTransformer
import faiss
import numpy as np

model = SentenceTransformer("all-MiniLM-L6-v2")

DATA_DIR = "data/parsed_filings"
VECTOR_DIR = "data/vector_store"
os.makedirs(VECTOR_DIR, exist_ok=True)

def chunk_text(text, max_tokens=500):
    lines = text.split("\n")
    chunks = []
    chunk = []
    token_count = 0
    for line in lines:
        line = line.strip()
        if not line:
            continue
        tokens = line.split()
        if token_count + len(tokens) > max_tokens:
            chunks.append(" ".join(chunk))
            chunk = tokens
            token_count = len(tokens)
        else:
            chunk.extend(tokens)
            token_count += len(tokens)
    if chunk:
        chunks.append(" ".join(chunk))
    return chunks

corpus = []
metadata = []

for fname in tqdm(os.listdir(DATA_DIR), desc="📁 Reading filings"):
    with open(os.path.join(DATA_DIR, fname), "r", encoding="utf-8") as f:
        for line in f:
            entry = json.loads(line)
            chunks = chunk_text(entry["text"])
            for chunk in chunks:
                corpus.append(chunk)
                metadata.append({
                    "ticker": entry["ticker"],
                    "date": entry["date"],
                    "form_type": entry["form_type"],
                    "accession": entry["accession"]
                })

print(f"🔢 Total chunks: {len(corpus)}")

# Create embeddings
print("🧠 Generating embeddings...")
embeddings = model.encode(corpus, show_progress_bar=True, batch_size=32)
embeddings = np.array(embeddings).astype("float32")

# Build FAISS index
index = faiss.IndexFlatL2(embeddings.shape[1])
index.add(embeddings)

# Save index
faiss.write_index(index, os.path.join(VECTOR_DIR, "sec_index.faiss"))

# Save metadata and chunks
with open(os.path.join(VECTOR_DIR, "metadata.json"), "w", encoding="utf-8") as f:
    json.dump(metadata, f)

with open(os.path.join(VECTOR_DIR, "chunks.json"), "w", encoding="utf-8") as f:
    json.dump(corpus, f)

print("✅ Vector store saved.")
