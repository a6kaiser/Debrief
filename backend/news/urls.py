from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import NewsOutletViewSet, AuthorViewSet, AuthorOutletAssociationViewSet, EventViewSet, ArticleViewSet, ArticleFactViewSet, EventFactViewSet, EventFactSourceViewSet

router = DefaultRouter()
router.register(r'news-outlets', NewsOutletViewSet)
router.register(r'authors', AuthorViewSet)
router.register(r'author-outlet-associations', AuthorOutletAssociationViewSet)
router.register(r'events', EventViewSet)
router.register(r'articles', ArticleViewSet)
router.register(r'article-facts', ArticleFactViewSet)
router.register(r'event-facts', EventFactViewSet)
router.register(r'event-fact-sources', EventFactSourceViewSet)

urlpatterns = router.urls
