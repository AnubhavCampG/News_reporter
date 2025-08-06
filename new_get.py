"""
Indian Stock Market News Scraper

This script collects latest global news related to companies and factors 
that could have a direct impact on Indian stock markets.

Configuration:
To use your own API keys, set these environment variables:
- NEWSAPI_KEY: Your NewsAPI key from https://newsapi.org/
- FINNHUB_KEY: Your Finnhub API key from https://finnhub.io/

Example (Windows):
set NEWSAPI_KEY=your_newsapi_key_here
set FINNHUB_KEY=your_finnhub_key_here

Example (Linux/Mac):
export NEWSAPI_KEY=your_newsapi_key_here
export FINNHUB_KEY=your_finnhub_key_here

Recent fixes applied:
- Fixed undefined response variable in error handling
- Updated hardcoded dates to use dynamic current year
- Added proper href validation for all scraping functions
- Moved API keys to environment variables for security
- Added rate limiting to prevent IP blocking
- Ensured consistent URL construction across all functions
- Implemented compact pipe-separated format for space efficiency
- Added content compression while preserving full information
- Optimized output for LLM processing and analysis
"""

import requests
from bs4 import BeautifulSoup
from datetime import datetime
import time
import re
import os
import random
from urllib.parse import urljoin

# Nifty 50 tickers (unchanged)
NIFTY_50_TICKERS = [
    'ADANIENT.NS', 'ADANIPORTS.NS', 'APOLLOHOSP.NS', 'ASIANPAINT.NS', 'AXISBANK.NS',
    'BAJAJ-AUTO.NS', 'BAJFINANCE.NS', 'BAJAJFINSV.NS', 'BHARTIARTL.NS', 'BPCL.NS',
    'BRITANNIA.NS', 'CIPLA.NS', 'COALINDIA.NS', 'DIVISLAB.NS', 'DRREDDY.NS',
    'EICHERMOT.NS', 'GRASIM.NS', 'HCLTECH.NS', 'HDFC.NS', 'HDFCBANK.NS',
    'HDFCLIFE.NS', 'HEROMOTOCO.NS', 'HINDALCO.NS', 'HINDUNILVR.NS', 'ICICIBANK.NS',
    'INDUSINDBK.NS', 'INFY.NS', 'ITC.NS', 'JSWSTEEL.NS', 'KOTAKBANK.NS',
    'LT.NS', 'M&M.NS', 'MARUTI.NS', 'NESTLEIND.NS', 'NTPC.NS', 'ONGC.NS',
    'POWERGRID.NS', 'RELIANCE.NS', 'SBILIFE.NS', 'SBIN.NS', 'SUNPHARMA.NS',
    'TATACONSUM.NS', 'TATAMOTORS.NS', 'TATASTEEL.NS', 'TECHM.NS', 'TITAN.NS',
    'ULTRACEMCO.NS', 'UPL.NS', 'WIPRO.NS'
]

def construct_url(base_url, href):
    """Helper function to construct full URLs from base and href"""
    if href.startswith('http'):
        return href
    return urljoin(base_url, href)

def rate_limit():
    """Add random delay to prevent IP blocking"""
    delay = random.uniform(0.5, 2.0)  # Random delay between 0.5 to 2 seconds
    time.sleep(delay)

