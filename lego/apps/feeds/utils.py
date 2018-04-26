from django.apps import apps

from lego.apps.feeds.activity import Activity
from lego.apps.feeds.aggregator import FeedAggregator
from lego.apps.feeds.constants import ADD, REMOVE
from lego.apps.feeds.models import TimelineStorage

aggregator = FeedAggregator()


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
    # Search the last x elements for a matching group
    recipients = set(recipients)
    timeline_ids = set()
    group_search_offset = 20
    group = aggregator.get_group(activity)

    existing_aggregated_activities = feed.objects.find_matching_groups(
        group, group_search_offset, recipients
    )

    # Populate existing aggregated activities
    for aggregated_activity in existing_aggregated_activities:
        aggregated_activity.add_activity(activity)
        aggregated_activity.save()
        recipients.remove(aggregated_activity.feed_id)
        timeline_ids.add(aggregated_activity.id)

    # Create new aggregated activity for users that don't have an item already
    activity_ids = feed.create_activities(activity, recipients, group)
    timeline_ids |= set(activity_ids)

    TimelineStorage.add_ids(activity.activity_id, timeline_ids, feed)


def remove_from_feed(activity, feed, recipients):
    """
    The feed removal function is not optimal, recipients is ignored because we don't store
    the original recipients of the activity.

    Lookup aggregated activities in the timeline storage, remove activity and remove the aggregated
    ids from the timeline store.
    """

    aggregated_ids = TimelineStorage.aggregated_ids(activity.activity_id, feed)
    aggregated_activities = feed.objects.filter(id__in=aggregated_ids)
    for aggregated_activity in aggregated_activities:
        aggregated_activity.remove_activity(activity)
        if len(aggregated_activity.activity_store) == 0:
            aggregated_activity.delete()
        else:
            aggregated_activity.save()
    TimelineStorage.remove_ids(activity.activity_id, aggregated_ids, feed)


def chunks(l, n):
    for i in range(0, len(l), n):
        yield l[i:i + n]
