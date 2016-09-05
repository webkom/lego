index_registry = {}


def register_search_index(search_index_cls):
    """
    Register the search index in our index registry.
    """
    search_index = search_index_cls()
    index_registry[search_index.get_model()] = search_index


def get_model_index(model):
    """
    Retrieve the model index by model, None otherwise. Use this function to decide to index a
    model change or not.
    """
    try:
        return index_registry[model]
    except KeyError:
        pass
