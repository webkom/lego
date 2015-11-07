from haystack import indexes

from lego.search.index import SearchIndex

from .models import Article


class ArticleIndex(SearchIndex, indexes.Indexable):

    auto_complete = indexes.EdgeNgramField(model_attr='title')
    author = indexes.CharField(model_attr='author', faceted=True)

    def get_model(self):
        return Article

    def index_queryset(self, using=None):
        return Article.objects.all()
