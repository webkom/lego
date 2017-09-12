from lego.apps.events.websockets import notify_event_updated


def event_save_callback(sender, instance, created, **kwargs):
    if not created and not instance.deleted:
        notify_event_updated(instance)
