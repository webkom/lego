from django.utils.encoding import force_text
from structlog import get_logger

from . import backend

log = get_logger()


class SearchIndex:
    """
    Base class for search indexes. Implement this class to index a model. Remeber to use the
    register function to register the index.
    """

    queryset = None
    serializer_class = None

    def get_backend(self):
        """
        Return the backend used to handle changes by this index. You should know what you do if
        you override this function. The search interface only supports one backend.
        """
        return backend.current_backend

    def get_queryset(self):
        """
        Get the queryset that should be indexed. Override this method or set a queryset attribute
        on this class.
        """
        queryset = getattr(self, 'queryset')

        if queryset is None:
            raise NotImplementedError(
                f'You must provide a \'get_qyeryset\' method or queryset attribute for the {self} '
                f'index.'
            )
        return queryset

    def get_model(self):
        """
        Get the model this index is bound to.
        """
        queryset = self.get_queryset()
        return queryset.model

    def get_serializer_class(self):
        """
        Override this method or set the serializer_class attribute on the class to define the
        serializer.
        """
        serializer_class = getattr(self, 'serializer_class')
        if serializer_class is None:
            raise NotImplementedError('You must provide a \'get_serializer_class\' function or a '
                                      f'serializer_class attribute for the {self} index')
        return serializer_class

    def get_filter_fields(self):
        """
        Returns an array of allowed fields to filter on. Returns a empty list by default. Override
        this function or set the filter_fields variable on the class to change this.
        """
        filter_fields = getattr(self, 'filter_fields', [])
        return filter_fields

    def get_result_fields(self):
        """
        Returns a list of fields attached to the search result.
        """
        result_fields = getattr(self, 'result_fields')
        if result_fields is None:
            raise NotImplementedError('You must provide a \'get_result_fields\' function or a '
                                      f'result_fields attribute for the {self} index')
        return result_fields

    def get_autocomplete_result_fields(self):
        """
        Returns a list of fields attached to the autocomplete result.
        """
        result_fields = getattr(self, 'autocomplete_result_fields', [])
        return result_fields

    def get_index_filter_fields(self):
        """
        Returns True if we want to index filter fields. Defaults to False.
        """
        index_filter_fields = getattr(self, 'index_filter_fields', False)
        return index_filter_fields

    def get_serializer(self, *args, **kwargs):
        """
        Return the serializer with args and kwargs.
        """
        serializer_class = self.get_serializer_class()
        return serializer_class(*args, **kwargs)

    def get_autocomplete(self, instance):
        """
        Implement this method to support autocomplete on the model. This function should return
        None, a string or a list of strings.
        """
        return None

    def should_update(self, instance):
        """
        Determine if an instance should be updated in the index.
        """
        return True

    def prepare(self, instance):
        """
        Prepare instance for indexing, this function returns a dict in a specific format.
        This is passed to the search-backend. The backend has to parse this and index it.
        """
        from lego.utils.content_types import instance_to_content_type_string

        serializer = self.get_serializer(instance)
        data = serializer.data

        def get_filter_data(data):
            get_func = data.get if self.get_index_filter_fields() else data.pop
            filter_fields = self.get_filter_fields()
            return {key: get_func(key) for key in filter_fields}

        prepared_instance = {
            'content_type': force_text(instance_to_content_type_string(instance)),
            'pk': force_text(instance.pk),
            'data': {
                'autocomplete': self.get_autocomplete(instance),
                'filters': {k: v for k, v in get_filter_data(data).items() if v or not v == ''},
                'fields': {k: v for k, v in data.items() if v or not v == ''}
            }
        }

        return prepared_instance

    def update(self):
        """
        Updates the entire index.
        We do this in batch to optimize performance. NB: Requires automatic IDs.
        """

        def batch(queryset, func, chunk=100, start=0):
            if not queryset.exists():
                return

            try:
                while start < queryset.order_by('pk').last().pk:
                    func(queryset.filter(pk__gt=start, pk__lte=start + chunk).iterator())
                    start += chunk
            except TypeError:
                func(queryset.all().iterator())

        def prepare(result):
            prepared = self.prepare(result)
            return prepared['content_type'], prepared['pk'], prepared['data']

        def update_bulk(result_set):
            self.get_backend().update_many(map(prepare, result_set))

        batch(self.get_queryset(), update_bulk)

    def update_instance(self, instance):
        """
        Update a given instance in the index.
        """
        if not self.should_update(instance):
            log.info('search_instance_update_rejected')
            return

        self.get_backend().update(**self.prepare(instance))

    def remove_instance(self, pk):
        """
        Remove a single instance from the index. We use pks here because the instance may not
        exists in the database.
        """
        from lego.utils.content_types import instance_to_content_type_string

        self.get_backend().remove(
            content_type=instance_to_content_type_string(self.get_model()),
            pk=force_text(pk)
        )
