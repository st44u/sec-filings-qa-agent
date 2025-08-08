# src/test_qa.py
from src.qa_engine import generate_answer

query = "What were the main risk factors for Apple in 2023?"
answer, citations = generate_answer(query)

print("\n💡 Answer:\n", answer)
print("\n🔎 Sources:")
for c in citations:
    print("-", c)
