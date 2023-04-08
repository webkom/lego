from lego.apps.meetings.models import Meeting
from lego.apps.meetings.serializers import MeetingSearchSerializer
from lego.apps.search import register
from lego.apps.search.index import SearchIndex


class MeetingModelIndex(SearchIndex):
    queryset = Meeting.objects.all()
    serializer_class = MeetingSearchSerializer
    result_fields = (
        "title",
        "description",
        "report",
        "start_time",
    )
    autocomplete_result_fields = ("title", "start_time")

    autocomplete_fields = ("title", "description")
    search_fields = ("title", "description", "report")

    def get_autocomplete(self, instance):
        return instance.title

    def search(self, query):
        return super().search(query).order_by("-start_time")

    def autocomplete(self, query):
        return super().autocomplete(query).order_by("-start_time")


register(MeetingModelIndex)
