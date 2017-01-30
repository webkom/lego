from functools import wraps

from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver

from .signal_handler import AsyncSignalHandler

signal_handler = AsyncSignalHandler()


def disable_for_loaddata(signal_handler):
    """
    Decorator that turns off signal handlers when loading fixture data.
    """

    @wraps(signal_handler)
    def wrapper(*args, **kwargs):
        if kwargs.get('raw'):
            return
        signal_handler(*args, **kwargs)
    return wrapper


@receiver(post_save)
@disable_for_loaddata
def post_save_callback(**kwargs):
    if kwargs.get('created'):
        signal_handler.on_create(kwargs.get('instance'))
    else:
        signal_handler.on_update(kwargs.get('instance'))


@receiver(post_delete)
def post_delete_callback(**kwargs):
    signal_handler.on_delete(kwargs.get('instance'))