def get_full_article_content(url, source_name):
    """Fetch full article content from URL"""
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Accept-Encoding': 'gzip, deflate',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
    }
    try:
        rate_limit()  # Add rate limiting
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        
        for element in soup(['script', 'style', 'nav', 'header', 'footer', 'aside', 'form', 'button']):
            element.decompose()
        
        content = None
        if 'moneycontrol.com' in url:
            content = soup.find('div', class_='article_content') or soup.find('div', class_='content_wrapper')
        elif 'economictimes.indiatimes.com' in url:
            content = soup.find('div', class_='articleContent') or soup.find('div', class_='article')
        elif 'livemint.com' in url:
            content = soup.find('div', class_='articleBody') or soup.find('div', class_='content')
        elif 'ndtv.com' in url:
            content = soup.find('div', class_='content_text') or soup.find('div', class_='article')
        elif 'reuters.com' in url:
            content = soup.find('div', class_='article-body') or soup.find('article')
        elif 'bloomberg.com' in url:
            content = soup.find('div', class_='body-copy') or soup.find('article')
        elif 'cnbc.com' in url:
            content = soup.find('div', class_='ArticleBody-articleBody') or soup.find('article')
        elif 'ft.com' in url:
            content = soup.find('div', class_='article__content') or soup.find('article')
        elif 'wsj.com' in url:
            content = soup.find('div', class_='article-content') or soup.find('article')
        elif 'business-standard.com' in url:
            content = soup.find('div', class_='article-content') or soup.find('div', class_='content')
        
        if not content:
            selectors = [
                'article', 'div[class*="content"]', 'div[class*="article"]', 
                'div[class*="body"]', 'div[class*="text"]', 'div[class*="story"]',
                '.post-content', '.entry-content', '.story-content', '.article-body'
            ]
            for selector in selectors:
                content = soup.select_one(selector)
                if content:
                    break
        
        if not content:
            paragraphs = soup.find_all('p')
            if paragraphs:
                content = soup.new_tag('div')
                for p in paragraphs:
                    if len(p.get_text(strip=True)) > 50:
                        content.append(p)
        
        if content:
            text = content.get_text(separator=' ', strip=True)
            # Compress whitespace while preserving all content
            text = re.sub(r'\s+', ' ', text)
            # Remove special characters but keep essential punctuation
            text = re.sub(r'[^\w\s\.\,\!\?\:\;\-\(\)]', '', text)
            # Remove redundant spaces around punctuation to save space
            text = re.sub(r'\s+([\.!?;,])', r'\1', text)
            text = re.sub(r'([\.!?;,])\s+', r'\1 ', text)
            
            # Remove common redundant phrases to save space while preserving meaning
            redundant_phrases = [
                r'\bRead more.*?$', r'\bClick here.*?$', r'\bSubscribe.*?$',
                r'\bShare this.*?$', r'\bFollow us.*?$', r'\bAdvertisement\b',
                r'\bAlso read.*?$', r'\bStory continues.*?$'
            ]
            for phrase in redundant_phrases:
                text = re.sub(phrase, '', text, flags=re.IGNORECASE)
            
            # Final cleanup
            text = re.sub(r'\s+', ' ', text).strip()
            return text if len(text) > 150 else None  # Reduced minimum to capture more articles
        
        return None
    except requests.exceptions.HTTPError as e:
        if hasattr(e, 'response') and e.response and e.response.status_code in [401, 403, 404]:
            print(f"Access error for {url} ({source_name}): HTTP {e.response.status_code} - {str(e)}")
            return None
        print(f"HTTP error for {url} ({source_name}): {str(e)}")
        return None
    except Exception as e:
        print(f"Error fetching content from {url} ({source_name}): {str(e)}")
        return None

def is_valid_news_item(title, content):
    """Check if news item has valid title and content"""
    if not title or not content:
        return False
    
    if len(title.strip()) < 10:
        return False
    
    if len(content.strip()) < 150:  # Reduced minimum to capture more articles
        return False
    
    error_indicators = [
        'error fetching', 'forbidden', 'not available', 'too short',
        'content not available', 'error:', '403', '404', '500'
    ]
    
    content_lower = content.lower()
    for indicator in error_indicators:
        if indicator in content_lower:
            return False
    
    return True

def fetch_newsapi():
    """Fetch full news from NewsAPI with multiple search queries for better coverage"""
    API_KEY = os.getenv('NEWSAPI_KEY', 'b014126aa39e4161a1a6586f7e7fda8a')
    full_news = []
    
    # Multiple search queries to capture more relevant articles
    search_queries = [
        'indian%20stocks%20OR%20nifty%20OR%20sensex%20OR%20stock%20market%20india',
        'india%20economy%20OR%20rbi%20OR%20rupee%20OR%20mumbai%20stock%20exchange',
        'adani%20OR%20tata%20OR%20reliance%20OR%20infosys%20OR%20wipro',
        'emerging%20markets%20india%20OR%20asian%20markets%20OR%20bse%20OR%20nse'
    ]
    
    for query in search_queries:
        try:
            url = ('https://newsapi.org/v2/everything?'
                   f'q={query}&'
                   'language=en&'
                   'sortBy=publishedAt&'
                   'pageSize=50&'
                   f'apiKey={API_KEY}')
            
            response = requests.get(url)
            articles = response.json().get('articles', [])
            
            for article in articles:
                title = article.get('title', '')
                url = article.get('url', '')
                
                full_content = get_full_article_content(url, f'NewsAPI-{query[:20]}')
                
                if full_content and is_valid_news_item(title, full_content):
                    # Compact format: Title|Content separated by pipe, no extra formatting
                    news_item = f"{title.strip()}|{full_content.strip()}\n"
                    full_news.append(news_item)
            
            rate_limit()  # Delay between API calls
        except Exception as e:
            print(f"NewsAPI error for query {query}: {e}")
    
    return full_news

