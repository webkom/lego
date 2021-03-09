from django.contrib.postgres.search import SearchQuery, SearchVector
from django.db.models import Q

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

    def get_autocomplete(self, instance):
        return [instance.title, instance.slug_field]


register(PageModelIndex)
