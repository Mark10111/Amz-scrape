from bs4 import BeautifulSoup
import requests
import json
import re
from datetime import datetime
import locale
from fake_useragent import UserAgent
import os
from duplicate_remover_title import *

products = []
filename="products3.json"
# Function to extract Product Title




def get_next_pg(soup):
    try:
        pagination_element = soup.find('span',
									class_='s-pagination-item s-pagination-disabled'
									, string=lambda text: text.isdigit())
        if pagination_element:
            page_number = int(pagination_element.text.strip())
            next_page_element = soup.find('a',
                class_='s-pagination-item s-pagination-next s-pagination-button s-pagination-separator'
                )
            if next_page_element:
                next_page_url = 'https://www.amazon.it' + next_page_element.get('href')
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
    # Check if file is empty
    if os.path.getsize(filename) == 0:
        with open(filename, 'w') as outfile:
            json.dump([], outfile, indent=4)

    # Fetch links as List of Tag Objects
    results = soup.find_all('div', class_='s-result-item')

    try:
        with open(filename, 'r') as infile:
            data = json.load(infile)
    except FileNotFoundError:
        data = []


    for result in results:
        # Extract ASIN
        asin = result['data-asin']

        # Extract title
        try:
            #title_element = result.find('span', class_= ['a-size-medium', 'a-color-base', 'a-text-normal']) old one, gave "" and "Sponsorizzato" problems
            title_element = result.find("span", {"class": "a-size-base-plus a-color-base a-text-normal"})
            title = title_element.text.strip() if title_element else ''
        except Exception as e:
            print('Failed to retrieve title', e)

        # Extract price
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

        # Create a dictionary to hold the product data if the asin was registered
        if asin:
            product = {
                'title': title,
                'price': str(price),
                'asin': asin,
                'rating': rating,
                'review_count': review_count,
                'timestamp': str(datetime.now().strftime("%Y-%m-%d %H:%M")),
            }
	    	#print out the product description
            #print('asin:', asin)
            #print('title:', title)
            #print('price:', price)#,"-", type(price))
            #print("timestamp", str(datetime.now().strftime("%Y-%m-%d %H:%M")))    
            products.append(product)

    data.extend(products)

    with open(filename, 'w') as outfile:
        json.dump(data, outfile, indent=4)









def sendRequest(urltosend):
	try:
		tof = False
		while not tof:
			ua = UserAgent()
			headersrando = {'User-Agent': ua.random}
			response = requests.get(urltosend, headers=headersrando)
			if response.ok:
				tof = True
				soup = BeautifulSoup(response.content, 'lxml')
				print('Request was successful')
			else:
				print(f'Request failed with status code {response.status_code}, changing header')
				soup = None
	except Exception as E:
		print("def sendRequest(urltosend): ", E)

	return soup









