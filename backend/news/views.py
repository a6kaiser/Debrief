from rest_framework import viewsets
from .models import NewsOutlet, Author, AuthorOutletAssociation, Event, Article, ArticleFact, EventFact, EventFactSource
from .serializers import NewsOutletSerializer, AuthorSerializer, AuthorOutletAssociationSerializer, EventSerializer, ArticleSerializer, ArticleFactSerializer, EventFactSerializer, EventFactSourceSerializer

class NewsOutletViewSet(viewsets.ModelViewSet):
    queryset = NewsOutlet.objects.all()
    serializer_class = NewsOutletSerializer

class AuthorViewSet(viewsets.ModelViewSet):
    queryset = Author.objects.all()
    serializer_class = AuthorSerializer

class AuthorOutletAssociationViewSet(viewsets.ModelViewSet):
    queryset = AuthorOutletAssociation.objects.all()
    serializer_class = AuthorOutletAssociationSerializer

class EventViewSet(viewsets.ModelViewSet):
    queryset = Event.objects.all()
    serializer_class = EventSerializer

class ArticleViewSet(viewsets.ModelViewSet):
    queryset = Article.objects.all()
    serializer_class = ArticleSerializer

class ArticleFactViewSet(viewsets.ModelViewSet):
    queryset = ArticleFact.objects.all()
    serializer_class = ArticleFactSerializer

class EventFactViewSet(viewsets.ModelViewSet):
    queryset = EventFact.objects.all()
    serializer_class = EventFactSerializer

class EventFactSourceViewSet(viewsets.ModelViewSet):
    queryset = EventFactSource.objects.all()
    serializer_class = EventFactSourceSerializer
