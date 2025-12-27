from bs4 import BeautifulSoup
import pandas as pd
from scraper.fetcher import fetch_page
import time

def parse_books(limit=20, base_url="http://books.toscrape.com/catalogue/page-{}.html"):
    """
    Scrapes books from a given URL pattern using fetcher.
    """
    books_data = []
    
    rating_map = {'One': '1', 'Two': '2', 'Three': '3', 'Four': '4', 'Five': '5'}
    
    page = 1
    while len(books_data) < limit:
        url = base_url.format(page)
        # fetch_page is now robust
        html = fetch_page(url)
        
        if not html:
            break
            
        soup = BeautifulSoup(html, 'html.parser')
        articles = soup.find_all('article', class_='product_pod')
        
        if not articles:
            break
            
        for article in articles:
            if len(books_data) >= limit:
                break
                
            try:
                title = article.h3.a['title']
                price = article.find('p', class_='price_color').text
                
                star_tag = article.find('p', class_='star-rating')
                rating_classes = star_tag['class']
                rating = "Unknown"
                for cls in rating_classes:
                    if cls in rating_map:
                        rating = rating_map[cls]
                        break
                        
                availability = article.find('p', class_='instock availability').text.strip()
                
                books_data.append({
                    'title': title,
                    'price': price,
                    'rating': rating,
                    'availability': availability
                })
            except AttributeError:
                continue
            
        page += 1
        time.sleep(0.5) 
            
    return pd.DataFrame(books_data)

def parse_quotes(limit=20, base_url="http://quotes.toscrape.com/page/{}/"):
    """
    Scrapes quotes from a given URL pattern using fetcher.
    """
    quotes_data = []
    
    page = 1
    while len(quotes_data) < limit:
        url = base_url.format(page)
        html = fetch_page(url)
        
        if not html:
            break
            
        soup = BeautifulSoup(html, 'html.parser')
        quotes = soup.find_all('div', class_='quote')
        
        if not quotes:
            break
            
        for quote in quotes:
            if len(quotes_data) >= limit:
                break
            
            try:
                text = quote.find('span', class_='text').text
                author = quote.find('small', class_='author').text
                
                tags_container = quote.find('div', class_='tags')
                tags = [tag.text for tag in tags_container.find_all('a', class_='tag')]
                tags_str = ", ".join(tags)
                
                quotes_data.append({
                    'text': text,
                    'author': author,
                    'tags': tags_str
                })
            except AttributeError:
                continue
            
        page += 1
        time.sleep(0.5)
            
            
    return pd.DataFrame(quotes_data)

def parse_jobs(limit=20, base_url="https://realpython.github.io/fake-jobs/"):
    """
    Scrapes jobs from https://realpython.github.io/fake-jobs/ (single page demo).
    """
    jobs_data = []
    
    # This site lists all jobs on the main page, so no paging loop strictly needed for the demo main page
    # but we can implement a visual limit
    
    html = fetch_page(base_url)
    if html:
        soup = BeautifulSoup(html, 'html.parser')
        cards = soup.find_all('div', class_='card')
        
        for card in cards:
            if len(jobs_data) >= limit:
                break
                
            try:
                title = card.find('h2', class_='title').text.strip()
                company = card.find('h3', class_='company').text.strip()
                location = card.find('p', class_='location').text.strip()
                date_posted = card.find('time').text.strip()
                
                jobs_data.append({
                    'title': title,
                    'company': company,
                    'location': location,
                    'date_posted': date_posted
                })
            except AttributeError:
                continue
                
    return pd.DataFrame(jobs_data)
