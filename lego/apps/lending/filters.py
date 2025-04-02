from django.db.models import Q
from django_filters import CharFilter, FilterSet

from lego.apps.lending.models import LendingRequest


class LendingRequestFilterSet(FilterSet):

    status = CharFilter(method="filter_lending_status")

    def filter_lending_status(self, queryset, name, value):
        if not value:
            return queryset

        statuses = [
            status.strip()
            for status in self.request.query_params.get("status", "").split(",")
        ]

        if statuses and all(statuses):
            status_q = Q()
            for status in statuses:
                status_q |= Q(
                    status__in=[status],
                )

            filtered_queryset = queryset.filter(status_q)

            return filtered_queryset

        return queryset

    class Meta:
        model = LendingRequest
        fields = ["status"]
