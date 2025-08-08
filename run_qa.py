# run_qa.py

from src.qa_engine import generate_answer

query = input("Ask your SEC question: ")
tickers_input = input("Enter tickers separated by comma (default AAPL,MSFT): ").strip()
tickers = tickers_input.split(",") if tickers_input else ["AAPL", "MSFT"]

answer, sources = generate_answer(query, tickers)

print("\n💡 Answer:\n", answer)
print("\n🔎 Sources:")
for src in sources:
    print("-", src)
