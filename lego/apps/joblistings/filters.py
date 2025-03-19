from django.utils import timezone
from django_filters import BooleanFilter, DateFilter, FilterSet

from lego.apps.joblistings.models import Joblisting


class JoblistingFilterSet(FilterSet):
    created_after = DateFilter("created_at", lookup_expr="gte")
    timeFilter = BooleanFilter(method="filter_time")

    class Meta:
        model = Joblisting
        fields = ("company",)

    def filter_time(self, queryset, name, value):
        if value:
            return queryset.filter(
                visible_from__lte=timezone.now(), visible_to__gte=timezone.now()
            )
        return queryset