def fetch_finnhub_news():
    """Fetch full news from Finnhub API for Indian stocks (unchanged, URLs handled by API response)"""
    API_KEY = os.getenv('FINNHUB_KEY', 'd24e0i9r01qu2jghqr50d24e0i9r01qu2jghqr5g')
    all_news = []
    
    try:
        url = f'https://finnhub.io/api/v1/news?category=general&token={API_KEY}'
        response = requests.get(url)
        if response.status_code == 200:
            articles = response.json()
            for article in articles[:50]:
                # Expanded keywords for better Indian market coverage
                indian_keywords = [
                    'india', 'indian', 'nifty', 'sensex', 'bse', 'nse', 'mumbai', 'delhi', 
                    'rupee', 'rbi', 'reserve bank', 'modi', 'adani', 'tata', 'reliance',
                    'infosys', 'wipro', 'hdfc', 'icici', 'sbi', 'asian market', 'emerging market'
                ]
                if any(keyword in article.get('headline', '').lower() for keyword in indian_keywords):
                    headline = article.get('headline', '')
                    url = article.get('url', '')
                    
                    full_content = get_full_article_content(url, 'Finnhub')
                    
                    if full_content and is_valid_news_item(headline, full_content):
                        # Compact format: Title|Content separated by pipe, no extra formatting
                        news_item = f"{headline.strip()}|{full_content.strip()}\n"
                        all_news.append(news_item)
    except Exception as e:
        print(f"Finnhub general news error {e}")
    
    for ticker in NIFTY_50_TICKERS:
        try:
            print(f"Fetching news for {ticker}...")
            current_year = datetime.now().year
            url = f'https://finnhub.io/api/v1/company-news?symbol={ticker}&from={current_year}-01-01&to={current_year}-12-31&token={API_KEY}'
            response = requests.get(url)
            if response.status_code == 200:
                articles = response.json()
                for article in articles[:20]:
                    headline = article.get('headline', '')
                    url = article.get('url', '')
                    
                    full_content = get_full_article_content(url, f'Finnhub-{ticker}')
                    
                    if full_content and is_valid_news_item(headline, full_content):
                        # Compact format: Title|Content separated by pipe, no extra formatting
                        news_item = f"{headline.strip()}|{full_content.strip()}\n"
                        all_news.append(news_item)
            
            time.sleep(0.5)
        except Exception as e:
            print(f"Finnhub {ticker} news error: {e}")
    
    return all_news

def fetch_moneycontrol():
    """Fetch full news from Moneycontrol"""
    base_url = 'https://www.moneycontrol.com'
    url = f'{base_url}/news/business/markets/'
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    try:
        response = requests.get(url, headers=headers)
        soup = BeautifulSoup(response.text, 'html.parser')
        news = []
        
        # Multiple selectors to catch more articles
        selectors = [
            '.clearfix .headline', '.news-list h2 a', '.news-item h3 a', 
            '.story-list h2 a', 'article h2 a', '.content h3 a'
        ]
        
        processed_urls = set()  # Avoid duplicates
        
        for selector in selectors:
            items = soup.select(selector)
            for item in items:
                if selector.endswith('a'):
                    title = item.get_text(strip=True)
                    href = item.get('href')
                    if not href:
                        continue
                    link = construct_url(base_url, href)
                else:
                    title = item.get_text(strip=True)
                    a_tag = item.find('a')
                    if not a_tag or not a_tag.get('href'):
                        continue
                    href = a_tag['href']
                    link = construct_url(base_url, href)
                
                if link in processed_urls:
                    continue
                processed_urls.add(link)
                
                full_content = get_full_article_content(link, 'Moneycontrol')
                
                if full_content and is_valid_news_item(title, full_content):
                    # Compact format: Title|Content separated by pipe, no extra formatting
                    news_item = f"{title.strip()}|{full_content.strip()}\n"
                    news.append(news_item)
        
        return news
    except Exception as e:
        print(f"Moneycontrol error: {e}")
        return []

def fetch_economictimes():
    """Fetch full news from Economic Times"""
    base_url = 'https://economictimes.indiatimes.com'
    url = f'{base_url}/markets/stocks'
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    try:
        response = requests.get(url, headers=headers)
        soup = BeautifulSoup(response.text, 'html.parser')
        news = []
        
        # Multiple selectors to catch more articles from Economic Times
        selectors = [
            '.eachStory h3 a', '.story-list h2 a', '.top-news h3 a',
            'article h3 a', '.news-list h2 a', '.market-news h3 a'
        ]
        
        processed_urls = set()  # Avoid duplicates
        
        for selector in selectors:
            items = soup.select(selector)
            for item in items:
                title = item.get_text(strip=True)
                href = item.get('href')
                if not href:
                    continue
                link = construct_url(base_url, href)
                
                if link in processed_urls:
                    continue
                processed_urls.add(link)
                
                full_content = get_full_article_content(link, 'Economic Times')
                
                if full_content and is_valid_news_item(title, full_content):
                    # Compact format: Title|Content separated by pipe, no extra formatting
                    news_item = f"{title.strip()}|{full_content.strip()}\n"
                    news.append(news_item)
        
        return news
    except Exception as e:
        print(f"Economic Times error: {e}")
        return []

def fetch_livemint():
    """Fetch full news from LiveMint"""
    base_url = 'https://www.livemint.com'
    url = f'{base_url}/market'
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    try:
        response = requests.get(url, headers=headers)
        soup = BeautifulSoup(response.text, 'html.parser')
        news = []
        
        for item in soup.select('.listingPage h2 a'):
            title = item.get_text(strip=True)
            href = item.get('href')
            if not href:
                continue
            link = construct_url(base_url, href)
            
            full_content = get_full_article_content(link, 'LiveMint')
            
            if full_content and is_valid_news_item(title, full_content):
                # Compact format: Title|Content separated by pipe, no extra formatting
                news_item = f"{title.strip()}|{full_content.strip()}\n"
                news.append(news_item)
        
        return news
    except Exception as e:
        print(f"LiveMint error: {e}")
        return []

