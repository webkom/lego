from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver
from prometheus_client import Counter

from .signal_handlers import AsyncSignalHandler

signal_handler = AsyncSignalHandler()
SEARCH_INDEXER_COUNTER = Counter('search_index', 'Search indexer', ['method'])


@receiver(post_save)
def post_save_callback(**kwargs):
    SEARCH_INDEXER_COUNTER.labels('insert').inc()
    signal_handler.on_save(kwargs.get('instance'))


@receiver(post_delete)
def post_delete_callback(**kwargs):
    SEARCH_INDEXER_COUNTER.labels('remove').inc()
    signal_handler.on_delete(kwargs.get('instance'))
