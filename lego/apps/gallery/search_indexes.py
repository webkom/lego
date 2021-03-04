from lego.apps.search import register
from lego.apps.search.index import SearchIndex

from .models import Gallery
from .serializers import GallerySearchSerializer


class GalleryIndex(SearchIndex):

    queryset = Gallery.objects.all()
    serializer_class = GallerySearchSerializer
    result_fields = ("title", "location", "description")
    autocomplete_result_fields = ("title",)
    autocomplete_fields = ("title",)

    def get_autocomplete(self, instance):
        return [instance.title]

    def autocomplete(self, query):
        return super().autocomplete(query).order_by("-created_at")


register(GalleryIndex)
