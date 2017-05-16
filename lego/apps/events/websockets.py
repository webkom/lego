from datetime import datetime

from lego.apps.events.models import Event
from lego.apps.events.serializers.events import EventReadDetailedSerializer
from lego.apps.events.serializers.registrations import RegistrationReadSerializer, RegistrationPaymentReadSerializer
from lego.apps.events.serializers.sockets import (WebsocketSerializer)
from lego.apps.permissions.filters import filter_queryset
from lego.apps.websockets.groups import group_for_event, group_for_user
from lego.apps.websockets.notifiers import notify_group


def socket_response_creator(action_type, payload, meta, payload_serializer, context=None):

    serializer = WebsocketSerializer(data={
        'type': action_type,
        'payload': payload_serializer(payload).data,
        'meta': meta
    }, context=context)
    serializer.is_valid(raise_exception=True)
    return serializer.validated_data


def find_event_groups(user):
    """
    Find all channels groups the user belongs to as a result
    of being signed up to future events.
    """
    queryset = Event.objects.filter(start_time__gt=datetime.now())
    if not user.has_perm('/sudo/admin/events/list/'):
        queryset = filter_queryset(user, queryset)
    groups = []
    for event in queryset.all():
        groups.append(group_for_event(event))

    return groups


def notify_event_registration(action_type, registration, **kwargs):
    group = group_for_event(registration.event)
    response = socket_response_creator(
        action_type, registration, kwargs, RegistrationReadSerializer,
        context={'user': registration.user}
    )
    notify_group(group, response)


def notify_user_payment(action_type, registration, **kwargs):
    group = group_for_user(registration.user)
    kwargs['event_id'] = registration.event.id
    response = socket_response_creator(
        action_type, registration, kwargs, RegistrationPaymentReadSerializer,
        context={'user': registration.user}
    )
    notify_group(group, response)


def notify_user_registration(action_type, registration, **kwargs):
    group = group_for_user(registration.user)
    kwargs['event_id'] = registration.event.id
    response = socket_response_creator(
        action_type, registration, kwargs, RegistrationReadSerializer,
        context={'user': registration.user}
    )

    notify_group(group, response)


def notify_event_updated(event, **kwargs):
    group = group_for_event(event)
    response = socket_response_creator('SOCKET_EVENT_UPDATED', event, kwargs, EventReadDetailedSerializer)

    notify_group(group, response)
