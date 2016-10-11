from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver

from .signal_handler import AsyncSignalHandler

signal_handler = AsyncSignalHandler()


@receiver(post_save)
def post_save_callback(**kwargs):
    if kwargs.get('created'):
        signal_handler.on_create(kwargs.get('instance'))
    else:
        signal_handler.on_update(kwargs.get('instance'))


@receiver(post_delete)
def post_delete_callback(**kwargs):
    signal_handler.on_delete(kwargs.get('instance'))
