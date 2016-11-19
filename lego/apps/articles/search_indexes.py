from lego.apps.search import register
from lego.apps.search.index import SearchIndex

from .models import Article
from .serializers import DetailedArticleSerializer


class ArticleModelIndex(SearchIndex):
    model = Article
    serializer_class = DetailedArticleSerializer

    def get_autocomplete(self, instance):
        return instance.title


register(ArticleModelIndex)
