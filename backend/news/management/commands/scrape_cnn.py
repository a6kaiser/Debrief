import sys
from pathlib import Path

# Add the project root directory to the Python path
project_root = Path(__file__).resolve().parents[4]
print(f"Project root: {project_root}")
sys.path.append(str(project_root))

# Print the current Python path
print("Python path:")
for path in sys.path:
    print(path)

import os
from django.core.management.base import BaseCommand
from django.utils import timezone
from news.models import NewsOutlet, Article, Author, ScrapingLog
# Try importing with different paths
from scripts.utils_cnn import parse_cnn, parse_sitemap_cnn, read_cnn_article
import pytz

class Command(BaseCommand):
    help = 'Scrapes CNN articles for a specified time range and saves them to the database'

    def add_arguments(self, parser):
        parser.add_argument('--start', type=str, help='Start datetime (ISO format)')
        parser.add_argument('--end', type=str, help='End datetime (ISO format)')

    def handle(self, *args, **options):
        end_datetime = timezone.now()
        
        if options['start'] and options['end']:
            start_datetime = timezone.datetime.fromisoformat(options['start'])
            end_datetime = timezone.datetime.fromisoformat(options['end'])
        else:
            # Get the last scrape end time from the database
            last_scrape = ScrapingLog.objects.filter(site='CNN').order_by('-end_time').first()
            start_datetime = last_scrape.end_time if last_scrape else end_datetime - timezone.timedelta(days=1)

        cnn_outlet, _ = NewsOutlet.objects.get_or_create(
            name='CNN',
            defaults={'url': 'https://www.cnn.com'}
        )

        self.stdout.write(f"Scraping CNN articles from {start_datetime} to {end_datetime}")
        self.scrape_and_store_articles(start_datetime, end_datetime, cnn_outlet)

        # Log the scraping session
        ScrapingLog.objects.create(site='CNN', start_time=start_datetime, end_time=end_datetime)

    def scrape_and_store_articles(self, start_datetime, end_datetime, outlet):
        sitemaps = parse_cnn(start_datetime, end_datetime)
        count = 0
        for category, sitemap_url in sitemaps:
            urls = parse_sitemap_cnn(sitemap_url, start_datetime, end_datetime)
            for url in urls:
                count += 1
                self.process_article(url, category, outlet, count)

    def process_article(self, url, category, outlet, count):
        title, published_time, modified_time, author_name, article_text = read_cnn_article(url)
        self.stdout.write(f"{count}. Processing: {title}")

        if title and article_text:
            # Create or get Author
            author, _ = Author.objects.get_or_create(name=author_name) if author_name else (None, None)

            # Create or update Article
            article, created = Article.objects.update_or_create(
                url=url,
                defaults={
                    'site': outlet.name,  # Use the name of the outlet instead of the instance
                    'category': category,
                    'title': title,
                    'published_time': published_time,
                    'modified_time': modified_time,
                    'article_text': article_text,
                    'author': author,
                }
            )

            if created:
                self.stdout.write(self.style.SUCCESS(f"Created new article: {title}"))
            else:
                self.stdout.write(self.style.WARNING(f"Updated existing article: {title}"))
