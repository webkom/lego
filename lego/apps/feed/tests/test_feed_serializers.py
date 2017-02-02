
from datetime import datetime

from django.test import TestCase
from stream_framework.verbs.base import Comment as CommentVerb

from lego.apps.articles.models import Article
from lego.apps.comments.models import Comment
from lego.apps.feed.activities import Activity, AggregatedActivity
from lego.apps.feed.feed_serializers import AggregatedActivitySerializer
from lego.apps.feed.feeds.notification_feed import NotificationFeed
from lego.apps.users.models import User


class FeedActivitySerializerTestCase(TestCase):

    fixtures = ['test_abakus_groups.yaml', 'test_users.yaml', 'test_articles.yaml']

    def setUp(self):
        self.user = User.objects.get(id=1)
        self.article = Article.objects.get(id=2)
        self.comment = Comment.objects.create(
            content_object=self.article, created_by=self.user, text='comment'
        )

        self.activity = Activity(
            actor=self.user,
            verb=CommentVerb,
            object=self.comment,
            target=self.article,
            extra_context={
                'content': self.comment.text
            }
        )
        self.aggregated_activity = AggregatedActivity(
            'test-group', [self.activity],
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )

        self.aggregated_serializer = AggregatedActivitySerializer(
            aggregated_activity_class=AggregatedActivity,
            activity_class=Activity,
            model=NotificationFeed.get_timeline_storage().model
        )

    def test_aggregated_serializer(self):
        """Check if the relevant variables gets restored."""
        serialized = self.aggregated_serializer.dumps(self.aggregated_activity)
        deserialized = self.aggregated_serializer.loads(serialized)

        self.assertEqual(deserialized.group, self.aggregated_activity.group)
        self.assertEqual(deserialized.created_at, self.aggregated_activity.created_at)
        self.assertEqual(deserialized.updated_at, self.aggregated_activity.updated_at)
        self.assertEqual(deserialized.serialization_id, self.aggregated_activity.serialization_id)
        self.assertEqual(deserialized.last_activities, self.aggregated_activity.last_activities)
