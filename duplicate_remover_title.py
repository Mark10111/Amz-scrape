import json


def main2(filename):
    #filename = "products3.json"

    # this script removes duplicate items from the products22.json file that have been registered on the same day + appends newer items prices and timestamp to the older already registered items
    print("starting script")

    with open(filename, 'r') as f:
        data = json.load(f)

    unique_items = []
    unique_timestamps = set()

    for item in data:
        timestamp = item['timestamp'][:10]
        if (item['asin'], timestamp) not in unique_timestamps:
            unique_items.append(item)
            unique_timestamps.add((item['asin'], timestamp))

    with open(filename, 'w') as f:
        json.dump(unique_items, f, indent=4)

    # Load data from file
    with open(filename, 'r') as f:
        data = json.load(f)

    # Modify data
    for i in range(len(data)):
        for j in range(i + 1, len(data)):
            if j < len(data) and data[i]['asin'] == data[j]['asin']:
                if data[i]['title'] == "" or data[i]['title'] == "Sponsorizzato":
                    data[i]['title'] = data[j]['title']
                data[i]['price'] += ';' + str(data[j]['price'])  # Convert float to string before concatenating
                data[i]['timestamp'] += ';' + data[j]['timestamp']
                if data[i]["rating"]!=data[j]["rating"] and data[j]["rating"]!="": #more efficient, if the rating is different in the 2nd newer item, update the older item
                    data[i]['rating'] = data[j]['rating']
                if data[i]["review_count"]!=data[j]["review_count"] and data[j]["review_count"]!="": # same as the rating above but with review_count
                    data[i]['review_count'] = data[j]['review_count']
                del data[j]

    # Save modified data to file
    with open(filename, 'w') as f:
        json.dump(data, f, indent=4)

    print("program terminated successfully")
