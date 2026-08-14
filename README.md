# 📦 Amazon Web Scraper

## Overview

This project scrapes product data from Amazon search result pages with configurable runtime options, retry/backoff handling, and SQLite-backed persistence.

The scraper now:
- Reads inputs from `scraper_config.json` and/or CLI args.
- Detects common captcha/blocked responses.
- Normalizes product data before storage.
- Stores raw records in SQLite (`products.db`) and exports deduplicated JSON (`products3.json`).

## Project Structure

- `/product_grabber_main.py` - entrypoint.
- `/scraper_config.json` - default runtime configuration.
- `/amz_scrape/config.py` - config loading + CLI overrides.
- `/amz_scrape/scraper.py` - request/retry/rate-limit scrape loop.
- `/amz_scrape/parser.py` - parsing and normalization.
- `/amz_scrape/storage.py` - SQLite persistence and JSON export.
- `/amz_scrape/dedup.py` - dedup/merge logic.
- `/duplicate_remover_title.py` - standalone JSON dedup utility.
- `/tests/` - unit tests.

## Installation

```bash
pip3 install -r /home/runner/work/Amz-scrape/Amz-scrape/requirements.txt
```

## Usage

### Run with default config

```bash
python3 /home/runner/work/Amz-scrape/Amz-scrape/product_grabber_main.py
```

### Run with a custom config file

```bash
python3 /home/runner/work/Amz-scrape/Amz-scrape/product_grabber_main.py --config /home/runner/work/Amz-scrape/Amz-scrape/scraper_config.json
```

### Override selected settings from CLI

```bash
python3 /home/runner/work/Amz-scrape/Amz-scrape/product_grabber_main.py \
  --max-pages 10 \
  --max-retries 4 \
  --min-delay 1.5 \
  --max-delay 3.0 \
  --sqlite-db /home/runner/work/Amz-scrape/Amz-scrape/products.db \
  --output-json /home/runner/work/Amz-scrape/Amz-scrape/products3.json
```

## Configuration Fields (`scraper_config.json`)

- `search_urls` (list[str])
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

Each exported JSON record uses this schema:

```json
{
  "title": "string",
  "price": "string decimal or ';'-joined price history",
  "asin": "string",
  "rating": "string decimal",
  "review_count": 0,
  "timestamp": "ISO timestamp or ';'-joined timestamp history"
}
```

## Observability

Structured logs include:
- URL start events.
- request/network failure warnings.
- captcha/block warnings.
- final summary with scraped pages, failed/skipped pages, and item counts.

## Testing

Run unit tests:

```bash
python3 -m unittest discover -s /home/runner/work/Amz-scrape/Amz-scrape/tests -p "test_*.py"
```

## Limitations and Risks

- Amazon page markup changes can break selectors.
- Automated scraping may trigger captchas or temporary blocks.
- Use respectful request pacing and comply with target site policies and legal requirements.
- Historical `price` and `timestamp` are merged as semicolon-delimited strings for compatibility.
