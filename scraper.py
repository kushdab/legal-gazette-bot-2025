import os
import time
import json
import requests
import pdfplumber
import schedule
from bs4 import BeautifulSoup
from datetime import datetime
from io import BytesIO

# Configuration
BASE_URL = "http://kenyalaw.org/kenya_gazette/"
KEYWORDS = ["Land Registration Act", "Title No", "Lost Title", "Notice of Application", "Mutations"]
DATA_FILE = "processed_gazettes.json"

class GazetteBot:
    def __init__(self):
        self.processed_ids = self.load_processed_ids()

    def load_processed_ids(self):
        if os.path.exists(DATA_FILE):
            with open(DATA_FILE, 'r') as f:
                return json.load(f)
        return []

    def save_processed_ids(self):
        with open(DATA_FILE, 'w') as f:
            json.dump(self.processed_ids, f)

    def get_latest_gazettes(self):
        """Scrapes the Kenya Law Gazette page for the most recent PDF links."""
        print(f"[{datetime.now()}] Checking for new gazettes...")
        try:
            response = requests.get(BASE_URL, timeout=30)
            soup = BeautifulSoup(response.content, 'html.parser')
            links = []
            
            # Logic to find PDF links in the table
            for row in soup.select('table tr'):
                pdf_link = row.find('a', href=True)
                if pdf_link and '.pdf' in pdf_link['href']:
                    gazette_id = pdf_link['href'].split('/')[-1]
                    links.append({
                        'url': pdf_link['href'],
                        'id': gazette_id,
                        'title': row.text.strip().split('\n')[0]
                    })
            return links
        except Exception as e:
            print(f"Error fetching gazettes: {e}")
            return []

    def scan_pdf(self, url):
        """Downloads and scans the PDF for land-related keywords."""
        print(f"Scanning: {url}")
        found_matches = []
        try:
            response = requests.get(url, timeout=60)
            with pdfplumber.open(BytesIO(response.content)) as pdf:
                for i, page in enumerate(pdf.pages):
                    text = page.extract_text()
                    if text:
                        for keyword in KEYWORDS:
                            if keyword.lower() in text.lower():
                                found_matches.append({
                                    'page': i + 1,
                                    'keyword': keyword,
                                    'snippet': text[:200].replace('\n', ' ') + "..."
                                })
            return found_matches
        except Exception as e:
            print(f"Error scanning PDF {url}: {e}")
            return []

    def run(self):
        gazettes = self.get_latest_gazettes()
        for gazette in gazettes:
            if gazette['id'] not in self.processed_ids:
                print(f"New Gazette detected: {gazette['title']}")
                matches = self.scan_pdf(gazette['url'])
                
                if matches:
                    self.alert(gazette, matches)
                
                self.processed_ids.append(gazette['id'])
                self.save_processed_ids()
                # Rate limiting
                time.sleep(2)

    def alert(self, gazette, matches):
        """Simple console alert (could be integrated with Email/Telegram)."""
        print("\n--- ALERT: LAND NOTICE DETECTED ---")
        print(f"Source: {gazette['title']}")
        print(f"URL: {gazette['url']}")
        for m in matches:
            print(f"[Page {m['page']}] Keyword: {m['keyword']}")
        print("------------------------------------\n")

if __name__ == "__main__":
    bot = GazetteBot()
    
    # Run once at start
    bot.run()

    # Schedule to run every day at 10:00 AM
    schedule.every().day.at("10:00").do(bot.run)

    print("Bot is active and scheduled.")
    while True:
        schedule.run_pending()
        time.sleep(60)