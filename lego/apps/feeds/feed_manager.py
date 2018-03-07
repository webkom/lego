from lego.apps.feeds.constants import ADD, REMOVE

from .tasks import feed_fanout
from .utils import chunks


class FeedManager:

    fanout_chunk_size = 10

    def add_activity(self, activity, recipients, feed_classes):
        for feed in feed_classes:
            self._feed_operation(ADD, activity, set(recipients), feed)

    def remove_activity(self, activity, recipients, feed_classes):
        """
        The remove action ignores the recipient, the recipients argument is unused.
        """
        for feed in feed_classes:
            self._feed_operation(REMOVE, activity, set(), feed)

    def retrieve_feed(self, feed_class, feed_id):
        return feed_class.objects.filter(feed_id=str(feed_id))

    def _feed_operation(self, operation, activity, recipients, feed):
        """
        Divide the fanout task into multiple celery tasks
        """

        recipient_chunks = chunks(list(recipients), self.fanout_chunk_size)
        for chunk in recipient_chunks:
            feed_fanout.delay(operation, activity.serialize(), chunk, feed._meta.model_name)


feed_manager = FeedManager()
