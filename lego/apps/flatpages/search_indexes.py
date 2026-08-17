from lego.apps.search import register
from lego.apps.search.index import SearchIndex

from .models import Page
from .serializers import PageDetailSerializer


class PageModelIndex(SearchIndex):
    queryset = Page.objects.all()
    serializer_class = PageDetailSerializer
    result_fields = ("title", "content", "slug", "picture", "category")
    autocomplete_result_fields = ("title", "slug", "picture", "category")

    search_fields = ("title", "slug", "content")
    autocomplete_fields = ("title", "slug")


register(PageModelIndex)
