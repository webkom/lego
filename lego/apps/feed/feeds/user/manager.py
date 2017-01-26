from lego.apps.feed.feed_manager import FeedManager
from lego.apps.feed.feeds.user.feed import PersonalFeed, UserFeed


class UserFeedManager(FeedManager):

    def fanout_user_action(self, activity, follower_ids):
        self.add_activity(activity, follower_ids, [PersonalFeed])
        self.add_activity(activity, [activity.actor_id], [UserFeed])
