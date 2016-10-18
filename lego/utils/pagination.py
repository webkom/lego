import six
from rest_framework.pagination import CursorPagination as RFCursorPagination
from rest_framework.pagination import PageNumberPagination
from rest_framework.settings import api_settings


class APIPagination(PageNumberPagination):
    page_size = api_settings.PAGE_SIZE
    max_page_size = api_settings.PAGE_SIZE
    page_query_param = 'page'
    page_size_query_param = 'page_size'


class CursorPagination(RFCursorPagination):
    offset_cutoff = 50
    ordering = 'created_at'

    def get_ordering(self, request, queryset, view):
        """
        Return a tuple of strings, that may be used in an `order_by` method.
        """
        ordering_filters = [
            filter_cls for filter_cls in getattr(view, 'filter_backends', [])
            if hasattr(filter_cls, 'get_ordering')
            ]

        if ordering_filters:
            # If a filter exists on the view that implements `get_ordering`
            # then we defer to that filter to determine the ordering.
            filter_cls = ordering_filters[0]
            filter_instance = filter_cls()
            ordering = filter_instance.get_ordering(request, queryset, view)
            assert ordering is not None, (
                'Using cursor pagination, but filter class {filter_cls} '
                'returned a `None` ordering.'.format(
                    filter_cls=filter_cls.__name__
                )
            )
        else:
            # Try to get the `ordering` attribute on the viewset class. Defaults to the `ordering`
            # attribute on the paginator class.
            ordering = getattr(view, 'ordering', self.ordering)

            assert ordering is not None, (
                'Using cursor pagination, but no ordering attribute was declared '
                'on the pagination class.'
            )
            assert '__' not in ordering, (
                'Cursor pagination does not support double underscore lookups '
                'for orderings. Orderings should be an unchanging, unique or '
                'nearly-unique field on the model, such as "-created" or "pk".'
            )

        assert isinstance(ordering, (six.string_types, list, tuple)), (
            'Invalid ordering. Expected string or tuple, but got {type}'.format(
                type=type(ordering).__name__
            )
        )

        if isinstance(ordering, six.string_types):
            return (ordering, )
        return tuple(ordering)
