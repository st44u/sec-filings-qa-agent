# src/utils.py
import requests

def get_cik_from_ticker(ticker):
    url = "https://www.sec.gov/files/company_tickers.json"
    headers = {
        "User-Agent": "Your Name (your.email@example.com)"
    }
    response = requests.get(url, headers=headers)
    
    if response.status_code != 200:
        raise Exception(f"Failed to fetch ticker list. Status code: {response.status_code}")
    
    data = response.json()
    for entry in data.values():
        if entry['ticker'].lower() == ticker.lower():
            cik = str(entry['cik_str']).zfill(10)
            return cik
    
    raise Exception(f"CIK not found for ticker: {ticker}")

