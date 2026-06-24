# Legal Gazette Bot 2025

An automated Python utility designed to monitor the **Kenya Gazette** for land title changes, legal notices, and property-related mutations. 

## Features
- Scrapes Kenya Law Gazette repository.
- Downloads and parses PDF content in-memory.
- Filters notices using specific keywords (e.g., "Land Registration Act", "Lost Title").
- Maintains a local state to avoid redundant processing.
- Includes a scheduling mechanism for daily checks.

## Installation
1. Ensure you have Python 3.9+ installed.
2. Clone this repository.
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Usage
Run the bot manually:
```bash
python scraper.py
```

The bot will check for new publications daily and output alerts to the console if matching criteria are found.

## Customization
You can modify the `KEYWORDS` list in `scraper.py` to track other legal events such as "Insolvency" or "Succession Cause".