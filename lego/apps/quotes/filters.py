from django_filters import FilterSet

from .models import Quote


class QuotesFilterSet(FilterSet):

    class Meta:
        model = Quote
        fields = ('approved', )