if __name__ == '__main__':


	# The webpage URL
	#URL = "https://www.amazon.it/s?k=laptop&i=computers&__mk_it_IT=%C3%85M%C3%85%C5%BD%C3%95%C3%91&crid=E7GZISO0AAIT&sprefix=laptop%2Ccomputers%2C294&ref=nb_sb_noss_1"
	URL = [	
    "https://www.amazon.it/s?k=xiaomi&ref=nb_sb_noss_1",
    "https://www.amazon.it/s?k=scheda+video&i=computers&__mk_it_IT=%C3%85M%C3%85%C5%BD%C3%95%C3%91&crid=E7GZISO0AAIT&sprefix=laptop%2Ccomputers%2C294&ref=nb_sb_noss_1",
    "https://www.amazon.it/s?k=iphone+14+pro&i=computers&__mk_it_IT=%C3%85M%C3%85%C5%BD%C3%95%C3%91&crid=E7GZISO0AAIT&sprefix=laptop%2Ccomputers%2C294&ref=nb_sb_noss_1",
    "https://www.amazon.it/s?k=cuffie+wireless&i=computers&__mk_it_IT=%C3%85M%C3%85%C5%BD%C3%95%C3%91&crid=E7GZISO0AAIT&sprefix=laptop%2Ccomputers%2C294&ref=nb_sb_noss_1",
    "https://www.amazon.it/s?k=mouse+gaming&i=computers&__mk_it_IT=%C3%85M%C3%85%C5%BD%C3%95%C3%91&crid=E7GZISO0AAIT&sprefix=laptop%2Ccomputers%2C294&ref=nb_sb_noss_1",
    "https://www.amazon.it/s?k=snapdragon+gen+1&i=computers&__mk_it_IT=%C3%85M%C3%85%C5%BD%C3%95%C3%91&crid=E7GZISO0AAIT&sprefix=laptop%2Ccomputers%2C294&ref=nb_sb_noss_1",
    "https://www.amazon.it/s?k=macbook&i=computers&__mk_it_IT=%C3%85M%C3%85%C5%BD%C3%95%C3%91&crid=E7GZISO0AAIT&sprefix=laptop%2Ccomputers%2C294&ref=nb_sb_noss_1",
    "https://www.amazon.it/s?k=snapdragon+gen+1&i=computers&__mk_it_IT=%C3%85M%C3%85%C5%BD%C3%95%C3%91&crid=E7GZISO0AAIT&sprefix=laptop%2Ccomputers%2C294&ref=nb_sb_noss_1",
    "https://www.amazon.it/s?k=hard+disk+esterno&i=computers&__mk_it_IT=%C3%85M%C3%85%C5%BD%C3%95%C3%91&ref=nb_sb_noss",
    "https://www.amazon.it/s?k=low+profile+keyboard&i=computers&__mk_it_IT=%C3%85M%C3%85%C5%BD%C3%95%C3%91&crid=E7GZISO0AAIT&sprefix=laptop%2Ccomputers%2C294&ref=nb_sb_noss_1"
]

	xi = 0
	while xi < len(URL):
                
		if xi ==0:
			print("Starting url: ", URL[xi])    
		else:
			print("going to the next url:", URL[xi])
                        
		#send the first soup request to get item listing
		soup = sendRequest(URL[xi])

		#go get the individual link of each item on the current item listing link
		fetch_links(soup)


		#get number of last pages and link to the next page
		page_number, next_page_url= get_next_pg(soup)
		#print("page number max: ", page_number,", next pg url: ",next_page_url)
		
		
		match = re.search(r'page=(\d+)', next_page_url)
		if match:
			page_num = int(match.group(1))
			page_str = f"page {page_num}"
			print("\ncurrent page: ", page_str)


		i = 1
		if page_number=='':
			page_number = i
			print("changing page number to: ",page_number)
		#while i < page_number or not next_page_url:
		while i < 35 and next_page_url!='':
                        
			try:
				next_page_url_soup = sendRequest(next_page_url)
				#get number of last pages and link to the next page
			except Exception as problem_with_next_page_url_soup:
				print("next_page_url_soup = sendRequest(next_page_url): ")#, next_page_url_soup, "\nthe error:", problem_with_next_page_url_soup)

			#a = input("continue?")
			#go get the individual link of each item on the current item listing link
			fetch_links(next_page_url_soup)
			#print("old  page url: ",next_page_url)        
			result = get_next_pg(next_page_url_soup)
			if result is not None:
				page_number, next_page_url = result
				# Rest of your code that uses `userless_var` and `next_page_url`
			else:
				pass
			#print("page number max: ", page_number,", NEW next pg url: ",next_page_url)
			
			match = re.search(r'page=(\d+)', next_page_url)
			if match:
				page_num = int(match.group(1))
				page_str = f"page {page_num}"
				print("\ncurrent page: ", page_str)
			print("\nstarting next page, current I:", i, "\nnext link: ", next_page_url , " - page number: ",page_number)
			if page_number=='':
				page_number = i
				print("changing page number to: ",page_number)
			i=i+1
		xi = xi+1

print("\nProgram terminated")
main2(filename)



