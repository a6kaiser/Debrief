from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class NewsOutlet(models.Model):
    name = models.CharField(max_length=100)
    url = models.URLField()
    icon = models.ImageField(upload_to='news_outlet_icons/', null=True, blank=True)

    def __str__(self):
        return self.name

class Author(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True)
    name = models.CharField(max_length=100)
    bio = models.TextField(blank=True)
    profile_picture = models.ImageField(upload_to='author_profiles/', null=True, blank=True)

    def __str__(self):
        return self.name

class AuthorOutletAssociation(models.Model):
    author = models.ForeignKey(Author, related_name='outlet_associations', on_delete=models.CASCADE)
    outlet = models.ForeignKey(NewsOutlet, related_name='author_associations', on_delete=models.CASCADE)
    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)
    role = models.CharField(max_length=100, blank=True)

    def __str__(self):
        return f"{self.author} at {self.outlet} ({self.role})"

class Event(models.Model):
    title = models.CharField(max_length=200)
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.title

class Article(models.Model):
    site = models.CharField(max_length=200)
    category = models.CharField(max_length=100)
    url = models.URLField(unique=True)
    title = models.CharField(max_length=200)
    published_time = models.DateTimeField()
    modified_time = models.DateTimeField()
    author = models.ForeignKey(Author, related_name='articles', on_delete=models.SET_NULL, null=True)
    article_text = models.TextField()

    def __str__(self):
        return self.title

class ArticleFact(models.Model):
    article = models.ForeignKey(Article, related_name='facts', on_delete=models.CASCADE)
    content = models.TextField()
    newsworthiness = models.FloatField()

    def __str__(self):
        return f"Fact from {self.article.title}"

class EventFact(models.Model):
    event = models.ForeignKey(Event, related_name='facts', on_delete=models.CASCADE)
    content = models.TextField()
    newsworthiness = models.FloatField()

    def __str__(self):
        return f"Fact about {self.event.title}"

class EventFactSource(models.Model):
    event_fact = models.ForeignKey(EventFact, related_name='sources', on_delete=models.CASCADE)
    article_fact = models.ForeignKey(ArticleFact, on_delete=models.CASCADE)
    contribution_weight = models.FloatField(default=1.0)

    def __str__(self):
        return f"Source for fact about {self.event_fact.event.title}"
