Amazon Web Scraper

This Python script scrapes product information from Amazon.it and saves it to a JSON file. It utilizes the BeautifulSoup library for web scraping and requests for sending HTTP requests.

Features
Scrapes product titles, prices, ASINs, ratings, and review counts from Amazon.it search pages.
Handles pagination to scrape multiple pages of search results.
Stores the scraped data in a JSON file (products3.json).





Usage
Install the required Python packages listed in requirements.txt.

pip install -r requirements.txt
python3 amazon_scraper.py

The script will start scraping product information from the provided Amazon URLs in the URL list.
Once finished, the scraped data will be saved in the products3.json file.

Contributing
Feel free to contribute to this project by submitting pull requests or reporting issues.

License
This project is licensed under the MIT License - see the LICENSE file for details.
