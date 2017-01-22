from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver

from .signal_handlers import AsyncSignalHandler

signal_handler = AsyncSignalHandler()


@receiver(post_save)
def post_save_callback(**kwargs):
    signal_handler.on_save(kwargs.get('instance'))


@receiver(post_delete)
def post_delete_callback(**kwargs):
    signal_handler.on_delete(kwargs.get('instance'))
