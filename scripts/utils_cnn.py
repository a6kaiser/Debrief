import re
import requests
import time
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from datetime import datetime
import xml.etree.ElementTree as ET
import logging
import pytz

# Set up basic logging configuration
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def read_cnn_article(url):
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'html.parser')

        # Get title
        title = soup.title.string if soup.title else "Title not found"

        # Get publish time
        published_time = None
        published_time_tags = [
            'meta[property="article:published_time"]',
            'meta[name="article:published_time"]',
            'meta[itemprop="datePublished"]'
        ]
        for tag in published_time_tags:
            published_time_meta = soup.select_one(tag)
            if published_time_meta and published_time_meta.get('content'):
                published_time = published_time_meta['content']
                break

        # Get modified time
        modified_time = None
        modified_time_tags = [
            'meta[property="article:modified_time"]',
            'meta[name="article:modified_time"]',
            'meta[itemprop="dateModified"]'
        ]
        for tag in modified_time_tags:
            modified_time_meta = soup.select_one(tag)
            if modified_time_meta and modified_time_meta.get('content'):
                modified_time = modified_time_meta['content']
                break

        # Get author
        author = None
        author_tags = [
            'meta[name="author"]',
            'meta[property="article:author"]',
            'meta[itemprop="author"]'
        ]
        for tag in author_tags:
            author_meta = soup.select_one(tag)
            if author_meta and author_meta.get('content'):
                author = author_meta['content']
                break

        # Extract article text
        article_text = ""
        article_container = soup.find('article')
        if article_container:
            paragraphs = article_container.find_all('p')
            article_text = "\n".join([p.get_text(strip=True) for p in paragraphs])
        else:
            # If no <article> tag is found, fall back to searching for paragraphs in large <div>
            div_container = soup.find('div', {'class': 'article-content'}) or soup.find('div', {'class': 'post-content'})
            if div_container:
                paragraphs = div_container.find_all('p')
                article_text = "\n".join([p.get_text(strip=True) for p in paragraphs])
            else:
                # Fallback to finding all <p> tags in the document
                paragraphs = soup.find_all('p')
                article_text = "\n".join([p.get_text(strip=True) for p in paragraphs])

        return title, published_time, modified_time, author, article_text

    except requests.RequestException as e:
        print(f"Error fetching {url}: {e}")
        return None, None, None, None, None

def parse_sitemap_cnn(sitemap_url, start_datetime=None, end_datetime=None):
    logger.info(f"Parsing sitemap: {sitemap_url}")
    logger.info(f"Date range: {start_datetime} to {end_datetime}")

    try:
        response = requests.get(sitemap_url)
        response.raise_for_status()
    except requests.RequestException as e:
        logger.error(f"Error fetching sitemap {sitemap_url}: {e}")
        return []

    try:
        root = ET.fromstring(response.content)
    except ET.ParseError as e:
        logger.error(f"Error parsing XML from {sitemap_url}: {e}")
        return []

    namespace = {'ns': 'http://www.sitemaps.org/schemas/sitemap/0.9'}
    urls = []
    total_urls = 0
    urls_in_range = 0

    for url_elem in root.findall('ns:url', namespace):
        total_urls += 1
        loc = url_elem.find('ns:loc', namespace)
        lastmod = url_elem.find('ns:lastmod', namespace)
        
        if loc is not None and lastmod is not None:
            url = loc.text
            date_str = lastmod.text
            try:
                article_datetime = datetime.fromisoformat(date_str.rstrip('Z')).replace(tzinfo=pytz.UTC)
                
                if start_datetime and article_datetime < start_datetime:
                    logger.debug(f"Skipping {url}: {article_datetime} is before start_datetime")
                    continue
                if end_datetime and article_datetime > end_datetime:
                    logger.debug(f"Skipping {url}: {article_datetime} is after end_datetime")
                    continue
                
                urls.append(url)
                urls_in_range += 1
            except ValueError as e:
                logger.warning(f"Error parsing date {date_str} for URL {url}: {e}")
        else:
            logger.warning(f"Missing loc or lastmod for an entry in {sitemap_url}")

    logger.info(f"Sitemap {sitemap_url} summary:")
    logger.info(f"  Total URLs found: {total_urls}")
    logger.info(f"  URLs within date range: {urls_in_range}")
    
    if urls_in_range == 0:
        logger.warning(f"No URLs found within the specified date range in {sitemap_url}")
        logger.debug(f"First few dates in sitemap: {[url_elem.find('ns:lastmod', namespace).text for url_elem in root.findall('ns:url', namespace)[:5]]}")

    return urls

