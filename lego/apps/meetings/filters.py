from datetime import datetime, time

from django.utils import timezone
from django_filters import DateFilter, FilterSet

from lego.apps.meetings.models import Meeting


class MeetingFilterSet(FilterSet):
    date_after = DateFilter(method="filter_date_after")
    date_before = DateFilter(method="filter_date_before")

    def filter_date_after(self, queryset, name, value):
        aware_start_of_day = timezone.make_aware(datetime.combine(value, time.min))
        return queryset.filter(start_time__gte=aware_start_of_day)

    def filter_date_before(self, queryset, name, value):
        aware_end_of_day = timezone.make_aware(datetime.combine(value, time.max))
        return queryset.filter(start_time__lte=aware_end_of_day)

    class Meta:
        model = Meeting
        fields = ("date_after", "date_before")
