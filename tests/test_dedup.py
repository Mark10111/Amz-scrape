import unittest

from amz_scrape.dedup import merge_products


class DedupTests(unittest.TestCase):
    def test_merge_products(self):
        products = [
            {
                "title": "",
                "price": "100.00",
                "asin": "A1",
                "rating": "4.0",
                "review_count": 10,
                "timestamp": "2026-08-14T09:00+00:00",
            },
            {
                "title": "Real Title",
                "price": "120.00",
                "asin": "A1",
                "rating": "4.2",
                "review_count": 12,
                "timestamp": "2026-08-15T10:00+00:00",
            },
            {
                "title": "Duplicate Day",
                "price": "130.00",
                "asin": "A1",
                "rating": "4.3",
                "review_count": 15,
                "timestamp": "2026-08-15T11:00+00:00",
            },
        ]

        merged = merge_products(products)

        self.assertEqual(len(merged), 1)
        item = merged[0]
        self.assertEqual(item["title"], "Real Title")
        self.assertEqual(item["price"], "100.00;120.00")
        self.assertEqual(item["rating"], "4.2")
        self.assertEqual(item["review_count"], 12)


if __name__ == "__main__":
    unittest.main()
