# src/sec_retriever.py
import re
import requests
from bs4 import BeautifulSoup
import time

HEADERS = {
    "User-Agent": "Sahaj Arora saprojects24@gmail.com"
}

CIK_CACHE = {}

def get_cik_mapping():
    if CIK_CACHE:
        return CIK_CACHE
    url = "https://www.sec.gov/files/company_tickers.json"
    res = requests.get(url, headers=HEADERS)
    if res.status_code != 200:
        raise Exception(f"Failed to fetch CIK mapping: {res.status_code}")
    data = res.json()
    mapping = {entry["ticker"].upper(): str(entry["cik_str"]).zfill(10) for entry in data.values()}
    CIK_CACHE.update(mapping)
    return mapping

def get_company_cik(ticker):
    url = "https://www.sec.gov/files/company_tickers.json"
    res = requests.get(url, headers=HEADERS)
    data = res.json()
    for _, info in data.items():
        if info["ticker"].upper() == ticker.upper():
            return str(info["cik_str"]).zfill(10)
    return None


def get_latest_filing_url(cik, form_type="10-K", year=None):
    base_url = f"https://data.sec.gov/submissions/CIK{cik}.json"
    res = requests.get(base_url, headers=HEADERS)
    if res.status_code != 200:
        raise Exception(f"Failed to get submissions for CIK {cik}")
    data = res.json()
    filings = data.get("filings", {}).get("recent", {})
    for i, form in enumerate(filings.get("form", [])):
        if form == form_type:
            filing_date = filings["filingDate"][i]
            if year and not filing_date.startswith(str(year)):
                continue
            accession = filings["accessionNumber"][i].replace("-", "")
            return f"https://www.sec.gov/Archives/edgar/data/{int(cik)}/{accession}/index.json"
    return None

def get_filing_html_text(url):
    res = requests.get(url, headers=HEADERS)
    if res.status_code != 200:
        return ""
    data = res.json()
    for file in data["directory"]["item"]:
        name = file["name"]
        if name.endswith(".htm") or name.endswith(".html"):
            html_url = url.replace("index.json", name)
            time.sleep(0.5)
            html_res = requests.get(html_url, headers=HEADERS)
            if html_res.status_code == 200:
                soup = BeautifulSoup(html_res.text, "html.parser")
                return soup.get_text()
    return ""

def get_context_from_sec(tickers: list, year=None):
    full_context = ""
    source_links = []
    for ticker in tickers:
        try:
            cik = get_company_cik(ticker)
            if not cik:
                raise ValueError(f"CIK not found for ticker: {ticker}")
            filing_url = get_latest_filing_url(cik, "10-K", year)
            if not filing_url:
                print(f"⚠️ No matching 10-K found for {ticker} in year {year}")
                continue
            text = get_filing_html_text(filing_url)
            if text:
                full_context += f"\n\n--- {ticker} Filing ---\n\n" + text[:10000]  # Truncate to 10K chars
                source_links.append(filing_url.replace("index.json", ""))
        except Exception as e:
            print(f"Error fetching for {ticker}: {str(e)}")
    return full_context.strip(), source_links


def extract_year_from_question(question: str):
    match = re.search(r"\b(20[0-2][0-9])\b", question)
    if match:
        return match.group(1)
    return None
