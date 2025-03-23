from django.http import Http404
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.exceptions import NotAuthenticated, PermissionDenied
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from lego.apps.articles.filters import ArticleFilterSet
from lego.apps.articles.models import Article
from lego.apps.articles.serializers import (
    DetailedArticleAdminSerializer,
    DetailedArticleSerializer,
    PublicArticleSerializer,
)
from lego.apps.permissions.api.views import AllowedPermissionsMixin
from lego.apps.permissions.constants import OBJECT_PERMISSIONS_FIELDS
from lego.apps.permissions.utils import get_permission_handler
from lego.utils.functions import request_plausible_statistics


class ArticlesViewSet(AllowedPermissionsMixin, ModelViewSet):
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

    def get_object(self) -> Article:
        queryset = self.get_queryset()
        pk = self.kwargs.get("pk")

        try:
            obj = queryset.get(id=pk)
        except (TypeError, OverflowError, Article.DoesNotExist, ValueError):
            obj = get_object_or_404(queryset, slug=pk)

        try:
            self.check_object_permissions(self.request, obj)
        except (NotAuthenticated, PermissionDenied) as e:
            raise Http404 from e
        return obj

    @action(detail=True, methods=["GET"])
    def statistics(self, request, pk=None, *args, **kwargs) -> Response:
        article = Article.objects.get(id=pk)
        user = request.user

        if not user or not user.is_authenticated:
            return Response(status=status.HTTP_401_UNAUTHORIZED)

        has_perm = user.has_perm("statistics", article) or user.has_perm(
            "edit", article
        )
        if not has_perm:
            return Response(status=status.HTTP_403_FORBIDDEN)

        response = request_plausible_statistics(article)
        return Response(response.json())