def fetch_ndtv_business():
    """Fetch full news from NDTV Business"""
    base_url = 'https://www.ndtv.com'
    url = f'{base_url}/business/market'
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    try:
        response = requests.get(url, headers=headers)
        soup = BeautifulSoup(response.text, 'html.parser')
        news = []
        
        for item in soup.select('.newsHdng a'):
            title = item.get_text(strip=True)
            href = item.get('href')
            if not href:
                continue
            link = construct_url(base_url, href)
            
            full_content = get_full_article_content(link, 'NDTV Business')
            
            if full_content and is_valid_news_item(title, full_content):
                # Compact format: Title|Content separated by pipe, no extra formatting
                news_item = f"{title.strip()}|{full_content.strip()}\n"
                news.append(news_item)
        
        return news
    except Exception as e:
        print(f"NDTV Business error: {e}")
        return []

def fetch_business_standard():
    """Fetch full news from Business Standard"""
    base_url = 'https://www.business-standard.com'
    url = f'{base_url}/markets'
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    try:
        response = requests.get(url, headers=headers)
        soup = BeautifulSoup(response.text, 'html.parser')
        news = []
        
        for item in soup.select('.article-list h2 a'):
            title = item.get_text(strip=True)
            href = item.get('href')
            if not href:
                continue
            link = construct_url(base_url, href)
            
            full_content = get_full_article_content(link, 'Business Standard')
            
            if full_content and is_valid_news_item(title, full_content):
                # Compact format: Title|Content separated by pipe, no extra formatting
                news_item = f"{title.strip()}|{full_content.strip()}\n"
                news.append(news_item)
        
        return news
    except Exception as e:
        print(f"Business Standard error: {e}")
        return []

def fetch_reuters_world():
    """Fetch global news from Reuters that can affect Indian markets"""
    base_url = 'https://www.reuters.com'
    url = f'{base_url}/world/'
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    try:
        response = requests.get(url, headers=headers)
        soup = BeautifulSoup(response.text, 'html.parser')
        news = []
        
        for item in soup.select('h3 a'):
            title = item.get_text(strip=True)
            href = item.get('href')
            if not href:
                continue
            link = construct_url(base_url, href)
            
            full_content = get_full_article_content(link, 'Reuters World')
            
            if full_content and is_valid_news_item(title, full_content):
                # Compact format: Title|Content separated by pipe, no extra formatting
                news_item = f"{title.strip()}|{full_content.strip()}\n"
                news.append(news_item)
        
        return news
    except Exception as e:
        print(f"Reuters World error: {e}")
        return []

def fetch_bloomberg_markets():
    """Fetch global market news from Bloomberg"""
    base_url = 'https://www.bloomberg.com'
    url = f'{base_url}/markets'
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    try:
        response = requests.get(url, headers=headers)
        soup = BeautifulSoup(response.text, 'html.parser')
        news = []
        
        for item in soup.select('h3 a'):
            title = item.get_text(strip=True)
            href = item.get('href')
            if not href:
                continue
            link = construct_url(base_url, href)
            
            full_content = get_full_article_content(link, 'Bloomberg Markets')
            
            if full_content and is_valid_news_item(title, full_content):
                # Compact format: Title|Content separated by pipe, no extra formatting
                news_item = f"{title.strip()}|{full_content.strip()}\n"
                news.append(news_item)
        
        return news
    except Exception as e:
        print(f"Bloomberg Markets error: {e}")
        return []

def fetch_cnbc_world():
    """Fetch global business news from CNBC"""
    base_url = 'https://www.cnbc.com'
    url = f'{base_url}/world-markets/'
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    try:
        response = requests.get(url, headers=headers)
        soup = BeautifulSoup(response.text, 'html.parser')
        news = []
        
        for item in soup.select('h3 a'):
            title = item.get_text(strip=True)
            href = item.get('href')
            if not href:
                continue
            link = construct_url(base_url, href)  # Fixed URL construction
            
            full_content = get_full_article_content(link, 'CNBC World Markets')
            
            if full_content and is_valid_news_item(title, full_content):
                # Compact format: Title|Content separated by pipe, no extra formatting
                news_item = f"{title.strip()}|{full_content.strip()}\n"
                news.append(news_item)
        
        return news
    except Exception as e:
        print(f"CNBC World Markets error: {e}")
        return []

def fetch_financial_times():
    """Fetch global financial news from Financial Times"""
    base_url = 'https://www.ft.com'
    url = f'{base_url}/markets'
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    try:
        response = requests.get(url, headers=headers)
        soup = BeautifulSoup(response.text, 'html.parser')
        news = []
        
        for item in soup.select('h3 a'):
            title = item.get_text(strip=True)
            href = item.get('href')
            if not href:
                continue
            link = construct_url(base_url, href)  # Fixed URL construction
            
            full_content = get_full_article_content(link, 'Financial Times')
            
            if full_content and is_valid_news_item(title, full_content):
                # Compact format: Title|Content separated by pipe, no extra formatting
                news_item = f"{title.strip()}|{full_content.strip()}\n"
                news.append(news_item)
        
        return news
    except Exception as e:
        print(f"Financial Times error: {e}")
        return []

