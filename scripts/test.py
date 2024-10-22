from datetime import datetime, timedelta
import pytz
from scrape_cnn import *
from text2facts import *

if __name__ == "__main__":
    end_datetime = datetime.now(pytz.utc)
    start_datetime = end_datetime - timedelta(hours=1)
    
    sitemaps = parse_cnn(start_datetime,end_datetime)
    count = 0
    for (category,sitemap_url) in sitemaps:
        urls = parse_sitemap_cnn(sitemap_url,start_datetime,end_datetime)
        for url in urls:
            count += 1
            article = read_cnn_article(url)
            print(count,article[0])
