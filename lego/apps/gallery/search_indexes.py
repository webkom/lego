from lego.apps.search import register
from lego.apps.search.index import SearchIndex

from .models import Gallery
from .serializers import GallerySearchSerializer


class GalleryIndex(SearchIndex):
    queryset = Gallery.objects.all()
    serializer_class = GallerySearchSerializer
    result_fields = ("title", "location", "description")
    autocomplete_result_fields = ("title",)

    search_fields = ("title", "event__title")
    autocomplete_fields = ("title",)

    autocomplete_ordering = ("-created_at",)


register(GalleryIndex)
