from django.conf import settings
from django.utils.encoding import force_text

from lego.apps.search.backends.elasticsearch import backend as es
from lego.utils.content_types import instance_to_content_type_string, instance_to_string


class SearchIndex:

    def __init__(self):
        pass

    def get_model(self):
        """
        Override this method or set model attribute on the class to define the index model.
        """
        model = getattr(self, 'model')
        if not model:
            raise NotImplementedError(
                'You must provide a \'get_model\' method or model attribute for the {0} '
                'index.'.format(self))
        return model

    def get_serializer_class(self):
        """
        Override this method or set the serializer_class attribute on the class to define the
        serializer.
        """
        serializer = getattr(self, 'serializer_class')
        if not serializer:
            raise NotImplementedError('You must provide a get_serializer_class method for '
                                      'the {0} index.'.format(self))
        return serializer

    def get_serializer(self, *args, **kwargs):
        """
        Return the serializer with args and kwargs.
        """
        serializer_class = self.get_serializer_class()
        return serializer_class(*args, **kwargs)

    def get_autocomplete_text(self, instance):
        """
        Implement this method for autocomplete support on this model.
        """
        return None

    def index_queryset(self):
        """
        Default queryset to index when doing a full update.
        Override this method to disable indexing of certain instances.
        """
        return self.get_model()._default_manager.all()

    def should_update(self, instance):
        """
        Determine if an instance should be updated in the index.
        """
        return True

    def prepare(self, instance):
        """
        Prepare a instance for indexing.
        This function creates a dict representing the instance.
        """
        prepared_data = {
            settings.SEARCH_ID_FIELD: instance_to_string(instance),
            settings.SEARCH_DJANGO_CT_FIELD: instance_to_content_type_string(instance),
            settings.SEARCH_DJANGO_ID_FIELD: force_text(instance.id)
        }

        serialized_data = self.get_serializer(instance)
        data = serialized_data.data
        data.update(prepared_data)

        autocomplete_input = self.get_autocomplete_text(instance)
        if autocomplete_input:
            data.update({
                'autocomplete': {
                    'input': autocomplete_input,
                    'payload': {
                        'ct': prepared_data[settings.SEARCH_DJANGO_CT_FIELD],
                        'id': prepared_data[settings.SEARCH_DJANGO_ID_FIELD]
                    }
                }
            })
        return data

    def update(self, **kwargs):
        """
        Updates the entire index.
        """
        queryset = self.index_queryset()
        es.update_many([self._get_payload_tuple(instance) for instance in queryset])

    def update_instance(self, instance, **kwargs):
        """
        Update a given instance in the index.
        """
        if not self.should_update(instance):
            return

        es.update(*self._get_payload_tuple(instance))

    def remove_instance(self, instance, **kwargs):
        """
        Remove a given instance from the index.
        """
        es.remove(instance_to_content_type_string(instance), force_text(instance.id))

    def _get_payload_tuple(self, instance):
        data = self.prepare(instance)
        return [
            data,
            data[settings.SEARCH_DJANGO_CT_FIELD],
            data[settings.SEARCH_DJANGO_ID_FIELD]
        ]
