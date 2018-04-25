from lego.apps.feeds.storage import RedisListStorage


class MarkerModelMixin:
    """
    The marker model mixin is responsible for storing unseen and unread counts.
    """

    @classmethod
    def mark_all(cls, feed_id, seen, read):
        storage = RedisListStorage(feed_id)
        args = []
        if seen:
            args.append('unseen')
        if read:
            args.append('unread')
        storage.flush(*args)

    @classmethod
    def mark_activity(cls, feed_id, activity, seen, read):
        storage = RedisListStorage(feed_id)
        kwargs = {}
        if seen:
            kwargs['unseen'] = [activity]
        if read:
            kwargs['unread'] = [activity]
        storage.remove(**kwargs)

    @classmethod
    def mark_insert_activity(cls, feed_id, activity):
        storage = RedisListStorage(feed_id)
        kwargs = {'unseen': [activity], 'unread': [activity]}
        storage.add(**kwargs)

    @classmethod
    def get_notification_data(cls, feed_id):
        storage = RedisListStorage(feed_id)
        unseen, unread = storage.count('unseen', 'unread')
        return {'unseen_count': unseen, 'unread_count': unread}
