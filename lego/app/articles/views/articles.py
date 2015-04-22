from lego.app.articles.permissions import ArticlePermissions
from rest_any_permissions.permissions import AnyPermissions
from rest_framework import viewsets

from lego.app.articles.models import Article
from lego.app.articles.serializers import ArticleSerializer
from lego.permissions.filters import ObjectPermissionsFilter
from lego.permissions.object_permissions import ObjectPermissions


class ArticlesViewSet(viewsets.ModelViewSet):
    queryset = Article.objects.all()
    serializer_class = ArticleSerializer
    filter_backends = (ObjectPermissionsFilter,)
    permission_classes = (AnyPermissions,)
    any_permission_classes = (ArticlePermissions,)
