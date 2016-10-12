from django_filters import CharFilter, FilterSet

from lego.apps.events.models import Event


class EventsFilterSet(FilterSet):
    year = CharFilter('start_time__year')
    month = CharFilter('start_time__month')

    class Meta:
        model = Event
        fields = ('year', 'month',)
