from django.core.management.base import BaseCommand
from news.models import Event, Article, ArticleFact, EventFact, EventFactSource, Author, NewsOutlet
from django.utils import timezone
import random

class Command(BaseCommand):
    help = 'Adds dummy events and related data to the database'

    def handle(self, *args, **kwargs):
        # Clear existing data
        self.stdout.write('Clearing existing data...')
        Event.objects.all().delete()
        Article.objects.all().delete()
        ArticleFact.objects.all().delete()
        EventFact.objects.all().delete()
        EventFactSource.objects.all().delete()
        Author.objects.all().delete()
        NewsOutlet.objects.all().delete()

        # Create dummy news outlets
        outlets = []
        for i in range(5):
            outlet = NewsOutlet.objects.create(
                name=f"News Outlet {i+1}",
                url=f"https://newsoutlet{i+1}.com"
            )
            outlets.append(outlet)

        # Create dummy authors
        authors = []
        for i in range(10):
            author = Author.objects.create(
                name=f"Author {i+1}",
                bio=f"Bio for Author {i+1}"
            )
            authors.append(author)

        # Create dummy events
        for i in range(5):
            event = Event.objects.create(
                title=f"Dummy Event {i+1}"
            )

            # Create 3-6 event facts for each event
            for j in range(random.randint(3, 6)):
                event_fact = EventFact.objects.create(
                    event=event,
                    content=f"Fact {j+1} for Event {i+1}",
                    newsworthiness=random.uniform(0, 10)
                )

                # Create 2-4 articles for each event fact
                for k in range(random.randint(2, 4)):
                    article = Article.objects.create(
                        site=random.choice(outlets).name,
                        category="General",
                        url=f"https://newssite{k+1}.com/article{random.randint(1,1000)}",
                        title=f"Article {k+1} about Fact {j+1} of Event {i+1}",
                        published_time=timezone.now(),
                        modified_time=timezone.now(),
                        author=random.choice(authors),
                        article_text=f"This is the content of article {k+1} about fact {j+1} of event {i+1}."
                    )

                    article_fact = ArticleFact.objects.create(
                        article=article,
                        content=f"Article fact for {article.title}",
                        newsworthiness=random.uniform(0, 10)
                    )

                    EventFactSource.objects.create(
                        event_fact=event_fact,
                        article_fact=article_fact,
                        contribution_weight=random.uniform(0.1, 1.0)
                    )

        self.stdout.write(self.style.SUCCESS('Successfully added dummy events and related data'))
