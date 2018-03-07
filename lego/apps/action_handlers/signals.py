from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver

from .events import handle_create, handle_delete, handle_update


@receiver(post_save)
def post_save_callback(**kwargs):
    instance = kwargs.get('instance')
    if not instance:
        return

    if kwargs.get('created'):
        handle_create(instance)
    else:
        handle_update(instance)


@receiver(post_delete)
def post_delete_callback(**kwargs):
    handle_delete(kwargs.get('instance'))
