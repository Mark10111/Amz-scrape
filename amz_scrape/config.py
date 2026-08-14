import argparse
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


DEFAULT_SEARCH_URLS = [
    "https://www.amazon.com/s?k=xiaomi&ref=nb_sb_noss_1",
    "https://www.amazon.com/s?k=iphone+14+pro&i=computers&__mk_it_IT=%C3%85M%C3%85%C5%BD%C3%95%C3%91&crid=E7GZISO0AAIT&sprefix=laptop%2Ccomputers%2C294&ref=nb_sb_noss_1",
    "https://www.amazon.com/s?k=macbook&i=computers&__mk_it_IT=%C3%85M%C3%85%C5%BD%C3%95%C3%91&crid=E7GZISO0AAIT&sprefix=laptop%2Ccomputers%2C294&ref=nb_sb_noss_1",
    "https://www.amazon.com/s?k=snapdragon+gen+1&i=computers&__mk_it_IT=%C3%85M%C3%85%C5%BD%C3%95%C3%91&crid=E7GZISO0AAIT&sprefix=laptop%2Ccomputers%2C294&ref=nb_sb_noss_1",
    "https://www.amazon.com/s?k=low+profile+keyboard&i=computers&__mk_it_IT=%C3%85M%C3%85%C5%BD%C3%95%C3%91&crid=E7GZISO0AAIT&sprefix=laptop%2Ccomputers%2C294&ref=nb_sb_noss_1",
]


@dataclass(slots=True)
class ScraperConfig:
    search_urls: list[str]
    max_pages_per_search: int = 35
    max_request_retries: int = 5
    request_timeout_seconds: int = 20
    min_delay_seconds: float = 1.0
    max_delay_seconds: float = 2.0
    backoff_multiplier: float = 2.0
    output_json: str = "products3.json"
    sqlite_db_path: str = "products.db"
    user_agent_fallback: str = "Mozilla/5.0"


def _merge(base: dict[str, Any], overrides: dict[str, Any]) -> dict[str, Any]:
    merged = base.copy()
    for key, value in overrides.items():
        if value is not None:
            merged[key] = value
    return merged


def _to_config(data: dict[str, Any]) -> ScraperConfig:
    urls = data.get("search_urls") or []
    if not isinstance(urls, list) or not urls:
        raise ValueError("search_urls must be a non-empty list")
    return ScraperConfig(
        search_urls=urls,
        max_pages_per_search=int(data.get("max_pages_per_search", 35)),
        max_request_retries=int(data.get("max_request_retries", 5)),
        request_timeout_seconds=int(data.get("request_timeout_seconds", 20)),
        min_delay_seconds=float(data.get("min_delay_seconds", 1.0)),
        max_delay_seconds=float(data.get("max_delay_seconds", 2.0)),
        backoff_multiplier=float(data.get("backoff_multiplier", 2.0)),
        output_json=str(data.get("output_json", "products3.json")),
        sqlite_db_path=str(data.get("sqlite_db_path", "products.db")),
        user_agent_fallback=str(data.get("user_agent_fallback", "Mozilla/5.0")),
    )


def load_config(config_path: str | None = None, cli_overrides: dict[str, Any] | None = None) -> ScraperConfig:
    defaults = ScraperConfig(search_urls=DEFAULT_SEARCH_URLS)
    payload: dict[str, Any] = {
        "search_urls": defaults.search_urls,
        "max_pages_per_search": defaults.max_pages_per_search,
        "max_request_retries": defaults.max_request_retries,
        "request_timeout_seconds": defaults.request_timeout_seconds,
        "min_delay_seconds": defaults.min_delay_seconds,
        "max_delay_seconds": defaults.max_delay_seconds,
        "backoff_multiplier": defaults.backoff_multiplier,
        "output_json": defaults.output_json,
        "sqlite_db_path": defaults.sqlite_db_path,
        "user_agent_fallback": defaults.user_agent_fallback,
    }

    if config_path:
        config_file = Path(config_path)
        with config_file.open("r", encoding="utf-8") as fh:
            file_data = json.load(fh)
        payload = _merge(payload, file_data)

    if cli_overrides:
        payload = _merge(payload, cli_overrides)

    config = _to_config(payload)
    if config.min_delay_seconds < 0 or config.max_delay_seconds < 0:
        raise ValueError("Delay values must be non-negative")
    if config.max_delay_seconds < config.min_delay_seconds:
        raise ValueError("max_delay_seconds must be >= min_delay_seconds")
    return config


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Amazon scraper")
    parser.add_argument("--config", dest="config", default="scraper_config.json", help="Path to JSON config file")
    parser.add_argument("--urls", nargs="+", help="Override search URLs")
    parser.add_argument("--max-pages", type=int, help="Maximum pages per search URL")
    parser.add_argument("--max-retries", type=int, help="Maximum request retries")
    parser.add_argument("--timeout", type=int, help="Request timeout seconds")
    parser.add_argument("--min-delay", type=float, help="Minimum delay between requests")
    parser.add_argument("--max-delay", type=float, help="Maximum delay between requests")
    parser.add_argument("--backoff", type=float, help="Backoff multiplier")
    parser.add_argument("--output-json", help="Output JSON path")
    parser.add_argument("--sqlite-db", help="SQLite database path")
    parser.add_argument("--log-level", default="INFO", help="Logging level")
    return parser.parse_args()


def cli_overrides_from_args(args: argparse.Namespace) -> dict[str, Any]:
    return {
        "search_urls": args.urls,
        "max_pages_per_search": args.max_pages,
        "max_request_retries": args.max_retries,
        "request_timeout_seconds": args.timeout,
        "min_delay_seconds": args.min_delay,
        "max_delay_seconds": args.max_delay,
        "backoff_multiplier": args.backoff,
        "output_json": args.output_json,
        "sqlite_db_path": args.sqlite_db,
    }
