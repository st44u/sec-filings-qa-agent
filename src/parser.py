# src/parser.py
import os
import requests
from bs4 import BeautifulSoup
from tqdm import tqdm

HEADERS = {
    "User-Agent": "SAHAJARORA (saprojects24@gmail.com)"
}

def download_html(url):
    response = requests.get(url, headers=HEADERS)
    if response.status_code != 200:
        print("Failed to fetch:", url)
        return None
    return response.text

def clean_text(text):
    return ' '.join(text.strip().split())

def extract_sections(html_text):
    soup = BeautifulSoup(html_text, "lxml")
    text = soup.get_text("\n")  # preserve line breaks
    lines = [clean_text(line) for line in text.split("\n") if line.strip()]
    
    sections = []
    current_section = {"title": None, "content": []}

    for line in lines:
        if line.lower().startswith("item"):
            if current_section["title"]:
                sections.append(current_section)
            current_section = {
                "title": line.strip(),
                "content": []
            }
        else:
            current_section["content"].append(line)
    
    if current_section["title"]:
        sections.append(current_section)

    return sections

def parse_and_save_filing(filing_meta, output_dir="parsed"):
    os.makedirs(output_dir, exist_ok=True)
    html = download_html(filing_meta["url"])
    if not html:
        return

    sections = extract_sections(html)
    filename = f"{filing_meta['ticker']}_{filing_meta['type']}_{filing_meta['date']}.json"
    path = os.path.join(output_dir, filename)

    enriched = []
    for sec in sections:
        enriched.append({
            "ticker": filing_meta["ticker"],
            "type": filing_meta["type"],
            "date": filing_meta["date"],
            "section_title": sec["title"],
            "section_text": " ".join(sec["content"])
        })

    with open(path, "w", encoding="utf-8") as f:
        import json
        json.dump(enriched, f, indent=2)
    print(f"[✓] Parsed and saved: {path}")

def parse_multiple_filings(json_file):
    import json
    with open(json_file, "r") as f:
        filings = json.load(f)

    for filing in tqdm(filings):
        parse_and_save_filing(filing)

if __name__ == "__main__":
    parse_multiple_filings("data/AAPL_10-K_edgar.json")
