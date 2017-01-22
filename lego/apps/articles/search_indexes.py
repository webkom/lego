from lego.apps.search import register
from lego.apps.search.index import SearchIndex

from .models import Article
from .serializers import DetailedArticleSerializer


class ArticleModelIndex(SearchIndex):

    queryset = Article.objects.all()
    serializer_class = DetailedArticleSerializer
    result_fields = ('title', 'description', 'text')

    def get_autocomplete(self, instance):
        return instance.title


register(ArticleModelIndex)
