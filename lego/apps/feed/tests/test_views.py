'''
from unittest import mock

from rest_framework import status
from rest_framework.test import APITestCase
from stream_framework.storage.redis.connection import get_redis_connection
from stream_framework.verbs.base import Comment as CommentVerb

from lego.apps.articles.models import Article
from lego.apps.comments.models import Comment
from lego.apps.feed import activities, managers
from lego.apps.users.models import User


class NotificationViewsTestCase(APITestCase):

    fixtures = ['test_abakus_groups.yaml', 'test_users.yaml', 'test_articles.yaml']

    def setUp(self):
        self.url = '/api/v1/notifications/'
        self.user = User.objects.get(id=1)
        self.second_user = User.objects.get(id=2)
        self.article = Article.objects.get(id=2)
        self.comment = Comment.objects.create(
            content_object=self.article, created_by=self.user, text='comment'
        )

        get_redis_connection().flushdb()
        self.activity = activities.Activity(
            actor=self.user,
            verb=CommentVerb,
            object=self.comment,
            target=self.article
        )
        #managers.notification_feed_manager.add_activity([1, 2], self.activity)

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

    @mock.patch('lego.apps.feed.feeds.NotificationFeed.mark_all')
    def test_mark_all(self, mock_mark_all):
        """Try to mark all items in feed as seen and read."""
        self.client.force_login(self.user)
        response = self.client.post(
            '{url}mark_all/'.format(url=self.url), data={'read': True, 'seen': True}
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        mock_mark_all.assert_called_once_with(read=True, seen=True)

    @mock.patch('lego.apps.feed.feeds.NotificationFeed.mark_activity')
    def test_mark(self, mock_mark_activity):
        """Try to mark a activity in feed as seen and read."""
        self.client.force_login(self.user)

        response = self.client.post(
            '{url}{activity_id}/mark/'.format(
                activity_id=10,
                url=self.url
            ), data={'read': True, 'seen': True}
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        mock_mark_activity.assert_called_once_with('10', read=True, seen=True)
'''
