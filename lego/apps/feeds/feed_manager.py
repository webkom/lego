class FeedManager:

    fanout_chunk_size = 100

    def add_activity(self, activity, recipients, feed_classes):
        pass

    def remove_activity(self, activity, recipients, feed_classes):
        pass

    def retrieve_feed(self, feed_class, feed_id):
        return feed_class.objects.filter(feed_id=str(feed_id))


feed_manager = FeedManager()
