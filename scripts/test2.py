from datetime import datetime, timedelta
import pytz
from scrape_cnn import *
from text2facts import *

if __name__ == "__main__":
    end_datetime = datetime.now(pytz.utc)
    start_datetime = end_datetime - timedelta(hours=1)
    
    sitemaps = parse_cnn(start_datetime,end_datetime)
    urls = parse_sitemap_cnn(sitemaps[0][1],start_datetime,end_datetime)
    article = read_cnn_article(urls[0])
    print(article[0])
    facts = text2facts(article[4])
    print(facts)
