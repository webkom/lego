ADD = 'add'
REMOVE = 'remove'


class FeedManager:

    fanout_chunk_size = 100

    def add_activity(self, activity, recipients, feed_classes):
        for feed in feed_classes:
            self._feed_operation(ADD, activity, set(recipients), feed)

    def remove_activity(self, activity, recipients, feed_classes):
        for feed in feed_classes:
            self._feed_operation(REMOVE, activity, set(recipients), feed)

    def retrieve_feed(self, feed_class, feed_id):
        return feed_class.objects.filter(feed_id=str(feed_id))

    def _feed_operation(self, operation, activity, recipients, feed):
        """
        Divide the fanout task into multiple celery tasks
        """
        pass


feed_manager = FeedManager()
