from lego.apps.search import register
from lego.apps.search.index import SearchIndex

from .models import Article
from .serializers import SearchArticleSerializer


class ArticleModelIndex(SearchIndex):

    queryset = Article.objects.all()
    serializer_class = SearchArticleSerializer
    result_fields = ('title', 'description', 'text', 'cover')
    autocomplete_result_fields = ('title')

    def get_autocomplete(self, instance):
        return instance.title


register(ArticleModelIndex)
