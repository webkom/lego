from functools import wraps

from django.conf import settings

from lego.utils.content_types import instance_to_string

from . import registry
from .tasks import execute_action_handler


def disable_on_test(signal_handler):
    """
    Decorator that turns off signal handlers when loading fixture data and running tests.
    """

    @wraps(signal_handler)
    def wrapper(*args, **kwargs):
        if kwargs.get('raw') or settings.TESTING:
            return
        return signal_handler(*args, **kwargs)

    return wrapper


@disable_on_test
def call_handler(instance, action, **kwargs):
    """
    The call_handler executes the delete action sync because the instance is removed from the DB
    before a worker is able to process the event.

    All other actions is executed by celery.
    """

    if registry.handler_exists(instance):
        if action == 'delete':
            handler = registry.get_handler_by_instance(instance)
            return handler.run(instance, action, **kwargs)

        return execute_action_handler.delay(
            instance=instance_to_string(instance), action=action, kwargs=kwargs
        )


def handle_event(instance, action, **kwargs):
    return call_handler(instance, action, **kwargs)


def handle_create(instance):
    return handle_event(instance, 'create')


def handle_update(instance):
    return handle_event(instance, 'update')


def handle_delete(instance):
    return handle_event(instance, 'delete')
