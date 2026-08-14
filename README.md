# Amazon Product Scraper

A configurable Python scraper for collecting product listings from Amazon search result pages, normalizing product data, and exporting deduplicated output.

## Features

- Config-driven scraping with optional CLI overrides
- Retry handling with randomized delays and exponential backoff
- Captcha/block-page signal detection
- Product normalization (price, rating, review count, timestamp)
- SQLite persistence for raw collected records
- Deduplicated JSON export by ASIN with merged history

## Project Structure

```text
.
├── product_grabber_main.py      # Main entrypoint
├── scraper_config.json          # Runtime configuration
├── duplicate_remover_title.py   # Standalone JSON dedup utility
├── amz_scrape/
│   ├── config.py                # Config loading and CLI parsing
│   ├── scraper.py               # Scraping loop and request handling
│   ├── parser.py                # HTML parsing and normalization
│   ├── storage.py               # SQLite storage and JSON export
│   └── dedup.py                 # Deduplication / merge logic
└── tests/                       # Unit tests
```

## Requirements

- Python 3.10+
- Pip

Install dependencies:

```bash
pip install -r requirements.txt
```

## Quick Start

Run with default config:

```bash
python product_grabber_main.py
```

Run with a custom config:

```bash
python product_grabber_main.py --config scraper_config.json
```

Override selected values from CLI:

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

`scraper_config.json` supports:

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

## Output

The scraper stores raw rows in SQLite and writes deduplicated JSON records in this shape:

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

## Testing

```bash
python -m unittest discover -s tests -p "test_*.py"
```

## Responsible Use

- Respect Amazon terms, robots policies, and applicable laws.
- Use conservative request pacing to reduce load and block risk.
- Expect selector updates when Amazon markup changes.
