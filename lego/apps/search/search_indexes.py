from lego.apps.search import register

from .index import SearchIndex
from .models import SearchTestModel
from .serializers import SearchTestModelSerializer


class SearchTestModelIndex(SearchIndex):
    """
    This model is used for testing only and as a example on how to implement a search index.
    This may me a bit overkill but it makes testing much easier.
    """
    model = SearchTestModel
    serializer_class = SearchTestModelSerializer

    def get_autocomplete_text(self, instance):
        return instance.title


register(SearchTestModelIndex)
