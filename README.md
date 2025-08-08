# SEC Filings QA Agent

This project is an intelligent Question Answering (QA) system designed to extract and answer financial questions from real-time SEC filings like 10-K, 10-Q, DEF 14A, and Forms 3/4/5. It supports dynamic data retrieval and allows users to query financial entities (e.g., "What was Apple's revenue in 2022?") using ticker symbols like AAPL, MSFT, GOOGL, etc.

## 📌 Features

- ✅ **Dynamic SEC Scraping** of filings from [sec.gov](https://www.sec.gov)
- ✅ **Year-based Filtering** from user queries (e.g., 2022, 2023)
- ✅ **Context Extraction** from HTML filings
- ✅ **Question Answering** using HuggingFace Transformers
- ✅ **Multi-Ticker Support** (e.g., MSFT, AAPL)
- ✅ **Model: RoBERTa Base (SQuAD2 fine-tuned)** for QA
- ✅ **CLI Interface** for interactive usage



```bash
sec-filings-qa-agent/
│
├── run_qa.py              
├── requirements.txt        
├── README.md               
├── src/
│   ├── qa_engine.py        
│   └── sec_retriever.py  

