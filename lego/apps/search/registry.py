index_registry = {}


def register_search_index(search_index_cls):
    """
    Register the search index in our index registry.
    """
    from lego.utils.content_types import instance_to_content_type_string

    search_index = search_index_cls()
    model = search_index.get_model()
    index_registry[instance_to_content_type_string(model)] = search_index


def get_content_string_index(content_string):
    """
    Return a search index based on a string like app_label.model_name
    """
    try:
        return index_registry[content_string]
    except KeyError:
        pass


def get_model_index(model):
    """
    Retrieve the model index by model, None otherwise. Use this function to decide to index a
    model change or not.
    """
    from lego.utils.content_types import instance_to_content_type_string

    return get_content_string_index(instance_to_content_type_string(model))
