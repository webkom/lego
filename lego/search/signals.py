from django.conf import settings
from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver

from .signal_handler import SignalHandler

signal_handler = SignalHandler()


@receiver(post_save)
def post_save_callback(sender, **kwargs):
    if not settings.TESTING:  # We do not want to run the indexing pipeline while testing.
        signal_handler.on_save(
            sender, kwargs.get('instance'), kwargs.get('created'), kwargs.get('update_fields')
        )


@receiver(post_delete)
def post_delete_callback(sender, **kwargs):
    if not settings.TESTING:  # We do not want to run the indexing pipeline while testing.
        signal_handler.on_delete(sender, kwargs.get('instance'))
