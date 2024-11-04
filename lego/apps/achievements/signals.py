from lego.apps.achievements.tasks import async_notify_user_of_achievement


def notify_on_achievement_callback(sender, instance, created, **kwargs):
    """
    Signal handler to check event-related achievements when a new registration is created.
        achievement_data = model_to_dict(instance)
    """
    async_notify_user_of_achievement.delay(instance.id)