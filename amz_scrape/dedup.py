from typing import Any


def merge_products(products: list[dict[str, Any]]) -> list[dict[str, Any]]:
    unique_day_items: list[dict[str, Any]] = []
    unique_timestamps: set[tuple[str, str]] = set()

    for item in products:
        asin = item.get("asin")
        timestamp = str(item.get("timestamp", ""))
        if not asin:
            continue

        day_key = (asin, timestamp[:10])
        if day_key not in unique_timestamps:
            unique_day_items.append(item)
            unique_timestamps.add(day_key)

    merged_items_by_asin: dict[str, dict[str, Any]] = {}

    for item in unique_day_items:
        asin = item["asin"]
        if asin not in merged_items_by_asin:
            merged_items_by_asin[asin] = {
                "title": item.get("title", ""),
                "price": str(item.get("price", "")),
                "asin": asin,
                "rating": str(item.get("rating", "")),
                "review_count": int(item.get("review_count", 0)),
                "timestamp": str(item.get("timestamp", "")),
            }
            continue

        current_item = merged_items_by_asin[asin]
        incoming_title = item.get("title", "")
        if current_item["title"] in ("", "Sponsorizzato") and incoming_title:
            current_item["title"] = incoming_title

        incoming_price = str(item.get("price", ""))
        if incoming_price:
            current_item["price"] = (
                f"{current_item['price']};{incoming_price}" if current_item["price"] else incoming_price
            )

        incoming_timestamp = str(item.get("timestamp", ""))
        if incoming_timestamp:
            current_item["timestamp"] = (
                f"{current_item['timestamp']};{incoming_timestamp}"
                if current_item["timestamp"]
                else incoming_timestamp
            )

        incoming_rating = str(item.get("rating", ""))
        if incoming_rating and current_item["rating"] != incoming_rating:
            current_item["rating"] = incoming_rating

        incoming_review_count = int(item.get("review_count", 0))
        if incoming_review_count and current_item["review_count"] != incoming_review_count:
            current_item["review_count"] = incoming_review_count

    return list(merged_items_by_asin.values())
