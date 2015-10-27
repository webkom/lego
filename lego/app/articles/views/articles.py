from rest_framework import viewsets

from lego.app.articles.models import Article
from lego.app.articles.permissions import ArticlePermissions
from lego.app.articles.serializers import DetailedArticleSerializer, PublicArticleSerializer
from lego.permissions.filters import ObjectPermissionsFilter


class ArticlesViewSet(viewsets.ModelViewSet):
    queryset = Article.objects.all()
    filter_backends = (ObjectPermissionsFilter,)
    permission_classes = (ArticlePermissions,)

    def get_serializer_class(self):
        if self.action == 'list':
            return PublicArticleSerializer

        return DetailedArticleSerializer
