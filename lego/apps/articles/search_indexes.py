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

    def get_autocomplete(self, instance):
        return instance.title

    def search(self, query):
        return (
            self.queryset.annotate(search=SearchVector("title", "text"))
            .filter(search=query)
            .order_by("-created_at")
        )

    def autocomplete(self, query):
        return (
            self.queryset.annotate(search=SearchVector("title"))
            .filter(
                search=SearchQuery(
                    ":* & ".join(query.split() + [""]).strip("& ").strip(),
                    search_type="raw",
                )
            )
            .order_by("-created_at")
        )


register(ArticleModelIndex)
