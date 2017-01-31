from datetime import datetime, timedelta

from rest_framework import status
from rest_framework.test import APITestCase
from stream_framework.storage.redis.connection import get_redis_connection
from stream_framework.verbs.base import Comment as CommentVerb

from lego.apps.articles.models import Article
from lego.apps.comments.models import Comment
from lego.apps.feed.activities import Activity
from lego.apps.feed.feed_manager import feed_manager
from lego.apps.feed.feeds.notification_feed import NotificationFeed
from lego.apps.feed.tests.feed_test_base import FeedTestBase
from lego.apps.users.models import User


class NotificationViewsTestCase(APITestCase, FeedTestBase):

    fixtures = ['test_abakus_groups.yaml', 'test_users.yaml', 'test_articles.yaml']

    def setUp(self):
        self.url = '/api/v1/feed/notifications/'

        self.user = User.objects.get(id=1)
        self.second_user = User.objects.get(id=2)
        self.article1 = Article.objects.get(id=2)
        self.article2 = Article.objects.get(id=3)
        comment1 = Comment.objects.create(
            content_object=self.article1, text='comment 1'
        )
        comment2 = Comment.objects.create(
            content_object=self.article2, text='comment 2'
        )

        get_redis_connection().flushdb()
        # Activity 1 and 2 get the same aggregation group.
        self.activity1 = Activity(
            actor=User.objects.get(id=3),
            verb=CommentVerb,
            object=comment1,
            target=comment1.content_object,
            time=datetime.now()-timedelta(minutes=1)
        )
        self.activity2 = Activity(
            actor=User.objects.get(id=3),
            verb=CommentVerb,
            object=comment1,
            target=comment1.content_object,
            time=datetime.now() - timedelta(minutes=2)
        )
        self.activity3 = Activity(
            actor=User.objects.get(id=4),
            verb=CommentVerb,
            object=comment2,
            target=comment2.content_object,
            time=datetime.now()
        )
        feed_manager.add_activity(self.activity1, [1, 2], [NotificationFeed])

    def test_list_notifications(self):
        """Try to list user notifications."""
        def test_for_user(user, expected_length=1):
            self.client.force_login(user)
            response = self.client.get(self.url)
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            result = response.json()['results']
            self.assertEqual(len(result), expected_length)

        test_for_user(self.user)
        test_for_user(self.second_user)
        test_for_user(User.objects.get(id=3), expected_length=0)

    def test_notification_data(self):
        self.client.force_login(self.user)

        res = self.client.get(f'{self.url}notification_data/')
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        res = res.json()
        self.assertEqual(res['unseenCount'], 1)
        self.assertEqual(res['unreadCount'], 1)

        feed_manager.add_activity(self.activity2, [1], [NotificationFeed])
        res = self.client.get(f'{self.url}notification_data/').json()
        self.assertEqual(res['unseenCount'], 1)
        self.assertEqual(res['unreadCount'], 1)

        feed_manager.add_activity(self.activity3, [1], [NotificationFeed])
        res = self.client.get(f'{self.url}notification_data/').json()
        self.assertEqual(res['unseenCount'], 2)
        self.assertEqual(res['unreadCount'], 2)

    def test_mark(self):
        self.client.force_login(self.user)
        feed_manager.add_activity(self.activity3, [1], [NotificationFeed])
        res = self.client.get(f'{self.url}notification_data/').json()
        self.assertEqual(res['unseenCount'], 2)
        self.assertEqual(res['unreadCount'], 2)

        notifications = self.client.get(f'{self.url}').json()['results']
        self.assertEqual(len(notifications), 2)

        '''
            Test marking as seen and read
        '''
        res = self.client.post(f'{self.url}{notifications[0]["id"]}/mark/', data=dict(
            seen=True
        ))
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        res = self.client.get(f'{self.url}notification_data/').json()
        self.assertEqual(res['unseenCount'], 1)
        self.assertEqual(res['unreadCount'], 2)

        res = self.client.post(f'{self.url}{notifications[0]["id"]}/mark/', data=dict(
            read=True
        ))
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        res = self.client.get(f'{self.url}notification_data/').json()
        self.assertEqual(res['unseenCount'], 1)
        self.assertEqual(res['unreadCount'], 1)

        '''
            Cannot unsee or unread
        '''
        res = self.client.post(f'{self.url}{notifications[0]["id"]}/mark/', data=dict(
            seen=False,
            read=False
        ))
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        res = self.client.get(f'{self.url}notification_data/').json()
        self.assertEqual(res['unseenCount'], 1)
        self.assertEqual(res['unreadCount'], 1)

        '''
            Test marking as both seen and read
        '''
        res = self.client.post(f'{self.url}{notifications[1]["id"]}/mark/', data=dict(
            seen=True,
            read=True
        ))
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        res = self.client.get(f'{self.url}notification_data/').json()
        self.assertEqual(res['unseenCount'], 0)
        self.assertEqual(res['unreadCount'], 0)

    def test_mark_all(self):
        self.client.force_login(self.user)
        res = self.client.get(f'{self.url}notification_data/').json()
        self.assertEqual(res['unseenCount'], 1)
        self.assertEqual(res['unreadCount'], 1)

        feed_manager.add_activity(self.activity3, [1], [NotificationFeed])
        res = self.client.get(f'{self.url}notification_data/').json()
        self.assertEqual(res['unseenCount'], 2)
        self.assertEqual(res['unreadCount'], 2)

        res = self.client.post(f'{self.url}mark_all/', data=dict(
            seen=True
        ))
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        res = self.client.get(f'{self.url}notification_data/').json()
        self.assertEqual(res['unseenCount'], 0)
        self.assertEqual(res['unreadCount'], 2)

        res = self.client.post(f'{self.url}mark_all/', data=dict(
            seen=True,
            read=True
        ))
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        res = self.client.get(f'{self.url}notification_data/').json()
        self.assertEqual(res['unseenCount'], 0)
        self.assertEqual(res['unreadCount'], 0)


class GroupFeedViewsTestCase(APITestCase, FeedTestBase):
    '''
    TODO: Test permissions for group feeds before granting users access
    '''
    pass
