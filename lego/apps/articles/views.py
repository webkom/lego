from django.http import Http404
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.exceptions import NotAuthenticated, PermissionDenied
from rest_framework import status

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

    def get_object(self) -> Article:
        queryset = self.get_queryset()
        pk = self.kwargs.get("pk")

        try:
            obj = queryset.get(id=pk)
        except (TypeError, ValueError, OverflowError, Article.DoesNotExist):
            obj = queryset.get(slug=pk)

        try:
            self.check_object_permissions(self.request, obj)
        except PermissionError:
            raise Http404
        return obj

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

    def create(self, request, *args, **kwargs):
        try:
            self.check_object_permissions(request, None)
        except:
            raise Http403
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return Response(
            serializer.data, status=status.HTTP_201_CREATED, headers=self.get_success_headers(serializer.data)
        )

    def destroy(self, request, *args, **kwargs):
        """
        Destroy an article and all its comments.
        """
        try:
            instance = self.get_object()
        except PermissionDenied:
            raise Http404

        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)

    def handle_exception(self, exc):
        if isinstance(exc, (NotAuthenticated, PermissionDenied)):
            raise Http404 from exc
        return super().handle_exception(exc)