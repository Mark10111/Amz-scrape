import random
import time
from dataclasses import dataclass
from typing import Callable

import requests
from bs4 import BeautifulSoup
from fake_useragent import UserAgent

from .config import ScraperConfig
from .logging_utils import LOGGER_NAME
from .parser import get_next_page, is_blocked_or_captcha_page, parse_search_results


@dataclass(slots=True)
class ScrapeSummary:
    total_urls: int = 0
    requested_pages: int = 0
    scraped_pages: int = 0
    failed_requests: int = 0
    blocked_pages: int = 0
    skipped_pages: int = 0
    items_scraped: int = 0


class Scraper:
    def __init__(self, config: ScraperConfig, logger, sleep_func: Callable[[float], None] = time.sleep):
        self.config = config
        self.logger = logger
        self.summary = ScrapeSummary(total_urls=len(config.search_urls))
        self.sleep_func = sleep_func
        self._user_agent = self._build_user_agent()
        self._session = requests.Session()

    def _build_user_agent(self):
        try:
            return UserAgent()
        except Exception:
            return None

    def _next_delay(self, attempt: int) -> float:
        random_delay = random.uniform(self.config.min_delay_seconds, self.config.max_delay_seconds)
        backoff = self.config.backoff_multiplier ** max(0, attempt - 1)
        return random_delay * backoff

    def _request_with_retries(self, url: str) -> BeautifulSoup | None:
        for attempt in range(1, self.config.max_request_retries + 1):
            self.summary.requested_pages += 1
            try:
                user_agent = (
                    self._user_agent.random if self._user_agent else self.config.user_agent_fallback
                )
                headers = {"User-Agent": user_agent}
                response = self._session.get(
                    url,
                    headers=headers,
                    timeout=self.config.request_timeout_seconds,
                )
                html = response.text or ""

                if response.ok and not is_blocked_or_captcha_page(html):
                    return BeautifulSoup(response.content, "lxml")

                if is_blocked_or_captcha_page(html):
                    self.summary.blocked_pages += 1
                    self.logger.warning(
                        "Blocked or captcha page detected",
                        extra={"event": "captcha", "url": url, "attempt": attempt},
                    )
                else:
                    self.logger.warning(
                        "Request failed",
                        extra={
                            "event": "request_failed",
                            "url": url,
                            "status_code": response.status_code,
                            "attempt": attempt,
                        },
                    )
            except requests.RequestException as err:
                self.logger.warning(
                    "Network error",
                    extra={"event": "network_error", "url": url, "attempt": attempt, "error": str(err)},
                )

            self.summary.failed_requests += 1
            delay = self._next_delay(attempt)
            self.sleep_func(delay)

        return None

    def scrape(self) -> list[tuple[str, list[dict]]]:
        scraped_batches: list[tuple[str, list[dict]]] = []

        for search_url in self.config.search_urls:
            self.logger.info("Starting URL", extra={"event": "start_url", "url": search_url})
            soup = self._request_with_retries(search_url)
            if soup is None:
                self.summary.skipped_pages += 1
                continue

            products = parse_search_results(soup)
            self.summary.items_scraped += len(products)
            self.summary.scraped_pages += 1
            scraped_batches.append((search_url, products))

            _, next_page_url = get_next_page(soup)
            page_index = 1
            while page_index < self.config.max_pages_per_search and next_page_url:
                page_soup = self._request_with_retries(next_page_url)
                if page_soup is None:
                    self.summary.skipped_pages += 1
                    break

                page_products = parse_search_results(page_soup)
                self.summary.items_scraped += len(page_products)
                self.summary.scraped_pages += 1
                scraped_batches.append((next_page_url, page_products))

                _, next_page_url = get_next_page(page_soup)
                page_index += 1

            self.sleep_func(random.uniform(self.config.min_delay_seconds, self.config.max_delay_seconds))

        return scraped_batches

    def close(self) -> None:
        self._session.close()
