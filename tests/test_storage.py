import json
import tempfile
import unittest
from pathlib import Path

from amz_scrape.storage import SQLiteStorage


class StorageTests(unittest.TestCase):
    def test_save_fetch_and_export(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = Path(tmpdir) / "products.db"
            output_path = Path(tmpdir) / "products.json"

            storage = SQLiteStorage(str(db_path))
            storage.save_products(
                [
                    {
                        "title": "Product",
                        "price": "10.00",
                        "asin": "A1",
                        "rating": "4.5",
                        "review_count": 100,
                        "timestamp": "2026-08-14T09:00+00:00",
                    }
                ],
                source_url="https://example.com",
            )

            rows = storage.fetch_all_products()
            self.assertEqual(len(rows), 1)
            self.assertEqual(rows[0]["asin"], "A1")

            exported = storage.export_json(str(output_path), deduplicate=True)
            self.assertEqual(len(exported), 1)

            with output_path.open("r", encoding="utf-8") as fh:
                payload = json.load(fh)
            self.assertEqual(payload[0]["asin"], "A1")

            storage.close()


if __name__ == "__main__":
    unittest.main()