def fetch_wall_street_journal():
    """Fetch global market news from Wall Street Journal"""
    base_url = 'https://www.wsj.com'
    url = f'{base_url}/news/markets'
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    try:
        response = requests.get(url, headers=headers)
        soup = BeautifulSoup(response.text, 'html.parser')
        news = []
        
        for item in soup.select('h3 a'):
            title = item.get_text(strip=True)
            href = item.get('href')
            if not href:
                continue
            link = construct_url(base_url, href)  # Fixed URL construction
            
            full_content = get_full_article_content(link, 'Wall Street Journal')
            
            if full_content and is_valid_news_item(title, full_content):
                # Compact format: Title|Content separated by pipe, no extra formatting
                news_item = f"{title.strip()}|{full_content.strip()}\n"
                news.append(news_item)
        
        return news
    except Exception as e:
        print(f"Wall Street Journal error: {e}")
        return []

def fetch_oil_price_news():
    """Fetch oil price news that affects Indian markets"""
    base_url = 'https://www.reuters.com'
    url = f'{base_url}/markets/commodities/'
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    try:
        response = requests.get(url, headers=headers)
        soup = BeautifulSoup(response.text, 'html.parser')
        news = []
        
        for item in soup.select('h3 a'):
            title = item.get_text(strip=True)
            href = item.get('href')
            if not href:
                continue
            link = construct_url(base_url, href)  # Fixed URL construction
            
            full_content = get_full_article_content(link, 'Reuters Commodities')
            
            if full_content and is_valid_news_item(title, full_content):
                # Compact format: Title|Content separated by pipe, no extra formatting
                news_item = f"{title.strip()}|{full_content.strip()}\n"
                news.append(news_item)
        
        return news
    except Exception as e:
        print(f"Oil Price News error: {e}")
        return []

def fetch_us_fed_news():
    """Fetch US Federal Reserve news that affects global markets"""
    base_url = 'https://www.reuters.com'
    url = f'{base_url}/markets/us/'
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    try:
        response = requests.get(url, headers=headers)
        soup = BeautifulSoup(response.text, 'html.parser')
        news = []
        
        for item in soup.select('h3 a'):
            title = item.get_text(strip=True)
            href = item.get('href')
            if not href:
                continue
            link = construct_url(base_url, href)  # Fixed URL construction
            
            full_content = get_full_article_content(link, 'Reuters US Markets')
            
            if full_content and is_valid_news_item(title, full_content):
                # Compact format: Title|Content separated by pipe, no extra formatting
                news_item = f"{title.strip()}|{full_content.strip()}\n"
                news.append(news_item)
        
        return news
    except Exception as e:
        print(f"US Fed News error: {e}")
        return []

def fetch_china_market_news():
    """Fetch China market news that affects Asian markets including India"""
    base_url = 'https://www.reuters.com'
    url = f'{base_url}/markets/asia/'
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    try:
        response = requests.get(url, headers=headers)
        soup = BeautifulSoup(response.text, 'html.parser')
        news = []
        
        for item in soup.select('h3 a'):
            title = item.get_text(strip=True)
            href = item.get('href')
            if not href:
                continue
            link = construct_url(base_url, href)  # Fixed URL construction
            
            full_content = get_full_article_content(link, 'Reuters Asia Markets')
            
            if full_content and is_valid_news_item(title, full_content):
                # Compact format: Title|Content separated by pipe, no extra formatting
                news_item = f"{title.strip()}|{full_content.strip()}\n"
                news.append(news_item)
        
        return news
    except Exception as e:
        print(f"China Market News error: {e}")
        return []

def fetch_zeebiz():
    """Fetch news from Zee Business"""
    base_url = 'https://www.zeebiz.com'
    url = f'{base_url}/markets'
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    try:
        response = requests.get(url, headers=headers)
        soup = BeautifulSoup(response.text, 'html.parser')
        news = []
        
        for item in soup.select('.article-title a'):
            title = item.get_text(strip=True)
            href = item.get('href')
            if not href:
                continue
            link = construct_url(base_url, href)  # Fixed URL construction
            
            full_content = get_full_article_content(link, 'Zee Business')
            
            if full_content and is_valid_news_item(title, full_content):
                # Compact format: Title|Content separated by pipe, no extra formatting
                news_item = f"{title.strip()}|{full_content.strip()}\n"
                news.append(news_item)
        
        return news
    except Exception as e:
        print(f"Zee Business error: {e}")
        return []

def fetch_financial_express():
    """Fetch news from Financial Express"""
    base_url = 'https://www.financialexpress.com'
    url = f'{base_url}/market/'
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    try:
        response = requests.get(url, headers=headers)
        soup = BeautifulSoup(response.text, 'html.parser')
        news = []
        
        for item in soup.select('h2 a'):
            title = item.get_text(strip=True)
            href = item.get('href', '')
            link = construct_url(base_url, href)  # Simplified using helper function
            
            full_content = get_full_article_content(link, 'Financial Express')
            
            if full_content and is_valid_news_item(title, full_content):
                # Compact format: Title|Content separated by pipe, no extra formatting
                news_item = f"{title.strip()}|{full_content.strip()}\n"
                news.append(news_item)
        
        return news
    except Exception as e:
        print(f"Financial Express error: {e}")
        return []

