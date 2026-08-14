from bs4 import BeautifulSoup
import requests
import json
import re
from datetime import datetime
from urllib.parse import urljoin
from fake_useragent import UserAgent
import os
from duplicate_remover_title import main2

filename = "products3.json"
MAX_PAGES_PER_SEARCH = 35
MAX_REQUEST_RETRIES = 5
REQUEST_TIMEOUT = 20

try:
    USER_AGENT = UserAgent()
except Exception:
    USER_AGENT = None


def get_next_pg(soup):
    try:
        pagination_element = soup.find('span',class_='s-pagination-item s-pagination-disabled', string=lambda text: text.isdigit())
        if pagination_element:
            page_number = int(pagination_element.text.strip())
            next_page_element = soup.find('a',
                class_='s-pagination-item s-pagination-next s-pagination-button s-pagination-separator'
                )
            if next_page_element:
                next_page_href = next_page_element.get('href') or ''
                next_page_url = urljoin('https://www.amazon.com', next_page_href)
            else:
                print('Failed to retrieve next page URL 2')
                next_page_url = ''
        else:
            print('Failed to retrieve next page URL 1')
            page_number = ''
            next_page_url = ''
    except Exception:
        print('Failed to retrieve next page URL')
        page_number = ''
        next_page_url = ''
        
    return page_number, next_page_url

def fetch_links(soup):
    products = []
    results = soup.find_all('div', class_='s-result-item')
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
    for result in results:
        asin = result.get('data-asin', '')
        try:
            title_element = result.find("span", {"class": "a-size-base-plus a-color-base a-text-normal"})
            title = title_element.text.strip() if title_element else ''
        except Exception:
            title = ''

        price_element = result.find('span', class_='a-offscreen')
        if price_element:
            price_text = price_element.text.strip()
            price_text = re.sub(r'[^\d.,]', '', price_text)
            price_text = price_text.replace('.', '').replace(',', '.')
            price = price_text
        else:
            price = None

        rating_element = result.find('span', class_='a-icon-alt')
        rating = rating_element.text.strip().split()[0] if rating_element else ''

        review_count_element = result.find('span', class_='a-size-base s-underline-text')
        review_count = review_count_element.text.strip() if review_count_element else ''

        if asin:
            product = {
                'title': title,
                'price': str(price),
                'asin': asin,
                'rating': rating,
                'review_count': review_count,
                'timestamp': timestamp,
            }
            products.append(product)
    return products


def sendRequest(urltosend):
    soup = None
    for _ in range(MAX_REQUEST_RETRIES):
        try:
            user_agent = USER_AGENT.random if USER_AGENT else "Mozilla/5.0"
            headersrando = {'User-Agent': user_agent}
            response = requests.get(urltosend, headers=headersrando, timeout=REQUEST_TIMEOUT)
            if response.ok:
                soup = BeautifulSoup(response.content, 'lxml')
                print('Request was successful')
                break
            print(f'Request failed with status code {response.status_code}, changing header')
        except Exception as err:
            print("def sendRequest(urltosend): ", err)
    return soup

if __name__ == '__main__':
    # The webpage URL
    # add amazon url searches here:
    URL = [
        "https://www.amazon.com/s?k=xiaomi&ref=nb_sb_noss_1",
        "https://www.amazon.com/s?k=iphone+14+pro&i=computers&__mk_it_IT=%C3%85M%C3%85%C5%BD%C3%95%C3%91&crid=E7GZISO0AAIT&sprefix=laptop%2Ccomputers%2C294&ref=nb_sb_noss_1",
        "https://www.amazon.com/s?k=macbook&i=computers&__mk_it_IT=%C3%85M%C3%85%C5%BD%C3%95%C3%91&crid=E7GZISO0AAIT&sprefix=laptop%2Ccomputers%2C294&ref=nb_sb_noss_1",
        "https://www.amazon.com/s?k=snapdragon+gen+1&i=computers&__mk_it_IT=%C3%85M%C3%85%C5%BD%C3%95%C3%91&crid=E7GZISO0AAIT&sprefix=laptop%2Ccomputers%2C294&ref=nb_sb_noss_1",
        "https://www.amazon.com/s?k=low+profile+keyboard&i=computers&__mk_it_IT=%C3%85M%C3%85%C5%BD%C3%95%C3%91&crid=E7GZISO0AAIT&sprefix=laptop%2Ccomputers%2C294&ref=nb_sb_noss_1",
    ]

    all_products = []
    xi = 0
    while xi < len(URL):
                 
        if xi == 0:
            print("Starting url: ", URL[xi])
        else:
            print("going to the next url:", URL[xi])
                         
        soup = sendRequest(URL[xi])
        if soup is None:
            print("Skipping url because first request failed:", URL[xi])
            xi = xi + 1
            continue

        all_products.extend(fetch_links(soup))


        page_number, next_page_url = get_next_pg(soup)

        match = re.search(r'page=(\d+)', next_page_url)
        if match:
            page_num = int(match.group(1))
            page_str = f"page {page_num}"
            print("\ncurrent page: ", page_str)


        i = 1
        if page_number == '':
            page_number = i
            print("changing page number to: ", page_number)
        while i < MAX_PAGES_PER_SEARCH and next_page_url != '':
                         
            next_page_url_soup = sendRequest(next_page_url)
            if next_page_url_soup is None:
                print("Stopping pagination because request failed:", next_page_url)
                break

            all_products.extend(fetch_links(next_page_url_soup))
            result = get_next_pg(next_page_url_soup)
            if result is not None:
                page_number, next_page_url = result

            match = re.search(r'page=(\d+)', next_page_url)
            if match:
                page_num = int(match.group(1))
                page_str = f"page {page_num}"
                print("\ncurrent page: ", page_str)
            print("\nstarting next page, current I:", i, "\nnext link: ", next_page_url, " - page number: ", page_number)
            if page_number == '':
                page_number = i
                print("changing page number to: ", page_number)
            i = i + 1
        xi = xi + 1

    if not os.path.exists(filename) or os.path.getsize(filename) == 0:
        existing_products = []
    else:
        with open(filename, 'r') as infile:
            existing_products = json.load(infile)

    existing_products.extend(all_products)
    with open(filename, 'w') as outfile:
        json.dump(existing_products, outfile, indent=4)

    print("\nProgram terminated")
    main2(filename)

