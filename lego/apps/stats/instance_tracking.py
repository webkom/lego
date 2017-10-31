from lego.apps.events.constants import SUCCESS_REGISTER, SUCCESS_UNREGISTER
from lego.apps.events.models import Registration
from lego.apps.users.models import Membership, User

from .utils import group, identify, track


def track_instance(instance):
    """
    This function creates some of the most common events for BI statistics.
    """

    if isinstance(instance, User):
        # Identify users after profile updates.
        identify(instance)
    elif isinstance(instance, Membership):
        # Track membership in a group
        group(instance)
    elif isinstance(instance, Registration):
        # Track event registrations
        if instance.status not in [SUCCESS_REGISTER, SUCCESS_UNREGISTER]:
            return

        event = instance.event
        pool = instance.pool

        registered = not(pool is None and instance.unregistration_date)

        properties = {
            'id': instance.id,
            'has_paid': instance.has_paid(),
            'presence': instance.presence,
            'waiting_list': pool is None and instance.unregistration_date is None,
            'event_id': event.id,
            'event_title': event.title,
            'event_type': event.event_type,
            'event_start_time': event.start_time.isoformat(),
            'event_company': event.company_id,
            'event_is_priced': event.is_priced,
            'event_use_stripe': event.use_stripe,
        }

        if pool:
            properties.update({
                'pool_capacity': pool.capacity,
                'pool_spots_left': pool.spots_left(),
                'pool_id': pool.id
            })
        else:
            properties.update({
                'pool_capacity': 0,
                'pool_spots_left': 0,
                'pool_id': None
            })

        earliest_registration = event.get_earliest_registration_time(instance.user)
        if earliest_registration and instance.registration_date:
            properties['seconds_after_opening'] = \
                int((instance.registration_date - earliest_registration).total_seconds())

        if registered:
            track(instance.user, 'event_register', properties)
        else:
            if event.start_time and instance.unregistration_date:
                properties['seconds_before_start'] = \
                    int((event.start_time - instance.unregistration_date).total_seconds())
            track(instance.user, 'event_unregister', properties)
