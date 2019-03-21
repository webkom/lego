from django_filters import FilterSet

from lego.apps.joblistings.models import Joblisting


class JoblistingFilterSet(FilterSet):
    class Meta:
        model = Joblisting
        fields = ("company",)
