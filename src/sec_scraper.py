# src/sec_scraper.py

import os
import json
import time
import requests
from bs4 import BeautifulSoup
from tqdm import tqdm

BASE_URL = "https://www.sec.gov"
HEADERS = {"User-Agent": "Your Name contact@domain.com"}

TICKERS = [
    "AAPL", "MSFT", "GOOGL",
    "JPM", "BAC", "GS",
    "JNJ", "PFE", "UNH",
    "WMT", "TGT", "KO",
    "XOM", "CVX"
]

SAVE_DIR = "data/parsed_filings"
os.makedirs(SAVE_DIR, exist_ok=True)

FORM_TYPES = ["10-K", "10-Q", "DEF 14A", "3", "4", "5"]

def fetch_cik(ticker):
    url = f"https://www.sec.gov/files/company_tickers.json"
    response = requests.get(url, headers=HEADERS)
    cik_map = {v["ticker"]: v["cik_str"] for k, v in response.json().items()}
    return str(cik_map[ticker.upper()]).zfill(10)

def fetch_filings(cik, form_type="10-K", count=3):
    url = f"https://data.sec.gov/submissions/CIK{cik}.json"
    res = requests.get(url, headers=HEADERS)
    data = res.json()
    filings = data["filings"]["recent"]
    documents = []
    for i in range(len(filings["form"])):
        if filings["form"][i].upper() == form_type.upper():
            doc = {
                "accession": filings["accessionNumber"][i].replace("-", ""),
                "date": filings["filingDate"][i],
                "type": form_type
            }
            documents.append(doc)
        if len(documents) >= count:
            break
    return documents

def extract_text_from_filing(cik, accession):
    url = f"https://www.sec.gov/Archives/edgar/data/{int(cik)}/{accession}/index.json"
    res = requests.get(url, headers=HEADERS)
    if res.status_code != 200:
        return None
    files = res.json().get("directory", {}).get("item", [])
    txt_file = next((f for f in files if f["name"].endswith(".htm") or f["name"].endswith(".html")), None)
    if not txt_file:
        return None
    full_url = f"https://www.sec.gov/Archives/edgar/data/{int(cik)}/{accession}/{txt_file['name']}"
    try:
        res = requests.get(full_url, headers=HEADERS)
        soup = BeautifulSoup(res.text, "html.parser")
        text = soup.get_text(separator="\n")
        return text[:100000]  # Truncate to 100k characters
    except:
        return None

def process_and_save(ticker):
    print(f"\n🗂️  Processing {ticker}")
    cik = fetch_cik(ticker)
    all_docs = []
    for form in FORM_TYPES:
        filings = fetch_filings(cik, form_type=form, count=3)
        for f in tqdm(filings, desc=f"{form} filings"):
            raw_text = extract_text_from_filing(cik, f["accession"])
            if raw_text:
                doc = {
                    "ticker": ticker,
                    "date": f["date"],
                    "form_type": f["type"],
                    "accession": f["accession"],
                    "text": raw_text
                }
                all_docs.append(doc)
            time.sleep(0.6)  # Rate limit
    # Save
    save_path = os.path.join(SAVE_DIR, f"{ticker}.jsonl")
    with open(save_path, "w", encoding="utf-8") as f:
        for doc in all_docs:
            f.write(json.dumps(doc) + "\n")
    print(f"✅ Saved {len(all_docs)} filings for {ticker}")

if __name__ == "__main__":
    for ticker in TICKERS:
        process_and_save(ticker)
