# Amazon Product Scraper

A production-minded Python project that collects Amazon search listing data, normalizes noisy web content, and exports clean analytics-ready records.

## Why This Project Matters

This project demonstrates practical software engineering skills often used in real data and backend workflows:

- Building resilient networked applications with retries and backoff
- Parsing unstable HTML structures and normalizing inconsistent input
- Designing a pipeline from ingestion to persistent storage and export
- Writing testable, modular Python code with focused unit tests

## Technical Highlights

- Config-driven scraping with CLI overrides for flexible runs
- Captcha/block detection safeguards in request flow
- Data normalization for price, rating, review count, and timestamp
- SQLite persistence layer for raw collection history
- Deduplicated JSON export by ASIN with merged value history

## Repository Layout

```text
.
├── product_grabber_main.py      # Main entrypoint and pipeline orchestration
├── scraper_config.json          # Runtime configuration
├── duplicate_remover_title.py   # Standalone JSON dedup utility
├── amz_scrape/
│   ├── config.py                # Config loading and CLI parsing
│   ├── scraper.py               # Request/retry logic and scrape loop
│   ├── parser.py                # HTML extraction and normalization
│   ├── storage.py               # SQLite storage and JSON export
│   └── dedup.py                 # Product merge/dedup rules
└── tests/                       # Unit tests
```

## Quick Start

```bash
pip install -r requirements.txt
python product_grabber_main.py
```

Run with custom options:

```bash
python product_grabber_main.py \
  --urls "https://www.amazon.com/s?k=iphone+14+pro" \
  --max-pages 10 \
  --max-retries 4 \
  --timeout 20 \
  --min-delay 1.5 \
  --max-delay 3.0 \
  --backoff 2.0 \
  --sqlite-db products.db \
  --output-json products3.json \
  --log-level INFO
```

## Configuration

Supported `scraper_config.json` fields:

- `search_urls` (list[str], required)
- `max_pages_per_search` (int)
- `max_request_retries` (int)
- `request_timeout_seconds` (int)
- `min_delay_seconds` (float)
- `max_delay_seconds` (float)
- `backoff_multiplier` (float)
- `output_json` (str)
- `sqlite_db_path` (str)
- `user_agent_fallback` (str)

## Output Schema

```json
{
  "title": "string",
  "price": "string decimal or ';'-joined history",
  "asin": "string",
  "rating": "string decimal",
  "review_count": 0,
  "timestamp": "ISO timestamp or ';'-joined history"
}
```

## Validation

```bash
python -m unittest discover -s tests -p "test_*.py"
```

## Responsible Use

- Follow target-site terms and applicable legal requirements.
- Keep request rates conservative to reduce load and block risk.
- Update selectors as page markup evolves.
