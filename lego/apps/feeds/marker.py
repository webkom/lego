from lego.apps.feeds.storage import RedisListStorage


class MarkerModelMixin:
    """
    The marker model mixin is responsible for storing unseen and unread counts.
    """

    @classmethod
    def mark_all(cls, feed_id, seen, read):
        """
        Mark every activity in the feed.
        """
        args = []
        if seen:
            args.append("unseen")
        if read:
            args.append("unread")
        if args:
            RedisListStorage(feed_id).flush(*args)

    @classmethod
    def mark_activities(cls, feed_id, activities, seen, read):
        """
        Mark a set of activity ids.
        """
        activities = [str(activity) for activity in activities]
        if not activities:
            return

        kwargs = {}
        if seen:
            kwargs["unseen"] = activities
        if read:
            kwargs["unread"] = activities
        if kwargs:
            RedisListStorage(feed_id).remove(**kwargs)

    @classmethod
    def mark_activity(cls, feed_id, activity, seen, read):
        cls.mark_activities(feed_id, [activity], seen, read)

    @classmethod
    def mark_insert_activity(cls, feed_id, activity):
        RedisListStorage(feed_id).add(unseen=[str(activity)], unread=[str(activity)])

    @classmethod
    def get_notification_data(cls, feed_id):
        unseen, unread = RedisListStorage(feed_id).count("unseen", "unread")
        return {"unseen_count": unseen, "unread_count": unread}

    def _activity_ids(self):
        return {str(activity.activity_id) for activity in self.activities}

    def _is_cleared(self, list_name):
        marked = set(RedisListStorage(self.feed_id).get(list_name))
        return marked.isdisjoint(self._activity_ids())

    @property
    def is_seen(self):
        return self._is_cleared("unseen")

    @property
    def is_read(self):
        return self._is_cleared("unread")