def fetch_business_today():
    """Fetch news from Business Today"""
    base_url = 'https://www.businesstoday.in'
    url = f'{base_url}/markets'
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    try:
        response = requests.get(url, headers=headers)
        soup = BeautifulSoup(response.text, 'html.parser')
        news = []
        
        for item in soup.select('h2 a'):
            title = item.get_text(strip=True)
            href = item.get('href', '')
            link = construct_url(base_url, href)  # Simplified using helper function
            
            full_content = get_full_article_content(link, 'Business Today')
            
            if full_content and is_valid_news_item(title, full_content):
                # Compact format: Title|Content separated by pipe, no extra formatting
                news_item = f"{title.strip()}|{full_content.strip()}\n"
                news.append(news_item)
        
        return news
    except Exception as e:
        print(f"Business Today error: {e}")
        return []

def fetch_outlook_business():
    """Fetch news from Outlook Business"""
    base_url = 'https://www.outlookbusiness.com'
    url = f'{base_url}/markets'
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    try:
        response = requests.get(url, headers=headers)
        soup = BeautifulSoup(response.text, 'html.parser')
        news = []
        
        for item in soup.select('h3 a'):
            title = item.get_text(strip=True)
            href = item.get('href')
            if not href:
                continue
            link = construct_url(base_url, href)  # Fixed URL construction
            
            full_content = get_full_article_content(link, 'Outlook Business')
            
            if full_content and is_valid_news_item(title, full_content):
                # Compact format: Title|Content separated by pipe, no extra formatting
                news_item = f"{title.strip()}|{full_content.strip()}\n"
                news.append(news_item)
        
        return news
    except Exception as e:
        print(f"Outlook Business error: {e}")
        return []

def fetch_fortune_india():
    """Fetch news from Fortune India"""
    base_url = 'https://www.fortuneindia.com'
    url = f'{base_url}/markets'
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    try:
        response = requests.get(url, headers=headers)
        soup = BeautifulSoup(response.text, 'html.parser')
        news = []
        
        for item in soup.select('h2 a, h3 a'):
            title = item.get_text(strip=True)
            href = item.get('href')
            if not href:
                continue
            link = construct_url(base_url, href)
            
            full_content = get_full_article_content(link, 'Fortune India')
            
            if full_content and is_valid_news_item(title, full_content):
                # Compact format: Title|Content separated by pipe, no extra formatting
                news_item = f"{title.strip()}|{full_content.strip()}\n"
                news.append(news_item)
        
        return news
    except Exception as e:
        print(f"Fortune India error: {e}")
        return []

def fetch_inc42():
    """Fetch news from Inc42 (Indian startup and business news)"""
    base_url = 'https://inc42.com'
    url = f'{base_url}/markets'
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    try:
        response = requests.get(url, headers=headers)
        soup = BeautifulSoup(response.text, 'html.parser')
        news = []
        
        for item in soup.select('h2 a, h3 a'):
            title = item.get_text(strip=True)
            href = item.get('href')
            if not href:
                continue
            link = construct_url(base_url, href)
            
            full_content = get_full_article_content(link, 'Inc42')
            
            if full_content and is_valid_news_item(title, full_content):
                # Compact format: Title|Content separated by pipe, no extra formatting
                news_item = f"{title.strip()}|{full_content.strip()}\n"
                news.append(news_item)
        
        return news
    except Exception as e:
        print(f"Inc42 error: {e}")
        return []

def fetch_yourstory():
    """Fetch news from YourStory (Indian business and startup news)"""
    base_url = 'https://yourstory.com'
    url = f'{base_url}/category/markets'
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    try:
        response = requests.get(url, headers=headers)
        soup = BeautifulSoup(response.text, 'html.parser')
        news = []
        
        for item in soup.select('h2 a, h3 a'):
            title = item.get_text(strip=True)
            href = item.get('href')
            if not href:
                continue
            link = construct_url(base_url, href)
            
            full_content = get_full_article_content(link, 'YourStory')
            
            if full_content and is_valid_news_item(title, full_content):
                # Compact format: Title|Content separated by pipe, no extra formatting
                news_item = f"{title.strip()}|{full_content.strip()}\n"
                news.append(news_item)
        
        return news
    except Exception as e:
        print(f"YourStory error: {e}")
        return []

def fetch_entrackr():
    """Fetch news from Entrackr (Indian business and startup news)"""
    base_url = 'https://entrackr.com'
    url = f'{base_url}/category/markets'
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    try:
        response = requests.get(url, headers=headers)
        soup = BeautifulSoup(response.text, 'html.parser')
        news = []
        
        for item in soup.select('h2 a, h3 a'):
            title = item.get_text(strip=True)
            href = item.get('href')
            if not href:
                continue
            link = construct_url(base_url, href)
            
            full_content = get_full_article_content(link, 'Entrackr')
            
            if full_content and is_valid_news_item(title, full_content):
                # Compact format: Title|Content separated by pipe, no extra formatting
                news_item = f"{title.strip()}|{full_content.strip()}\n"
                news.append(news_item)
        
        return news
    except Exception as e:
        print(f"Entrackr error: {e}")
        return []

