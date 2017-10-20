from django_filters import DateFilter, FilterSet

from lego.apps.meetings.models import Meeting


class MeetingFilterSet(FilterSet):
    date_after = DateFilter('start_time', lookup_expr='gte')
    date_before = DateFilter('start_time', lookup_expr='lte')

    class Meta:
        model = Meeting
        fields = ('date_after', 'date_before')
