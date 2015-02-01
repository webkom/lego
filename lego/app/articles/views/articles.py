from rest_framework import viewsets

from lego.app.articles.models import Article
from lego.app.articles.serializers import ArticleSerializer
from lego.permissions.filters import ObjectPermissionsFilter
from lego.permissions.model_permissions import PostModelPermissions
from lego.permissions.object_permissions import ObjectPermissions


class ArticlesViewSet(viewsets.ModelViewSet):
    queryset = Article.objects.all()
    serializer_class = ArticleSerializer
    filter_backends = (ObjectPermissionsFilter,)
    permission_classes = (PostModelPermissions, ObjectPermissions)
