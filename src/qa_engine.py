# src/qa_engine.py

import torch
from transformers import pipeline
try:
    from src.sec_retriever import get_context_from_sec, extract_year_from_question
except ImportError:
    from sec_retriever import get_context_from_sec, extract_year_from_question

MODEL_NAME = "deepset/roberta-base-squad2"

try:
    device = 0 if torch.cuda.is_available() else -1
    print(f"Device set to use {'cuda' if device == 0 else 'cpu'}")
    qa_pipeline = pipeline("question-answering", model=MODEL_NAME, tokenizer=MODEL_NAME, device=device)
except Exception as e:
    print(f"❌ Error loading QA pipeline: {e}")
    qa_pipeline = None

def generate_answer(question, tickers=["AAPL", "MSFT"]):
    # Step 1: Extract year from question
    year = extract_year_from_question(question)

    # Step 2: Get SEC context for tickers + year
    result = get_context_from_sec(tickers, year)

    if not result or not isinstance(result, tuple) or not result[0].strip():
        return "❌ Could not fetch SEC filings or extract context for the given tickers.", []

    context, sources = result

    # Step 3: Run QA model
    if qa_pipeline is None:
        return "❌ QA pipeline not loaded. Check model and dependencies.", sources
    try:
        result = qa_pipeline({
            "context": context,
            "question": question
        })
        answer = result["answer"] if isinstance(result, dict) and "answer" in result else str(result)
    except Exception as e:
        return f"❌ Error running QA model: {e}", sources

    return answer.strip(), sources


