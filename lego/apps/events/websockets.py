from __future__ import annotations

from datetime import timedelta
from typing import TYPE_CHECKING

from django.utils import timezone

from lego.apps.events.models import Event
from lego.apps.events.serializers.sockets import (
    EventReadDetailedSocketSerializer,
    RegistrationPaymentInitiateSocketSerializer,
    RegistrationPaymentReadErrorSerializer,
    RegistrationPaymentReadSocketSerializer,
    RegistrationReadAnonymizedSocketSerializer,
    RegistrationReadSocketSerializer,
)
from lego.apps.permissions.constants import LIST
from lego.apps.permissions.utils import get_permission_handler
from lego.apps.websockets.groups import group_for_event, group_for_user
from lego.apps.websockets.notifiers import notify_group

if TYPE_CHECKING:
    from django.db.models.query import QuerySet

    from lego.apps.events.models import Registration
    from lego.apps.users.models import User


def find_event_groups(user: User) -> list[str]:
    """
    Find all channels groups the user belongs to as a result
    of being signed up to future events.

    Since we use websockets for registrations and event description updates, include events
    that has not started and that started less than two days ago.
    """
    queryset: QuerySet[Event] = Event.objects.filter(
        start_time__gt=timezone.now() - timedelta(days=2)
    )
    if not user.has_perm(LIST, queryset):
        permission_handler = get_permission_handler(queryset.model)
        queryset = permission_handler.filter_queryset(user, queryset)

    groups: list[str] = []
    for event in queryset:
        groups.append(group_for_event(event, event.user_should_see_regs(user)))

    return groups


def notify_event_registration(action_type: str, registration: Registration, **kwargs):
    full_access_group = group_for_event(registration.event, True)
    partial_access_group = group_for_event(registration.event, False)

    kwargs["event_id"] = registration.event.id
    full_serializer = RegistrationReadSocketSerializer(
        {"type": action_type, "payload": registration, "meta": kwargs}
    )
    partial_serializer = RegistrationReadAnonymizedSocketSerializer(
        {"type": action_type, "payload": registration, "meta": kwargs}
    )

    notify_group(full_access_group, full_serializer.data)
    notify_group(partial_access_group, partial_serializer.data)


def notify_user_payment_initiated(
    action_type: str, registration: Registration, **kwargs
):
    group = group_for_user(registration.user.pk)
    kwargs["event_id"] = registration.event.id
    serializer = RegistrationPaymentInitiateSocketSerializer(
        {"type": action_type, "payload": registration, "meta": kwargs},
        context={"user": registration.user},
    )
    notify_group(group, serializer.data)


def notify_user_payment(action_type: str, registration: Registration, **kwargs):
    group = group_for_user(registration.user.pk)
    kwargs["event_id"] = registration.event.id
    serializer = RegistrationPaymentReadSocketSerializer(
        {"type": action_type, "payload": registration, "meta": kwargs},
        context={"user": registration.user},
    )
    notify_group(group, serializer.data)


def notify_user_payment_error(action_type: str, registration: Registration, **kwargs):
    group = group_for_user(registration.user.pk)
    kwargs["event_id"] = registration.event.id
    serializer = RegistrationPaymentReadErrorSerializer(
        {"type": action_type, "payload": registration, "meta": kwargs},
        context={"user": registration.user},
    )
    notify_group(group, serializer.data)


def notify_user_registration(action_type: str, registration: Registration, **kwargs):
    group = group_for_user(registration.user.pk)
    kwargs["event_id"] = registration.event.id
    serializer = RegistrationReadSocketSerializer(
        {"type": action_type, "payload": registration, "meta": kwargs},
        context={"user": registration.user},
    )

    notify_group(group, serializer.data)


def notify_event_updated(event: Event, **kwargs):
    full_access_group = group_for_event(event, True)
    limited_access_group = group_for_event(event, False)
    serializer = EventReadDetailedSocketSerializer(
        {"type": "SOCKET_EVENT_UPDATED", "payload": event, "meta": kwargs}
    )

    notify_group(full_access_group, serializer.data)
    notify_group(limited_access_group, serializer.data)
