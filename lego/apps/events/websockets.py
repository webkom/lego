from datetime import datetime

from channels import Group

from lego.apps.events.serializers import EventReadDetailedBaseSerializer, RegistrationReadSerializer
from lego.apps.permissions.filters import filter_queryset
from lego.apps.websockets.handlers import group_for_user
from lego.apps.websockets.notifiers import notify_group

from .models import Event


def get_group_for_event(event):
    return Group('event-{0}'.format(event.pk))


def get_group_for_registration(registration):
    return Group('registration-{0}'.format(registration.pk))


def find_event_groups(user):
    """
    Find all channels groups the user belongs to as a result
    of being signed up to future events.
    """
    after_now = Event.objects.filter(start_time__gt=datetime.now())
    queryset = filter_queryset(user, after_now)
    groups = []
    for event in queryset.all():
        groups.append(get_group_for_event(event))

    return groups


def notify_registration(type, registration):
    group = group_for_user(registration.user)
    serializer = RegistrationReadSerializer(registration)
    notify_group(group, {
        'type': type,
        'payload': serializer.data
    })


def notify_unregistration(type, registration, pool_id):
    group = group_for_user(registration.user)
    serializer = RegistrationReadSerializer(registration)
    payload = serializer.data
    payload['from_pool'] = pool_id
    notify_group(group, {
        'type': type,
        'payload': payload
    })


def event_updated_notifier(event):
    group = get_group_for_event(event)
    serializer = EventReadDetailedBaseSerializer(event)
    notify_group(group, {
        'type': 'EVENT_UPDATED',
        'payload': serializer.data
    })
