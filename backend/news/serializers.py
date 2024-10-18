from rest_framework import serializers
from .models import NewsOutlet, Author, AuthorOutletAssociation, Event, Article, ArticleFact, EventFact, EventFactSource

class NewsOutletSerializer(serializers.ModelSerializer):
    name = serializers.CharField()
    url = serializers.CharField(required=False, allow_blank=True)
    icon = serializers.CharField(required=False, allow_blank=True)

    class Meta:
        model = NewsOutlet
        fields = ['id', 'name', 'url', 'icon']

    def to_representation(self, instance):
        if isinstance(instance, str):
            return {'name': instance, 'url': '', 'icon': ''}
        return super().to_representation(instance)

class AuthorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Author
        fields = ['id', 'name', 'bio', 'profile_picture']

class AuthorOutletAssociationSerializer(serializers.ModelSerializer):
    class Meta:
        model = AuthorOutletAssociation
        fields = '__all__'

class ArticleSerializer(serializers.ModelSerializer):
    author = AuthorSerializer(read_only=True)
    site = NewsOutletSerializer(read_only=True)

    class Meta:
        model = Article
        fields = ['id', 'title', 'url', 'published_time', 'modified_time', 'author', 'site', 'article_text']

class ArticleFactSerializer(serializers.ModelSerializer):
    article = ArticleSerializer(read_only=True)

    class Meta:
        model = ArticleFact
        fields = ['id', 'content', 'newsworthiness', 'article']

class EventFactSourceSerializer(serializers.ModelSerializer):
    article_fact = ArticleFactSerializer(read_only=True)

    class Meta:
        model = EventFactSource
        fields = ['id', 'contribution_weight', 'article_fact']

class EventFactSerializer(serializers.ModelSerializer):
    sources = EventFactSourceSerializer(many=True, read_only=True)

    class Meta:
        model = EventFact
        fields = ['id', 'content', 'newsworthiness', 'sources']

class EventSerializer(serializers.ModelSerializer):
    facts = EventFactSerializer(many=True, read_only=True)

    class Meta:
        model = Event
        fields = ['id', 'title', 'created_at', 'facts']
