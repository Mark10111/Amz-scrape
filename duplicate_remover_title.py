import argparse
import json

from amz_scrape.dedup import merge_products


def main2(filename: str) -> None:
    with open(filename, "r", encoding="utf-8") as f:
        data = json.load(f)

    deduplicated = merge_products(data)

    with open(filename, "w", encoding="utf-8") as f:
        json.dump(deduplicated, f, indent=4)


def main() -> None:
    parser = argparse.ArgumentParser(description="Deduplicate scraped products JSON")
    parser.add_argument("filename", nargs="?", default="products3.json")
    args = parser.parse_args()
    main2(args.filename)


if __name__ == "__main__":
    main()
