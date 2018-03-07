from functools import wraps

from django.conf import settings

from . import registry

default_app_config = 'lego.apps.action_handlers.apps.ActionHandlersConfig'


def disable_on_test(signal_handler):
    """
    Decorator that turns off signal handlers when loading fixture data and running tests.
    """

    @wraps(signal_handler)
    def wrapper(*args, **kwargs):
        if kwargs.get('raw') or settings.TESTING:
            return
        signal_handler(*args, **kwargs)

    return wrapper


@disable_on_test
def call_handler(instance, action, **kwargs):
    if registry.handler_exists(instance):
        handler = registry.get_handler_by_instance(instance)
        return handler.run(instance, action, **kwargs)


def handle_event(instance, action, **kwargs):
    return call_handler(instance, action, **kwargs)


def handle_create(instance):
    return handle_event(instance, 'create')


def handle_update(instance):
    return handle_event(instance, 'update')


def handle_delete(instance):
    return handle_event(instance, 'delete')
