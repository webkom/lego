from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver
from prometheus_client import Counter

from .signal_handlers import AsyncSignalHandler

signal_handler = AsyncSignalHandler()
search_index = Counter('search_index', 'Track index events')
search_remove = Counter('search_remove', 'Track item removal from search index')


@receiver(post_save)
def post_save_callback(**kwargs):
    search_index.inc()
    signal_handler.on_save(kwargs.get('instance'))


@receiver(post_delete)
def post_delete_callback(**kwargs):
    search_remove.inc()
    signal_handler.on_delete(kwargs.get('instance'))
