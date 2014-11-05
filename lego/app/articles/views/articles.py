from rest_framework import viewsets
from rest_framework.response import  Response
from rest_framework.generics import get_object_or_404
from rest_framework.exceptions import PermissionDenied

from lego.app.articles.models import Article
from lego.app.articles.serializers import ArticleSerializer

class ArticlesViewSet(viewsets.ModelViewSet):
    queryset = Article.objects.all()
    serializer_class = ArticleSerializer

    def list(self, request, *args, **kwargs):
        def can_view(article):
            intersect = request.user.groups & article.can_view
            return  len(intersect) != 0
        articles = self.queryset.filter(can_view)

        serializer = ArticleSerializer(articles, many=True)
        return Response(serializer)

    def retrieve(self, request, pk=None, *args, **kwargs):
        article = get_object_or_404(self.queryset, pk=pk)
        if len(request.user.groups & article.can_view) != 0:
            raise PermissionDenied()
        serializer = ArticleSerializer(article)
        return Response(serializer)

    def update(self, request, pk=None, *args, **kwargs):
        user = request.user
        article = get_object_or_404(self.queryset, pk=pk)

        if len(request.user.groups & article.can_view) != 0\
                or user in article.users_can_edit:
            raise PermissionDenied()
        return super(ArticlesViewSet, self).update(request, *args, **kwargs)
