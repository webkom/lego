from datetime import datetime

from lego.apps.events.models import Event
from lego.apps.events.serializers import (EventReadDetailedSerializer,
                                          RegistrationPaymentReadSerializer,
                                          RegistrationReadSerializer)
from lego.apps.permissions.filters import filter_queryset
from lego.apps.websockets.groups import group_for_event, group_for_user
from lego.apps.websockets.notifiers import notify_group


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


def notify_event_registration(type, registration, from_pool=None):
    group = group_for_event(registration.event)
    payload = RegistrationReadSerializer(registration).data
    if from_pool:
        payload['from_pool'] = from_pool
    notify_registration(group, type, payload, registration)


def notify_user_registration(type, registration, error_msg=None):
    group = group_for_user(registration.user)
    if registration.event.is_priced:
        payload = RegistrationPaymentReadSerializer(
            registration, context={'user': registration.user}
        ).data
    else:
        payload = RegistrationReadSerializer(
            registration, context={'user': registration.user}
        ).data
    notify_registration(group, type, payload, registration, error_msg)


def notify_registration(group, type, payload, registration, error_msg=None):
    meta = {
        'event_id': registration.event.id
    }
    if error_msg:
        meta['error_message'] = error_msg

    notify_group(group, {
        'type': type,
        'payload': payload,
        'meta': meta
    })


def event_updated_notifier(event, error_msg=None):
    group = group_for_event(event)
    payload = EventReadDetailedSerializer(event).data
    meta = {}
    if error_msg:
        meta['error_message'] = error_msg
    notify_group(group, {
        'type': 'SOCKET_EVENT_UPDATED',
        'payload': payload,
        'meta': meta
    })
