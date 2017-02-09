handler_registry = {}


def register_handler(handler_cls):
    """
    Register the search index in our index registry.
    """
    handler_registry[handler_cls.model] = handler_cls()


def get_handler(model):
    """
    Retrieve the model index by model, None otherwise. Use this function to decide to index a
    model change or not.
    """
    try:
        return handler_registry[model]
    except KeyError:
        pass
