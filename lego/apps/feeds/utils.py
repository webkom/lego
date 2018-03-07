from django.apps import apps

from lego.apps.feeds.activity import Activity
from lego.apps.feeds.constants import ADD, REMOVE
from lego.apps.feeds.models import TimelineStorage


def fanout(operation, activity, recipients, feed):
    """
    Fanout is called in celery task and is responsible for distributing the actions into the
    destination feeds.
    """
    activity = Activity.deserialize(activity)
    feed = apps.get_model('feeds', feed)

    if operation == ADD:
        return add_to_feed(activity, feed, recipients)

    elif operation == REMOVE:
        return remove_from_feed(activity, feed, recipients)

    raise ValueError('Invalid feed operation')


def add_to_feed(activity, feed, recipients):
    """
    Lookup groupings and add the activity to the feed.
    """
    group_search_offset = 20
    print(group_search_offset)


def remove_from_feed(activity, feed, recipients):
    """
    The feed removal function is not optimal, recipients is ignored because we don't store
    the original recipients of the activity.
    """
    aggregated_ids = TimelineStorage.aggregated_ids(activity.activity_id, feed)
    print(aggregated_ids)


def chunks(l, n):
    for i in range(0, len(l), n):
        yield l[i:i + n]
