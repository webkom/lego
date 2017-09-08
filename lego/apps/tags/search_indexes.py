from lego.apps.search import register
from lego.apps.search.index import SearchIndex

from .models import Tag
from .serializers import TagSearchSerializer


class TagIndex(SearchIndex):

    queryset = Tag.objects.all()
    serializer_class = TagSearchSerializer
    result_fields = ('tag',)
    autocomplete_result_fields = ('tag',)

    def get_autocomplete(self, instance):
        return [instance.tag]


register(TagIndex)
