from lego.apps.events.models import Event
from lego.apps.users.models import User


def group_for_user(user: User) -> str:
    return f"user-{user.pk}"


def group_for_event(event: Event, has_registrations_access: bool) -> str:
    return f"event-{'full' if has_registrations_access else 'limited'}-{event.pk}"
