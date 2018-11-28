from django_filters.rest_framework import filterset
from lego.apps.articles.models import Article
from lego.apps.tags.filters import TagFilter


class ArticleFilterSet(filterset.FilterSet):

    tag = TagFilter()

    class Meta:
        model = Article
        fields = ("tag",)
