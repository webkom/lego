from django.contrib.postgres.search import SearchQuery, SearchVector

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

    def get_autocomplete(self, instance):
        return instance.title

    def search(self, query):
        return (
            self.queryset.annotate(search=SearchVector("title", "description", "text"))
            .filter(search=query)
            .order_by("-start_time")
        )

    def autocomplete(self, query):
        return (
            self.queryset.annotate(search=SearchVector("title"))
            .filter(
                search=SearchQuery(
                    ":* & ".join(query.split() + [""]).strip("& ").strip(),
                    search_type="raw",
                )
            )
            .order_by("-start_time")
        )


register(EventModelIndex)
