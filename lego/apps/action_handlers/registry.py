handler_registry = {}


def register_handler(handler_cls):
    model = handler_cls.model
    if not model:
        raise TypeError("Set the .model value on the handler class")

    handler_registry[model] = handler_cls()


def handler_exists(instance: object()):
    return instance._meta.model in handler_registry.keys()


def get_handler(model):
    try:
        return handler_registry[model]
    except KeyError:
        pass


def get_handler_by_instance(instance):
    try:
        return handler_registry[instance._meta.model]
    except KeyError:
        pass
