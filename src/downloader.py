# src/downloader.py
import os, json
import requests
from bs4 import BeautifulSoup
from utils import get_cik_from_ticker

BASE_URL = "https://data.sec.gov"
HEADERS = {"User-Agent": "sec-filing-qa-script"}

def download_filings_edgar(ticker, filing_type="10-K", limit=3):
    cik = get_cik_from_ticker(ticker)
    url = f"https://data.sec.gov/submissions/CIK{cik}.json"
    
    response = requests.get(url, headers=HEADERS)
    if response.status_code != 200:
        print("Error fetching filings list.")
        return []

    data = response.json()
    filings = data.get("filings", {}).get("recent", {})
    
    results = []
    for i in range(len(filings["form"])):
        if filings["form"][i] != filing_type:
            continue
        if len(results) >= limit:
            break
        accession = filings["accessionNumber"][i].replace("-", "")
        filing_date = filings["filingDate"][i]
        doc_url = f"https://www.sec.gov/Archives/edgar/data/{int(cik)}/{accession}/{filings['primaryDocument'][i]}"
        results.append({
            "ticker": ticker,
            "type": filing_type,
            "date": filing_date,
            "url": doc_url
        })
    
    os.makedirs("data", exist_ok=True)
    with open(f"data/{ticker}_{filing_type}_edgar.json", "w") as f:
        json.dump(results, f, indent=2)

    print(f"[✓] Downloaded metadata for {len(results)} filings for {ticker}")
    return results

if __name__ == "__main__":
    filings = download_filings_edgar("AAPL", "10-K", 3)
    print(json.dumps(filings, indent=2))


