import json


def main2(filename):
    print("starting script")

    with open(filename, 'r') as f:
        data = json.load(f)

    unique_day_items = []
    unique_timestamps = set()
    for item in data:
        asin = item.get('asin')
        timestamp = item.get('timestamp', '')
        day_key = (asin, timestamp[:10])
        if asin and day_key not in unique_timestamps:
            unique_day_items.append(item)
            unique_timestamps.add(day_key)

    merged_items_by_asin = {}
    for item in unique_day_items:
        asin = item.get('asin')
        if asin not in merged_items_by_asin:
            merged_items_by_asin[asin] = {
                'title': item.get('title', ''),
                'price': str(item.get('price', '')),
                'asin': asin,
                'rating': item.get('rating', ''),
                'review_count': item.get('review_count', ''),
                'timestamp': item.get('timestamp', ''),
            }
            continue

        current_item = merged_items_by_asin[asin]
        if current_item['title'] in ("", "Sponsorizzato") and item.get('title'):
            current_item['title'] = item.get('title', '')
        current_item['price'] += ';' + str(item.get('price', ''))
        current_item['timestamp'] += ';' + item.get('timestamp', '')

        rating = item.get('rating', '')
        if rating and current_item['rating'] != rating:
            current_item['rating'] = rating

        review_count = item.get('review_count', '')
        if review_count and current_item['review_count'] != review_count:
            current_item['review_count'] = review_count

    with open(filename, 'w') as f:
        json.dump(list(merged_items_by_asin.values()), f, indent=4)

    print("program terminated successfully")
