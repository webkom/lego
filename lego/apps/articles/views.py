from rest_framework import viewsets

from lego.apps.articles.models import Article
from lego.apps.articles.serializers import DetailedArticleSerializer, PublicArticleSerializer
from lego.apps.permissions.views import AllowedPermissionsMixin


class ArticlesViewSet(AllowedPermissionsMixin, viewsets.ModelViewSet):
    queryset = Article.objects.all()

    def get_queryset(self):
        if self.action == 'list':
            return self.queryset
        return self.queryset.prefetch_related('author', 'comments', 'comments__created_by',
                                              'reactions', 'reactions__created_by', 'tags')

    def get_serializer_class(self):
        if self.action == 'list':
            return PublicArticleSerializer

        return DetailedArticleSerializer
