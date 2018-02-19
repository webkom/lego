from functools import wraps

from django.conf import settings
from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver

from . import handle_create, handle_delete, handle_update


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


@receiver(post_save)
@disable_on_test
def post_save_callback(**kwargs):
    instance = kwargs.get('instance')
    if not instance:
        return

    if kwargs.get('created'):
        handle_create(instance)
    else:
        handle_update(instance)


@disable_on_test(post_delete)
def post_delete_callback(**kwargs):
    handle_delete(kwargs.get('instance'))