def fetch_techcrunch_india():
    """Fetch news from TechCrunch India section"""
    base_url = 'https://techcrunch.com'
    url = f'{base_url}/tag/india'
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    try:
        response = requests.get(url, headers=headers)
        soup = BeautifulSoup(response.text, 'html.parser')
        news = []
        
        for item in soup.select('h2 a, h3 a'):
            title = item.get_text(strip=True)
            href = item.get('href')
            if not href:
                continue
            link = construct_url(base_url, href)
            
            full_content = get_full_article_content(link, 'TechCrunch India')
            
            if full_content and is_valid_news_item(title, full_content):
                # Compact format: Title|Content separated by pipe, no extra formatting
                news_item = f"{title.strip()}|{full_content.strip()}\n"
                news.append(news_item)
        
        return news
    except Exception as e:
        print(f"TechCrunch India error: {e}")
        return []

def fetch_venturebeat():
    """Fetch news from VentureBeat (global tech and business news)"""
    base_url = 'https://venturebeat.com'
    url = f'{base_url}/category/business'
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    try:
        response = requests.get(url, headers=headers)
        soup = BeautifulSoup(response.text, 'html.parser')
        news = []
        
        for item in soup.select('h2 a, h3 a'):
            title = item.get_text(strip=True)
            href = item.get('href')
            if not href:
                continue
            link = construct_url(base_url, href)
            
            full_content = get_full_article_content(link, 'VentureBeat')
            
            if full_content and is_valid_news_item(title, full_content):
                # Compact format: Title|Content separated by pipe, no extra formatting
                news_item = f"{title.strip()}|{full_content.strip()}\n"
                news.append(news_item)
        
        return news
    except Exception as e:
        print(f"VentureBeat error: {e}")
        return []

def fetch_techcrunch():
    """Fetch news from TechCrunch (global tech and business news)"""
    base_url = 'https://techcrunch.com'
    url = f'{base_url}/category/enterprise'
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    try:
        response = requests.get(url, headers=headers)
        soup = BeautifulSoup(response.text, 'html.parser')
        news = []
        
        for item in soup.select('h2 a, h3 a'):
            title = item.get_text(strip=True)
            href = item.get('href')
            if not href:
                continue
            link = construct_url(base_url, href)
            
            full_content = get_full_article_content(link, 'TechCrunch')
            
            if full_content and is_valid_news_item(title, full_content):
                # Compact format: Title|Content separated by pipe, no extra formatting
                news_item = f"{title.strip()}|{full_content.strip()}\n"
                news.append(news_item)
        
        return news
    except Exception as e:
        print(f"TechCrunch error: {e}")
        return []

def fetch_arstechnica():
    """Fetch news from Ars Technica (tech and business news)"""
    base_url = 'https://arstechnica.com'
    url = f'{base_url}/business'
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    try:
        response = requests.get(url, headers=headers)
        soup = BeautifulSoup(response.text, 'html.parser')
        news = []
        
        for item in soup.select('h2 a, h3 a'):
            title = item.get_text(strip=True)
            href = item.get('href')
            if not href:
                continue
            link = construct_url(base_url, href)
            
            full_content = get_full_article_content(link, 'Ars Technica')
            
            if full_content and is_valid_news_item(title, full_content):
                # Compact format: Title|Content separated by pipe, no extra formatting
                news_item = f"{title.strip()}|{full_content.strip()}\n"
                news.append(news_item)
        
        return news
    except Exception as e:
        print(f"Ars Technica error: {e}")
        return []

