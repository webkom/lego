from django_filters import CharFilter
from django_filters.constants import EMPTY_VALUES


class TagFilter(CharFilter):
    """
    The tag filter makes sure objects with the given tag is returned.
    """

    def filter(self, qs, value):
        if value in EMPTY_VALUES:
            return qs
        tags = [tag.strip() for tag in value.split(",") if tag.strip()]
        if not tags:
            return qs
        return qs.filter(tags__in=tags).distinct()
