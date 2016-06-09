from unittest import mock

from rest_framework import status
from rest_framework.test import APITestCase
from stream_framework.storage.redis.connection import get_redis_connection
from stream_framework.verbs.base import Comment as CommentVerb

from lego.app.articles.models import Article
from lego.app.comments.models import Comment
from lego.app.feed import activities, managers
from lego.users.models import User


class NotificationViewsTestCase(APITestCase):

    fixtures = ['test_users.yaml', 'test_arcicles.yaml', 'test_comments.yaml']

    url = '/api/v1/notifications/'
    user = User.objects.get(id=1)
    second_user = User.objects.get(id=2)
    article = Article.objects.get(id=2)
    comment = Comment.objects.filter(content_type=21, object_id=article.id).first()

    def setUp(self):
        get_redis_connection().flushdb()
        self.activity = activities.FeedActivity(
            actor=self.user,
            verb=CommentVerb,
            object=self.comment,
            target=self.article
        )
        managers.notification_feed_manager.add_activity([1, 2], self.activity)

    def test_list_notifications(self):
        """Try to list user notifications."""
        def test_for_user(user):
            self.client.force_login(user)
            response = self.client.get(self.url)
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            result = response.json()['results']
            self.assertEqual(len(result), 1)

        test_for_user(self.user)
        test_for_user(self.second_user)

    @mock.patch('lego.app.feed.feeds.NotificationFeed.mark_all')
    def test_mark_all(self, mock_mark_all):
        """Try to mark all items in feed as seen and read."""
        self.client.force_login(self.user)
        response = self.client.post(
            '{url}mark_all/'.format(url=self.url), data={'read': True, 'seen': True}
        )

        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)
        mock_mark_all.assert_called_once_with(True, True)

    @mock.patch('lego.app.feed.feeds.NotificationFeed.mark_activity')
    def test_mark(self, mock_mark_activity):
        """Try to mark a activity in feed as seen and read."""
        self.client.force_login(self.user)

        response = self.client.post(
            '{url}{activity_id}/mark/'.format(
                activity_id=10,
                url=self.url
            ), data={'read': True, 'seen': True}
        )

        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)
        mock_mark_activity.assert_called_once_with('10', True, True)
