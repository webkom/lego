from lego.apps.events.websockets import event_updated_notifier


def event_save_callback(sender, instance, created, **kwargs):
    if not created:
        event_updated_notifier(instance)
