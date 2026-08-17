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

    search_ordering = ("-created_at",)
    autocomplete_ordering = ("-created_at",)


register(ArticleModelIndex)
