from django.test import TestCase

from lego.apps.feed.activities import Activity
from lego.apps.feed.feeds.user.feed import UserFeed
from lego.apps.feed.verbs import CommentVerb


class FeedTestBase(TestCase):

    def setUp(self):
        self.feed = UserFeed(1)

    def test_add_action(self):
        for i in range(100):
            activity = Activity(f'users.user-{i+2}', CommentVerb, 'comments.comment-4',
                                'events.event-2')
            self.feed.add(activity)

    def test_list_activities(self):
        activities = self.feed[:500000]
        print(activities)
