import re
import requests
import time
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from datetime import datetime
import xml.etree.ElementTree as ET

def read_cnn(url):
    """
    To read a CNN article, look for the article container
    Avoid a paragraph block that has a class name including "ad"
    Return the text of the article
    """
    try:
        response = requests.get(url)
        response.raise_for_status()  # Raise an error for bad status codes
    except requests.RequestException as e:
        print(f"Error fetching {url}: {e}")
        return ""

    soup = BeautifulSoup(response.text, 'html.parser')

    # CNN articles typically have their content within specific containers.
    # This may vary, so adjust the selector as needed.
    # Common containers include 'div' with class 'l-container' or 'pg-rail-tall__body'
    article_containers = soup.find_all('div', class_=re.compile(r'l-container|pg-rail-tall__body'))

    article_text = []
    for container in article_containers:
        paragraphs = container.find_all('p')
        for p in paragraphs:
            # Skip paragraphs with class names that include "ad"
            if p.get('class') and any('ad' in cls for cls in p.get('class')):
                continue
            article_text.append(p.get_text())

    return '\n'.join(article_text)

def parse_sitemap_cnn(category, year, month):
    """
    CNN has sitemaps that group articles by category. Read the URL
    f"https://www.cnn.com/sitemap/article/{category}/{year}/{month}.xml"
    Extract the url and lastmod for every article written in that month.
    Return the list of tuples (url, datetime)
    """
    sitemap_url = f"https://www.cnn.com/sitemap/article/{category}/{year}/{month:02d}.xml"
    try:
        response = requests.get(sitemap_url)
        response.raise_for_status()
    except requests.RequestException as e:
        print(f"Error fetching sitemap {sitemap_url}: {e}")
        return []

    # Parse XML sitemap
    try:
        root = ET.fromstring(response.content)
    except ET.ParseError as e:
        print(f"Error parsing XML from {sitemap_url}: {e}")
        return []

    namespace = {'ns': 'http://www.sitemaps.org/schemas/sitemap/0.9'}
    urls_with_dates = []
    pattern = re.compile(r"(https://\S*?index\.html)$")
    
    for url in root.findall('ns:url', namespace):
        loc = url.find('ns:loc', namespace)
        lastmod = url.find('ns:lastmod', namespace)
        if loc is not None and lastmod is not None:
            url_text = loc.text
            date_text = lastmod.text
            match = pattern.search(url_text)
            if match:
                urls_with_dates.append((match.group(1), datetime.fromisoformat(date_text)))

    return urls_with_dates

def parse_cnn(cutoff=0):
    """
    Fetches the CNN sitemap at "https://www.cnn.com/sitemap/article.xml".
    Uses a regex pattern to extract categories, years, and months from the sitemap URLs.
    Sorts the results by date (earliest to latest).

    Returns:
        A sorted list of tuples: (category, year, month)
    """
    main_sitemap = "https://www.cnn.com/sitemap/article.xml"

    try:
        response = requests.get(main_sitemap)
        response.raise_for_status()
    except requests.RequestException as e:
        print(f"Error fetching main sitemap {main_sitemap}: {e}")
        return []

    # Use regex to find all matches of the sitemap article URLs
    pattern = re.compile(r"https://www\.cnn\.com/sitemap/article/(\S+?)/(\d{4})/(\d{2})\.xml")

    # Extract all matches from the text of the sitemap
    matches = pattern.findall(response.text)

    # Print out each match and collect them in a list
    parsed_matches = []
    for match in matches:
        category, year, month = match
        if int(year) < cutoff: continue
        print(f"Category: {category}, Year: {year}, Month: {month}")
        parsed_matches.append((category, int(year), int(month)))

    # Sort the matches by date (earliest to latest)
    matches_sorted = sorted(parsed_matches, key=lambda x: datetime(x[1], x[2], 1), reverse=True)

    return matches_sorted

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

if __name__ == "__main__":
    main()
