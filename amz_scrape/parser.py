import re
from datetime import datetime, timezone
from decimal import Decimal, InvalidOperation
from typing import Any
from urllib.parse import urljoin

from bs4 import BeautifulSoup
from bs4.element import Tag


def normalize_price(price_text: str | None) -> str:
    if not price_text:
        return ""
    cleaned = re.sub(r"[^\d.,]", "", price_text.strip())
    if not cleaned:
        return ""

    if "," in cleaned and "." in cleaned:
        if cleaned.rfind(",") > cleaned.rfind("."):
            cleaned = cleaned.replace(".", "").replace(",", ".")
        else:
            cleaned = cleaned.replace(",", "")
    elif "," in cleaned:
        cleaned = cleaned.replace(".", "").replace(",", ".")

    try:
        value = Decimal(cleaned)
    except InvalidOperation:
        return ""

    return str(value.quantize(Decimal("0.01")))


def normalize_rating(rating_text: str | None) -> str:
    if not rating_text:
        return ""
    first_token = rating_text.strip().split()[0].replace(",", ".")
    try:
        value = Decimal(first_token)
    except InvalidOperation:
        return ""
    return str(value.quantize(Decimal("0.1")))


def normalize_review_count(review_text: str | None) -> int:
    if not review_text:
        return 0
    digits = re.sub(r"[^\d]", "", review_text)
    return int(digits) if digits else 0


def normalize_product(raw: dict[str, Any]) -> dict[str, Any] | None:
    asin = (raw.get("asin") or "").strip()
    if not asin:
        return None

    title = (raw.get("title") or "").strip()
    timestamp = raw.get("timestamp") or datetime.now(timezone.utc).isoformat(timespec="minutes")
    price = normalize_price(raw.get("price"))
    rating = normalize_rating(raw.get("rating"))
    review_count = normalize_review_count(raw.get("review_count"))

    return {
        "title": title,
        "price": price,
        "asin": asin,
        "rating": rating,
        "review_count": review_count,
        "timestamp": timestamp,
    }


def parse_result_item(result: Tag, timestamp: str) -> dict[str, Any] | None:
    raw_product = {
        "asin": result.get("data-asin", ""),
        "title": "",
        "price": "",
        "rating": "",
        "review_count": "",
        "timestamp": timestamp,
    }

    title_element = result.find("span", {"class": "a-size-base-plus a-color-base a-text-normal"})
    if title_element:
        raw_product["title"] = title_element.get_text(strip=True)

    price_element = result.find("span", class_="a-offscreen")
    if price_element:
        raw_product["price"] = price_element.get_text(strip=True)

    rating_element = result.find("span", class_="a-icon-alt")
    if rating_element:
        raw_product["rating"] = rating_element.get_text(strip=True)

    review_count_element = result.find("span", class_="a-size-base s-underline-text")
    if review_count_element:
        raw_product["review_count"] = review_count_element.get_text(strip=True)

    return normalize_product(raw_product)


def parse_search_results(soup: BeautifulSoup, now_utc: datetime | None = None) -> list[dict[str, Any]]:
    timestamp = (now_utc or datetime.now(timezone.utc)).isoformat(timespec="minutes")
    products: list[dict[str, Any]] = []
    for result in soup.find_all("div", class_="s-result-item"):
        product = parse_result_item(result, timestamp)
        if product is not None:
            products.append(product)
    return products


def get_next_page(soup: BeautifulSoup, base_url: str = "https://www.amazon.com") -> tuple[int | None, str]:
    pagination_element = soup.find(
        "span",
        class_="s-pagination-item s-pagination-disabled",
        string=lambda text: bool(text and text.isdigit()),
    )

    page_number = int(pagination_element.get_text(strip=True)) if pagination_element else None

    next_page_element = soup.find(
        "a",
        class_="s-pagination-item s-pagination-next s-pagination-button s-pagination-separator",
    )
    if not next_page_element:
        return page_number, ""

    href = next_page_element.get("href") or ""
    return page_number, urljoin(base_url, href)


def is_blocked_or_captcha_page(text: str) -> bool:
    lowered = text.lower()
    signals = [
        "captcha",
        "type the characters you see",
        "sorry, we just need to make sure you're not a robot",
        "enter the characters you see below",
        "automated access",
    ]
    return any(signal in lowered for signal in signals)
