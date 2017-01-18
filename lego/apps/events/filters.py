from django_filters import CharFilter, DateFilter, FilterSet

from lego.apps.events.models import Event


class EventsFilterSet(FilterSet):
    year = CharFilter('start_time__year')
    month = CharFilter('start_time__month')
    date_after = DateFilter('start_time', lookup_expr='gte')
    date_before = DateFilter('start_time', lookup_expr='lte')

    class Meta:
        model = Event
        fields = ('year', 'month', 'date_after', 'date_before')
