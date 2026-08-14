import json
import sqlite3
from pathlib import Path
from typing import Any

from .dedup import merge_products


class SQLiteStorage:
    def __init__(self, db_path: str):
        self.db_path = db_path
        self._conn = sqlite3.connect(db_path)
        self._conn.row_factory = sqlite3.Row
        self._create_schema()

    def _create_schema(self) -> None:
        self._conn.execute(
            """
            CREATE TABLE IF NOT EXISTS products (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                asin TEXT NOT NULL,
                title TEXT NOT NULL,
                price TEXT NOT NULL,
                rating TEXT NOT NULL,
                review_count INTEGER NOT NULL DEFAULT 0,
                timestamp TEXT NOT NULL,
                source_url TEXT NOT NULL
            )
            """
        )
        self._conn.execute(
            "CREATE INDEX IF NOT EXISTS idx_products_asin_timestamp ON products(asin, timestamp)"
        )
        self._conn.commit()

    def save_products(self, products: list[dict[str, Any]], source_url: str) -> None:
        if not products:
            return
        rows = [
            (
                product["asin"],
                product.get("title", ""),
                product.get("price", ""),
                product.get("rating", ""),
                int(product.get("review_count", 0)),
                product.get("timestamp", ""),
                source_url,
            )
            for product in products
        ]
        self._conn.executemany(
            """
            INSERT INTO products(asin, title, price, rating, review_count, timestamp, source_url)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            rows,
        )
        self._conn.commit()

    def fetch_all_products(self) -> list[dict[str, Any]]:
        cursor = self._conn.execute(
            """
            SELECT asin, title, price, rating, review_count, timestamp
            FROM products
            ORDER BY id ASC
            """
        )
        return [dict(row) for row in cursor.fetchall()]

    def export_json(self, output_json_path: str, deduplicate: bool = True) -> list[dict[str, Any]]:
        records = self.fetch_all_products()
        payload = merge_products(records) if deduplicate else records

        output_path = Path(output_json_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with output_path.open("w", encoding="utf-8") as fh:
            json.dump(payload, fh, indent=4)
        return payload

    def close(self) -> None:
        self._conn.close()
