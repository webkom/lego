from datetime import datetime

from lego.apps.events.models import Event
from lego.apps.events.serializers import EventReadDetailedSerializer, RegistrationReadSerializer
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
    notify_registration(group, type, registration, from_pool)


def notify_user_registration(type, registration, error_msg=None):
    group = group_for_user(registration.user)
    context = {'registration': registration.id}
    notify_registration(group, type, registration, error_msg=error_msg, context=context)


def notify_registration(group, type, registration, from_pool=None, error_msg=None, context=None):
    payload = RegistrationReadSerializer(registration, context=context).data
    meta = {}
    if from_pool:
        payload['from_pool'] = from_pool
    if error_msg:
        meta['error_message'] = error_msg

    notify_group(group, {
        'type': type,
        'payload': payload,
        'meta': meta
    })


def event_updated_notifier(event):
    group = group_for_event(event)
    serializer = EventReadDetailedSerializer(event)
    notify_group(group, {
        'type': 'EVENT_UPDATED',
        'payload': serializer.data
    })
