from django.core.management.base import BaseCommand
from django.utils import timezone
from news.models import NewsOutlet, Article, ArticleFact, Event, EventFact, EventFactSource, Author, ScrapingLog
from scripts.scrape_cnn import parse_cnn, parse_sitemap_cnn
from scripts.scrape_urls import fetch_metadata_and_article
from datetime import datetime, date
import csv
import os

class Command(BaseCommand):
    help = 'Scrapes CNN articles from a specific date range and saves them to the database'

    def add_arguments(self, parser):
        parser.add_argument('--start_date', type=str, help='Start date for scraping (YYYY-MM-DD)')
        parser.add_argument('--end_date', type=str, help='End date for scraping (YYYY-MM-DD)')
        parser.add_argument('--csv_file', type=str, default='cnn_urls.csv', help='CSV file with URLs')
        parser.add_argument('--checkpoint_file', type=str, default='cnn_progress_checkpoint.txt', help='Checkpoint file')

    def handle(self, *args, **options):
        start_date = datetime.strptime(options['start_date'] or '2024-10-01', '%Y-%m-%d')
        end_date = datetime.strptime(options['end_date'] or date.today().isoformat(), '%Y-%m-%d')
        csv_file = options['csv_file']
        checkpoint_file = options['checkpoint_file']

        cnn_outlet, _ = NewsOutlet.objects.get_or_create(
            name='CNN',
            defaults={'url': 'https://www.cnn.com'}
        )

        self.collect_urls(start_date, end_date, csv_file)
        self.process_urls(csv_file, checkpoint_file, cnn_outlet, start_date, end_date)

        self.stdout.write(self.style.SUCCESS(f'Successfully scraped CNN articles from {start_date} to {end_date}'))

    def collect_urls(self, start_date, end_date, csv_file):
        self.stdout.write("Collecting URLs...")
        urls = []
        sitemap_entries = parse_cnn(start_date.year)
        for entry in sitemap_entries:
            category, year, month = entry
            entry_date = date(year, month, 1)
            if start_date.date() <= entry_date <= end_date.date():
                self.stdout.write(f"Processing Category: {category}, Year: {year}, Month: {month}")
                sitemap_urls = parse_sitemap_cnn(category, year, month)
                for url, lastmod in sitemap_urls:
                    if start_date <= lastmod <= end_date:
                        urls.append((url, category, lastmod))

        with open(csv_file, 'w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(['site', 'category', 'url', 'lastmod'])
            for url, category, lastmod in urls:
                writer.writerow(['cnn', category, url, lastmod.isoformat()])

    def process_urls(self, csv_file, checkpoint_file, outlet, start_date, end_date):
        self.stdout.write("Processing URLs...")
        last_checkpoint = self.read_last_checkpoint(checkpoint_file)
        self.stdout.write(f"Resuming from row {last_checkpoint}...")

        with open(csv_file, 'r') as file:
            reader = csv.DictReader(file)
            for row_count, row in enumerate(reader, start=1):
                if row_count <= last_checkpoint:
                    continue

                url = row['url'].strip()
                category = row['category']
                lastmod = datetime.fromisoformat(row['lastmod'])

                self.stdout.write(f"Processing {row_count} - {url}")
                title, published_time, modified_time, author_name, article_text = fetch_metadata_and_article(url)

                if title and article_text:
                    # Create or get Author
                    author, _ = Author.objects.get_or_create(name=author_name) if author_name else (None, None)

                    # Create Article
                    article, created = Article.objects.get_or_create(
                        url=url,
                        defaults={
                            'site': outlet.name,
                            'title': title,
                            'published_time': published_time or lastmod,
                            'modified_time': modified_time or lastmod,
                            'article_text': article_text,
                        }
                    )
                    if author:
                        article.authors.add(author)

                    if created:
                        # Create Event
                        event = Event.objects.create(
                            title=article.title,
                            created_at=article.published_time
                        )

                        # Create ArticleFacts and EventFacts
                        for paragraph in article_text.split('\n'):
                            if paragraph.strip():
                                article_fact = ArticleFact.objects.create(
                                    article=article,
                                    content=paragraph,
                                    newsworthiness=len(paragraph) / 100
                                )
                                event_fact = EventFact.objects.create(
                                    event=event,
                                    content=paragraph,
                                    newsworthiness=article_fact.newsworthiness
                                )
                                EventFactSource.objects.create(
                                    event_fact=event_fact,
                                    article_fact=article_fact,
                                    contribution_weight=1.0
                                )

                self.write_checkpoint(checkpoint_file, row_count)

        # Update ScrapingLog
        ScrapingLog.objects.update_or_create(
            outlet=outlet,
            defaults={
                'start_date': start_date.date(),
                'end_date': end_date.date(),
                'last_scraped': timezone.now()
            }
        )

    def read_last_checkpoint(self, checkpoint_file):
        if os.path.exists(checkpoint_file):
            with open(checkpoint_file, 'r') as f:
                return int(f.read().strip())
        return 0

    def write_checkpoint(self, checkpoint_file, row_count):
        with open(checkpoint_file, 'w') as f:
            f.write(str(row_count))
