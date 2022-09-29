from django_filters import DateFilter, FilterSet

from lego.apps.joblistings.models import Joblisting


class JoblistingFilterSet(FilterSet):
    created_after = DateFilter("created_at", lookup_expr="gte")

    class Meta:
        model = Joblisting
        fields = ("company",)
