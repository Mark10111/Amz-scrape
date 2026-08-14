"""Amazon scraper package."""

from .config import ScraperConfig, load_config, parse_args
from .dedup import merge_products
from .scraper import Scraper, ScrapeSummary
from .storage import SQLiteStorage

__all__ = [
    "ScraperConfig",
    "load_config",
    "parse_args",
    "merge_products",
    "Scraper",
    "ScrapeSummary",
    "SQLiteStorage",
]
