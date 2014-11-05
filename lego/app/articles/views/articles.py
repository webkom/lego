from rest_framework import viewsets

from lego.app.articles.models import Article
from lego.app.articles.serializers import ArticleSerializer

class ArticlesViewSet(viewsets.ModelViewSet):
    queryset = Article.get.all()
    serializer_class = ArticleSerializer
