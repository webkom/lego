from rest_framework import viewsets

from lego.apps.articles.filters import ArticleFilterSet
from lego.apps.articles.models import Article
from lego.apps.articles.serializers import (
    DetailedArticleAdminSerializer,
    DetailedArticleSerializer,
    PublicArticleSerializer,
)
from lego.apps.permissions.api.views import AllowedPermissionsMixin
from lego.apps.permissions.constants import OBJECT_PERMISSIONS_FIELDS


class ArticlesViewSet(AllowedPermissionsMixin, viewsets.ModelViewSet):
    queryset = Article.objects.all()
    ordering = "-created_at"
    serializer_class = DetailedArticleSerializer
    filterset_class = ArticleFilterSet

    def get_queryset(self):
        queryset = self.queryset.select_related("created_by").prefetch_related("tags")

        if self.action == "list":
            return queryset

        return queryset.prefetch_related(
            "comments", "comments__created_by", *OBJECT_PERMISSIONS_FIELDS
        )

    def get_serializer_class(self):
        if self.action == "list":
            return PublicArticleSerializer
        if self.request and self.request.user.is_authenticated:
            return DetailedArticleAdminSerializer

        return super().get_serializer_class()
