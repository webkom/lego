from django_filters import DateFilter, FilterSet

from lego.apps.gallery.models import Gallery


class GalleryFilterSet(FilterSet):
    date_after = DateFilter('taken_at', lookup_expr='gte')
    date_before = DateFilter('taken_at', lookup_expr='lte')

    class Meta:
        model = Gallery
        fields = ('date_after', 'date_before', 'event')
