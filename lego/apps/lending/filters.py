from django_filters import CharFilter, FilterSet

from lego.apps.lending.models import LendingRequest


class LendingRequestFilterSet(FilterSet):

    status = CharFilter(method="filter_lending_status")

    def filter_lending_status(self, queryset, name, value):
        if not value:
            return queryset

        statuses = [status.strip() for status in value.split(",")]

        if not statuses or "" in statuses:
            return queryset

        return queryset.filter(status__in=statuses)

    class Meta:
        model = LendingRequest
        fields = ["status"]
