from amz_scrape.config import cli_overrides_from_args, load_config, parse_args
from amz_scrape.logging_utils import configure_logging
from amz_scrape.scraper import Scraper
from amz_scrape.storage import SQLiteStorage


def main() -> None:
    args = parse_args()
    logger = configure_logging(args.log_level)

    config = load_config(args.config, cli_overrides=cli_overrides_from_args(args))
    scraper = Scraper(config=config, logger=logger)
    storage = SQLiteStorage(config.sqlite_db_path)

    try:
        batches = scraper.scrape()
        for source_url, products in batches:
            storage.save_products(products, source_url)

        exported_products = storage.export_json(config.output_json, deduplicate=True)
        summary = scraper.summary

        logger.info(
            "Scrape completed",
            extra={
                "event": "summary",
                "total_urls": summary.total_urls,
                "requested_pages": summary.requested_pages,
                "scraped_pages": summary.scraped_pages,
                "failed_requests": summary.failed_requests,
                "blocked_pages": summary.blocked_pages,
                "skipped_pages": summary.skipped_pages,
                "items_scraped": summary.items_scraped,
                "unique_products": len(exported_products),
                "sqlite_db": config.sqlite_db_path,
                "output_json": config.output_json,
            },
        )
    finally:
        scraper.close()
        storage.close()


if __name__ == "__main__":
    main()
