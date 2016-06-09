from django.test import TestCase
from django.utils.timezone import make_naive, now
from stream_framework.verbs.base import Comment as CommentVerb

from lego.app.articles.models import Article
from lego.app.comments.models import Comment
from lego.app.feed.activities import FeedActivity
from lego.users.models import User


class ActivityTestCase(TestCase):

    fixtures = ['test_users.yaml', 'test_arcicles.yaml', 'test_comments.yaml']

    user = User.objects.get(id=1)
    article = Article.objects.get(id=2)
    comment = Comment.objects.filter(content_type=21, object_id=article.id).first()
    test_time = now()

    def test_create_activity(self):
        """Check that the objects gets stored as content_strings."""
        activity = FeedActivity(
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
        activity = FeedActivity(
            time=self.test_time,
            actor=self.user,
            verb=CommentVerb,
            object=self.comment,
            extra_context={
                'content': self.comment.text
            }
        )

        self.assertEqual(activity.time, make_naive(self.test_time))