def parse_cnn(start_datetime=None, end_datetime=None):
    main_sitemap = "https://www.cnn.com/sitemap/article.xml"
    logger.info(f"Parsing main sitemap: {main_sitemap}")
    logger.info(f"Date range: {start_datetime} to {end_datetime}")

    try:
        response = requests.get(main_sitemap)
        response.raise_for_status()
    except requests.RequestException as e:
        logger.error(f"Error fetching main sitemap {main_sitemap}: {e}")
        return []

    try:
        root = ET.fromstring(response.content)
    except ET.ParseError as e:
        logger.error(f"Error parsing XML from {main_sitemap}: {e}")
        return []

    namespace = {'ns': 'http://www.sitemaps.org/schemas/sitemap/0.9'}
    filtered_pairs = []
    total_sitemaps = 0
    sitemaps_in_range = 0

    for sitemap in root.findall('ns:sitemap', namespace):
        total_sitemaps += 1
        loc = sitemap.find('ns:loc', namespace)
        lastmod = sitemap.find('ns:lastmod', namespace)
        
        if loc is not None and lastmod is not None:
            url = loc.text
            date_str = lastmod.text
            try:
                lastmod_date = datetime.fromisoformat(date_str.rstrip('Z')).replace(tzinfo=pytz.UTC)
                
                if end_datetime and lastmod_date > end_datetime:
                    logger.debug(f"Skipping {url}: {lastmod_date} is after end_datetime")
                    continue
                if start_datetime and lastmod_date < start_datetime:
                    logger.debug(f"Skipping {url}: {lastmod_date} is before start_datetime")
                    break  # Since it's sorted most recent first, we can stop once we're before the start date

                category = url.split('/')[5] if len(url.split('/')) > 5 else 'unknown'
                filtered_pairs.append((category, url))
                sitemaps_in_range += 1
                logger.debug(f"Including sitemap: {category} - {url}")
            except ValueError as e:
                logger.warning(f"Error parsing date {date_str} for sitemap {url}: {e}")
        else:
            logger.warning(f"Missing loc or lastmod for a sitemap in {main_sitemap}")

    logger.info(f"Main sitemap summary:")
    logger.info(f"  Total sitemaps found: {total_sitemaps}")
    logger.info(f"  Sitemaps within date range: {sitemaps_in_range}")

    return filtered_pairs

def main():
    # Parse and sort the sitemap dates
    sitemap_entries = parse_cnn(2024)
    print(sitemap_entries)

    # Dictionary to store articles by category
    articles = {}
    all_urls = []
    all_cats = []

    for entry in sitemap_entries:
        category, year, month = entry
        print(f"Processing Category: {category}, Year: {year}, Month: {month}")
        urls = parse_sitemap_cnn(category, year, month)
        print(f"Found {len(urls)} articles in {category} for {year}-{month:02d}")
        all_urls += urls
        all_cats += [category]*len(urls)
        """
        for url in urls:
            article_text = read_cnn(url)
            if article_text:
                if category not in articles:
                    articles[category] = []
                articles[category].append({
                    'url': url,
                    'content': article_text
                })
        """

    with open("last_urls.csv",'w') as file:
        file.write("site,category,url\n")
        for i,url in enumerate(all_urls):
            file.write(f"cnn,{all_cats[i]},{url}\n")
    # Example of how to store the articles
    # Here we simply print the number of articles collected per category
    #for category, articles_list in articles.items():
    #    print(f"Category: {category} - {len(articles_list)} articles collected.")

    # You can extend this part to save articles to a file or database as needed.

# This allows the script to be run standalone for testing
if __name__ == "__main__":
    from datetime import timedelta
    
    # Set logging level to DEBUG for more detailed output
    logging.getLogger().setLevel(logging.DEBUG)
    
    # Example usage
    end = datetime.now(pytz.UTC)
    start = end - timedelta(days=1)  # Last 24 hours
    results = parse_cnn(start, end)
    
    print(f"Found {len(results)} sitemaps in the last 24 hours:")
    for category, url in results[:5]:  # Print first 5 for brevity
        print(f"Category: {category}, URL: {url}")
        sitemap_urls = parse_sitemap_cnn(url, start, end)
        print(f"  Found {len(sitemap_urls)} articles in this sitemap")
        for article_url in sitemap_urls[:3]:  # Print first 3 article URLs for each sitemap
            print(f"    {article_url}")
    if len(results) > 5:
        print("...")