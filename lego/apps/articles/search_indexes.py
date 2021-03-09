from django.contrib.postgres.search import SearchQuery, SearchVector

from lego.apps.search import register
from lego.apps.search.index import SearchIndex

from .models import Article
from .serializers import SearchArticleSerializer


class ArticleModelIndex(SearchIndex):

    queryset = Article.objects.all()
    serializer_class = SearchArticleSerializer
    result_fields = ("title", "description", "cover")
    autocomplete_result_fields = ("title",)

    search_fields = ("title", "text", "description")
    autocomplete_fields = ("title",)

    def get_autocomplete(self, instance):
        return instance.title

    def search(self, query):
        return super().search(query).order_by("-created_at")

    def autocomplete(self, query):
        return super().autocomplete(query).order_by("-created_at")


register(ArticleModelIndex)
