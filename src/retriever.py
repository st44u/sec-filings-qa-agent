# src/retriever.py
from sentence_transformers import SentenceTransformer
import faiss
import json
import numpy as np

class SECQARetriever:
    def __init__(self, index_path="index/faiss.index", metadata_path="index/metadata.json"):
        self.model = SentenceTransformer("all-MiniLM-L6-v2")
        self.index = faiss.read_index(index_path)
        with open(metadata_path, "r", encoding="utf-8") as f:
            self.metadata = json.load(f)

    def search(self, query, top_k=5):
        query_embedding = self.model.encode([query])
        D, I = self.index.search(np.array(query_embedding).astype("float32"), top_k)

        results = []
        for idx in I[0]:
            if idx < len(self.metadata):
                results.append(self.metadata[idx])
        return results

