from . import registry


class SearchBacked:
    """
    Base class for search backends. A backend needs to implement all methods on this class to work
    like it should.
    """

    @property
    def name(self):
        raise NotImplementedError('Please set the name property on the class.')

    def set_up(self):
        """
        This method is called when the backend instance is created. Use this method to do any
        startup configuration.
        """
        pass

    def get_search_index(self, content_type):
        """
        Return the search_index used to index a content_type.
        """
        return registry.get_content_type_index(content_type)

    def migrate(self):
        """
        This function is used when the 'migrate_search' management command is called.
        Use this function to perform any preparation of the backend before we index items.
        """
        pass

    def update_many(self, tuple_list):
        """
        Bulk update items. Used by the update function by default.
        The tuple_list us a list of tuples containing ('content_type', 'pk', 'data')
        """
        raise NotImplementedError('Please implement the update_many function.')

    def update(self, content_type, pk, data):
        return self.update_many([(content_type, pk, data)])

    def remove_many(self, tuple_list):
        """
        Bulk remove items from backend. The remove function uses this function by default.
        The tuple_list is a list of tuples containing ('content_type', 'pk')
        """
        raise NotImplementedError('Please implement the remove_many function.')

    def remove(self, content_type, pk):
        return self.remove_many([(content_type, pk)])

    def clear(self):
        """
        Clear all items handled by this backend.
        """
        raise NotImplementedError('Please implement the clear function.')

    def search(self, query, content_types=None, filters=None):
        """
        Search on a string 'query', use content_type or/and filters to filter the search.
        """
        raise NotImplementedError('Please implement the search function.')

    def autocomplete(self, query, content_types=None):
        """
        Autocomplete on a string 'query', use content_type or/and filters to filter the search.
        """
        raise NotImplementedError('Please implement the autocomplete function.')


"""
The current backend is initialized on startup in the apps.py file. This is the search backend used
to index objects.
"""
current_backend = None


def get_current_backend():
    """
    Return the current initialized backend.
    """
    return current_backend
