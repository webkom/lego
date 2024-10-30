from django.db.models.signals import post_save
from django.dispatch import receiver

from lego.apps.achievements.tasks import async_check_event_achievements_single_user
from lego.apps.events.models import Registration
from lego.apps.events.websockets import notify_event_updated


def event_save_callback(sender, instance, created, **kwargs):
    if not created and not instance.deleted:
        notify_event_updated(instance)


@receiver(post_save, sender=Registration)
def check_achievement_on_registration_callback(sender, instance, created, **kwargs):
    """
    Signal handler to check event-related achievements when a new registration is created.
    """
    if created:
        async_check_event_achievements_single_user.delay(instance.user)
