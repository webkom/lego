from django_filters import CharFilter
from django_filters.constants import EMPTY_VALUES


class TagFilter(CharFilter):
    """
    The tag filter makes sure objects with the given tag is returned.
    """

    def filter(self, qs, value):
        if value in EMPTY_VALUES:
            return qs
        return qs.filter(tags__in=[value])
