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

    search_ordering = ("-start_time",)
    autocomplete_ordering = ("-start_time",)


register(MeetingModelIndex)
