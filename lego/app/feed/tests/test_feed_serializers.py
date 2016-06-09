from datetime import datetime

from django.test import TestCase
from stream_framework.verbs.base import Comment as CommentVerb

from lego.app.articles.models import Article
from lego.app.comments.models import Comment
from lego.app.feed.activities import FeedActivity, FeedAggregatedActivity
from lego.app.feed.feed_serializers import AggregatedFeedSerializer, FeedActivitySerializer
from lego.users.models import User


class FeedActivitySerializerTestCase(TestCase):

    fixtures = ['test_users.yaml', 'test_arcicles.yaml', 'test_comments.yaml']

    user = User.objects.get(id=1)
    article = Article.objects.get(id=2)
    comment = Comment.objects.filter(content_type=21, object_id=article.id).first()

    activity = FeedActivity(
        actor=user,
        verb=CommentVerb,
        object=comment,
        target=article,
        extra_context={
            'content': comment.text
        }
    )
    aggregated_activity = FeedAggregatedActivity(
        'test-group', [activity], created_at=datetime.utcnow(), updated_at=datetime.utcnow()
    )

    serializer = FeedActivitySerializer(FeedActivity)
    aggregated_serializer = AggregatedFeedSerializer(
        aggregated_activity_class=FeedAggregatedActivity,
        activity_class=FeedActivity
    )

    def test_serializer(self):
        """Check if the relevant variables gets restored."""
        serialized = self.serializer.dumps(self.activity)
        deserialized = self.serializer.loads(serialized.decode())

        self.assertEqual(deserialized.time, self.activity.time)
        self.assertEqual(deserialized.verb, self.activity.verb)
        self.assertEqual(deserialized.actor, self.activity.actor)
        self.assertEqual(deserialized.object, self.activity.object)
        self.assertEqual(deserialized.target, self.activity.target)
        self.assertEqual(deserialized.extra_context, self.activity.extra_context)

    def test_aggregated_serializer(self):
        """Check if the relevant variables gets restored."""
        serialized = self.aggregated_serializer.dumps(self.aggregated_activity)
        deserialized = self.aggregated_serializer.loads(serialized.decode())

        self.assertEqual(deserialized.group, self.aggregated_activity.group)
        self.assertEqual(deserialized.created_at, self.aggregated_activity.created_at)
        self.assertEqual(deserialized.updated_at, self.aggregated_activity.updated_at)
        self.assertEqual(deserialized.serialization_id, self.aggregated_activity.serialization_id)
        self.assertEqual(deserialized.last_activities, self.aggregated_activity.last_activities)
