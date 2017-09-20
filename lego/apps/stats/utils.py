from structlog import get_logger

from .analytics_client import track as analytics_track

log = get_logger()


def track(user, event, properties=None):
    """
    Track events as log messages and analytics events.
    """
    properties = properties if properties else {}
    user_id = user.id if user.is_authenticated else 'anonymous'

    # Send events to the analytics pipeline.
    analytics_track(user, event, properties)

    # Output the event as a log message.
    log.info(event, {'user_id': user_id, **properties})
