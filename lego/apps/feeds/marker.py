class MarkerModelMixin:
    """
    The marker model mixin is responsible for storing unseen and unread counts.
    """

    @classmethod
    def count_unseen(cls, feed_id):
        return 0

    @classmethod
    def count_unread(cls, feed_id):
        return 0

    @classmethod
    def get_notification_data(cls, feed_id):
        return {'unseen_count': 0, 'unread_count': 0}
