handler_registry = {}


def register_handler(handler_cls):
    """
    Register the search index in our index registry.
    """
    handler_registry[handler_cls.model] = handler_cls()


def handler_exists(instance):
    """
    Check if a handler is registered for a given instance.
    """
    return instance._meta.model in handler_registry.keys()


def get_handler(model):
    """
    Retrieve the model index by model, None otherwise. Use this function to decide to index a
    model change or not.
    """
    try:
        return handler_registry[model]
    except KeyError:
        pass
