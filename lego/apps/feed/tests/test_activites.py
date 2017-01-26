from django.test import TestCase
from django.utils.timezone import make_naive, now
from stream_framework.verbs.base import Comment as CommentVerb

from lego.apps.articles.models import Article
from lego.apps.comments.models import Comment
from lego.apps.feed.activities import Activity
from lego.apps.users.models import User


class ActivityTestCase(TestCase):

    fixtures = ['test_abakus_groups.yaml', 'test_users.yaml', 'test_articles.yaml']

    def setUp(self):
        self.user = User.objects.get(id=1)
        self.article = Article.objects.get(id=2)
        self.comment = Comment.objects.create(
            content_object=self.article, created_by=self.user, text='comment'
        )
        self.test_time = now()

    def test_create_activity(self):
        """Check that the objects gets stored as content_strings."""
        activity = Activity(
            actor=self.user,
            verb=CommentVerb,
            object=self.comment,
            target=self.article,
            extra_context={
                'content': self.comment.text
            }
        )

        self.assertEqual(activity.actor, 'users.user-1')
        self.assertEqual(activity.object, 'comments.comment-{comment_id}'.format(
            comment_id=self.comment.id))
        self.assertEqual(activity.target, 'articles.article-2')
        self.assertEqual(activity.verb, CommentVerb)

    def test_create_activity_with_time(self):
        """Check the time storage. The time should be naive."""
        activity = Activity(
            time=self.test_time,
            actor=self.user,
            verb=CommentVerb,
            object=self.comment,
            extra_context={
                'content': self.comment.text
            }
        )

        self.assertEqual(activity.time, make_naive(self.test_time))
