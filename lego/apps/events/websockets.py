from datetime import datetime

from lego.apps.events.models import Event
from lego.apps.events.serializers.sockets import (
    EventReadDetailedSocketSerializer,
    RegistrationPaymentInitiateSocketSerializer,
    RegistrationPaymentReadSocketSerializer,
    RegistrationReadSocketSerializer,
)
from lego.apps.permissions.constants import LIST
from lego.apps.permissions.utils import get_permission_handler
from lego.apps.websockets.groups import group_for_event, group_for_user
from lego.apps.websockets.notifiers import notify_group


def find_event_groups(user):
    """
    Find all channels groups the user belongs to as a result
    of being signed up to future events.
    """
    queryset = Event.objects.filter(start_time__gt=datetime.now())
    if not user.has_perm(LIST, queryset):
        permission_handler = get_permission_handler(queryset.model)
        queryset = permission_handler.filter_queryset(user, queryset)

    groups = []
    for event in queryset:
        groups.append(group_for_event(event))

    return groups


def notify_event_registration(action_type, registration, **kwargs):
    group = group_for_event(registration.event)
    kwargs["event_id"] = registration.event.id
    serializer = RegistrationReadSocketSerializer(
        {"type": action_type, "payload": registration, "meta": kwargs}
    )
    notify_group(group, serializer.data)


def notify_user_payment_initiated(action_type, registration, **kwargs):
    group = group_for_user(registration.user)
    kwargs["event_id"] = registration.event.id
    serializer = RegistrationPaymentInitiateSocketSerializer(
        {"type": action_type, "payload": registration, "meta": kwargs},
        context={"user": registration.user},
    )
    notify_group(group, serializer.data)


def notify_user_payment(action_type, registration, **kwargs):
    group = group_for_user(registration.user)
    kwargs["event_id"] = registration.event.id
    serializer = RegistrationPaymentReadSocketSerializer(
        {"type": action_type, "payload": registration, "meta": kwargs},
        context={"user": registration.user},
    )
    notify_group(group, serializer.data)


def notify_user_registration(action_type, registration, **kwargs):
    group = group_for_user(registration.user)
    kwargs["event_id"] = registration.event.id
    serializer = RegistrationReadSocketSerializer(
        {"type": action_type, "payload": registration, "meta": kwargs},
        context={"user": registration.user},
    )

    notify_group(group, serializer.data)


def notify_event_updated(event, **kwargs):
    group = group_for_event(event)
    serializer = EventReadDetailedSocketSerializer(
        {"type": "SOCKET_EVENT_UPDATED", "payload": event, "meta": kwargs}
    )

    notify_group(group, serializer.data)
