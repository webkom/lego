from lego.apps.achievements.tasks import async_check_event_achievements_single_user
from lego.apps.events.websockets import notify_event_updated


def event_save_callback(sender, instance, created, **kwargs):
    if not created and not instance.deleted:
        notify_event_updated(instance)


def check_achievement_on_registration_callback(sender, instance, created, **kwargs):
    """
    Signal handler to check event-related achievements when a new registration is created.
    """
    async_check_event_achievements_single_user.delay(user_id=instance.user.id)
