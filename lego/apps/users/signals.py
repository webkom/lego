from django.db.models.signals import post_save
from django.dispatch import receiver

from lego.apps.stats.analytics_client import identify
from lego.apps.users.models import User


@receiver(post_save, sender=User)
def post_save_callback(created, instance, **kwargs):
    """
    Send new user identities to the analytics backend.
    """
    if created:
        identify(instance)
