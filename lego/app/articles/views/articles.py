from rest_framework import viewsets
from rest_framework.permissions import DjangoModelPermissionsOrAnonReadOnly
from rest_framework.response import  Response
from rest_framework.generics import get_object_or_404
from rest_framework.exceptions import PermissionDenied

from lego.app.articles.models import Article
from lego.app.articles.serializers import ArticleSerializer

class ArticlesViewSet(viewsets.ModelViewSet):
    queryset = Article.objects.all()
    serializer_class = ArticleSerializer
    permission_classes = (DjangoModelPermissionsOrAnonReadOnly, )

    def list(self, request, *args, **kwargs):
        articles = self.queryset
        serializer = ArticleSerializer(articles, many=True)
        return Response(serializer.data)

    def retrieve(self, request, pk=None, *args, **kwargs):
        article = get_object_or_404(self.queryset, pk=pk)
        serializer = ArticleSerializer(article)
        return Response(serializer.data)

    def update(self, request, pk=None, *args, **kwargs):
        user = request.user
        article = get_object_or_404(self.queryset, pk=pk)
        return super(ArticlesViewSet, self).update(request, *args, **kwargs)
