from newsapi import NewsApiClient
from bs4 import BeautifulSoup
import requests
import datetime
import os
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("NEWS_API_KEY")

def fetch_news(query='indian stock market', count=5):
    try:
        newsapi = NewsApiClient(api_key=api_key)
        news = newsapi.get_everything(q=query, language='en', sort_by='publishedAt', page_size=count)
        return news['articles']
    except:
        return scrape_economic_times(count)

def scrape_economic_times(count=5):
    url = "https://economictimes.indiatimes.com/markets/stocks/news"
    headers = {"User-Agent": "Mozilla/5.0"}
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.content, 'html.parser')

    items = []
    stories = soup.find_all('div', class_='eachStory')[:count]
    for story in stories:
        title = story.find('h3').text.strip()
        link = "https://economictimes.indiatimes.com" + story.find('a')['href']
        desc = story.find('p').text.strip() if story.find('p') else ""
        items.append({
            'title': title,
            'url': link,
            'description': desc,
            'publishedAt': datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        })
    return items
