# src/test_retriever.py
from src.retriever import SECQARetriever

retriever = SECQARetriever()

query = "Apple's risk factors in 2023"
results = retriever.search(query)

for i, res in enumerate(results, 1):
    print(f"\n--- Result {i} ---")
    print("Ticker:", res["ticker"])
    print("Date:", res["date"])
    print("Section:", res["section_title"])
    print("Text:\n", res["text"][:800], "...")

