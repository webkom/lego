from lego.apps.events.models import Event
from lego.apps.events.serializers.events import EventSearchSerializer
from lego.apps.search import register
from lego.apps.search.index import SearchIndex


class EventModelIndex(SearchIndex):

    queryset = Event.objects.all()
    serializer_class = EventSearchSerializer
    result_fields = (
        "title",
        "description",
        "text",
        "cover",
        "location",
        "start_time",
        "end_time",
    )
    autocomplete_result_fields = ("title", "start_time")

    autocomplete_fields = ("title",)
    search_fields = ("title", "description", "text")

    def get_autocomplete(self, instance):
        return instance.title

    def search(self, query):
        return super().search(query).order_by("-start_time")

    def autocomplete(self, query):
        return super().autocomplete(query).order_by("-start_time")


register(EventModelIndex)
