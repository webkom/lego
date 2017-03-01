from django_filters import CharFilter, DateFilter, FilterSet

from lego.apps.events.models import Event


class EventsFilterSet(FilterSet):
    date_after = DateFilter('start_time', lookup_expr='gte')
    date_before = DateFilter('start_time', lookup_expr='lte')
    company = CharFilter('company')

    class Meta:
        model = Event
        fields = ('date_after', 'date_before')