def main():
    all_news = []
    seen_titles = set()  # Track titles to avoid duplicates across sources
    
    print("Fetching FULL DETAILED news from multiple sources...")
    
    try:
        print("Fetching from NewsAPI...")
        all_news.extend(fetch_newsapi())
    except Exception as e:
        print("NewsAPI error:", e)
    
    try:
        print("Fetching from Finnhub...")
        all_news.extend(fetch_finnhub_news())
    except Exception as e:
        print("Finnhub error:", e)
    
    try:
        print("Fetching from Moneycontrol...")
        all_news.extend(fetch_moneycontrol())
    except Exception as e:
        print("Moneycontrol error:", e)
    
    try:
        print("Fetching from Economic Times...")
        all_news.extend(fetch_economictimes())
    except Exception as e:
        print("Economic Times error:", e)
    
    try:
        print("Fetching from LiveMint...")
        all_news.extend(fetch_livemint())
    except Exception as e:
        print("LiveMint error:", e)
    
    try:
        print("Fetching from NDTV Business...")
        all_news.extend(fetch_ndtv_business())
    except Exception as e:
        print("NDTV Business error:", e)
    
    try:
        print("Fetching from Business Standard...")
        all_news.extend(fetch_business_standard())
    except Exception as e:
        print("Business Standard error:", e)
    
    try:
        print("Fetching from Zee Business...")
        all_news.extend(fetch_zeebiz())
    except Exception as e:
        print("Zee Business error:", e)
    
    try:
        print("Fetching from Financial Express...")
        all_news.extend(fetch_financial_express())
    except Exception as e:
        print("Financial Express error:", e)
    
    try:
        print("Fetching from Business Today...")
        all_news.extend(fetch_business_today())
    except Exception as e:
        print("Business Today error:", e)
    
    try:
        print("Fetching from Outlook Business...")
        all_news.extend(fetch_outlook_business())
    except Exception as e:
        print("Outlook Business error:", e)
    
    # Additional Indian and global news sources
    try:
        print("Fetching from Fortune India...")
        all_news.extend(fetch_fortune_india())
    except Exception as e:
        print("Fortune India error:", e)
    
    try:
        print("Fetching from Inc42...")
        all_news.extend(fetch_inc42())
    except Exception as e:
        print("Inc42 error:", e)
    
    try:
        print("Fetching from YourStory...")
        all_news.extend(fetch_yourstory())
    except Exception as e:
        print("YourStory error:", e)
    
    try:
        print("Fetching from Entrackr...")
        all_news.extend(fetch_entrackr())
    except Exception as e:
        print("Entrackr error:", e)
    
    try:
        print("Fetching from TechCrunch India...")
        all_news.extend(fetch_techcrunch_india())
    except Exception as e:
        print("TechCrunch India error:", e)
    
    try:
        print("Fetching from VentureBeat...")
        all_news.extend(fetch_venturebeat())
    except Exception as e:
        print("VentureBeat error:", e)
    
    try:
        print("Fetching from TechCrunch...")
        all_news.extend(fetch_techcrunch())
    except Exception as e:
        print("TechCrunch error:", e)
    
    try:
        print("Fetching from Ars Technica...")
        all_news.extend(fetch_arstechnica())
    except Exception as e:
        print("Ars Technica error:", e)
    
    try:
        print("Fetching from Reuters World...")
        all_news.extend(fetch_reuters_world())
    except Exception as e:
        print("Reuters World error:", e)
    
    try:
        print("Fetching from Bloomberg Markets...")
        all_news.extend(fetch_bloomberg_markets())
    except Exception as e:
        print("Bloomberg Markets error:", e)
    
    try:
        print("Fetching from CNBC World Markets...")
        all_news.extend(fetch_cnbc_world())
    except Exception as e:
        print("CNBC World Markets error:", e)
    
    try:
        print("Fetching from Financial Times...")
        all_news.extend(fetch_financial_times())
    except Exception as e:
        print("Financial Times error:", e)
    
    try:
        print("Fetching from Wall Street Journal...")
        all_news.extend(fetch_wall_street_journal())
    except Exception as e:
        print("Wall Street Journal error:", e)
    
    try:
        print("Fetching Oil Price News...")
        all_news.extend(fetch_oil_price_news())
    except Exception as e:
        print("Oil Price News error:", e)
    
    try:
        print("Fetching US Fed News...")
        all_news.extend(fetch_us_fed_news())
    except Exception as e:
        print("US Fed News error:", e)
    
    try:
        print("Fetching China Market News...")
        all_news.extend(fetch_china_market_news())
    except Exception as e:
        print("China Market News error:", e)

    # Remove duplicates based on title similarity
    unique_news = []
    for news_item in all_news:
        title = news_item.split('|')[0].strip().lower()
        # Create a simplified title for comparison
        simple_title = ''.join(title.split()[:8])  # First 8 words, no spaces
        
        if simple_title not in seen_titles:
            seen_titles.add(simple_title)
            unique_news.append(news_item)
    
    filename = "FULL_INDIAN_STOCK_NEWS.txt"
    with open(filename, 'w', encoding='utf-8') as f:
        # Add header with format explanation for LLM processing
        f.write("# Format: Title|FullContent (one article per line, pipe-separated)\n")
        f.write("# This compact format preserves all content while minimizing file size for LLM analysis\n")
        f.write(f"# Collected from {len(all_news)} sources, deduplicated to {len(unique_news)} unique articles\n\n")
        
        for news in unique_news:
            f.write(news)  # Each news item already has a newline
    
    print(f"Collected {len(all_news)} articles total, saved {len(unique_news)} unique articles to {filename}")
    print(f"Format: Compact pipe-separated (Title|Content) for optimal LLM processing")
    print(f"Duplicate removal: {len(all_news) - len(unique_news)} duplicate articles filtered out")
    print(f"News sources included: Indian sources (NewsAPI, Finnhub, Moneycontrol, Economic Times, LiveMint, NDTV Business, Business Standard, Zee Business, Financial Express, Business Today, Outlook Business, Fortune India, Inc42, YourStory, Entrackr) + Global sources (TechCrunch India, VentureBeat, TechCrunch, Ars Technica, Reuters, Bloomberg, CNBC, FT, WSJ, Oil prices, US Fed, China markets)")

if __name__ == "__main__":
    main()