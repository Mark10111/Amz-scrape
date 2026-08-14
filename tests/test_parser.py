import unittest
from datetime import datetime, timezone

from bs4 import BeautifulSoup

from amz_scrape.parser import (
    normalize_price,
    normalize_rating,
    normalize_review_count,
    parse_search_results,
)


class ParserTests(unittest.TestCase):
    def test_normalize_price(self):
        self.assertEqual(normalize_price("$1,234.50"), "1234.50")
        self.assertEqual(normalize_price("EUR 1.234,99"), "1234.99")
        self.assertEqual(normalize_price(None), "")

    def test_normalize_rating_and_reviews(self):
        self.assertEqual(normalize_rating("4,6 su 5 stelle"), "4.6")
        self.assertEqual(normalize_rating(""), "")
        self.assertEqual(normalize_review_count("1,234"), 1234)

    def test_parse_search_results(self):
        html = """
        <html><body>
        <div class="s-result-item" data-asin="ABC123">
          <span class="a-size-base-plus a-color-base a-text-normal">Phone</span>
          <span class="a-offscreen">$699.00</span>
          <span class="a-icon-alt">4.5 out of 5 stars</span>
          <span class="a-size-base s-underline-text">2,340</span>
        </div>
        <div class="s-result-item" data-asin=""></div>
        </body></html>
        """
        soup = BeautifulSoup(html, "lxml")
        now = datetime(2026, 8, 14, 9, 0, tzinfo=timezone.utc)

        products = parse_search_results(soup, now_utc=now)

        self.assertEqual(len(products), 1)
        self.assertEqual(products[0]["asin"], "ABC123")
        self.assertEqual(products[0]["title"], "Phone")
        self.assertEqual(products[0]["price"], "699.00")
        self.assertEqual(products[0]["rating"], "4.5")
        self.assertEqual(products[0]["review_count"], 2340)


if __name__ == "__main__":
    unittest.main()
