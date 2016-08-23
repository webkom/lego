from django.test import TestCase
from stream_framework.verbs.base import Comment as CommentVerb
from stream_framework.verbs.base import Verb, register

from lego.app.articles.models import Article
from lego.app.comments.models import Comment
from lego.app.feed import activities, aggregator
from lego.users.models import User


class AggregatorTestCase(TestCase):

    fixtures = ['test_abakus_groups.yaml', 'test_users.yaml', 'test_articles.yaml']

    def setUp(self):
        self.user = User.objects.get(id=1)
        self.article = Article.objects.get(id=2)
        self.comment = Comment.objects.filter(content_type=21, object_id=self.article.id).first()
        self.aggregator = aggregator.FeedAggregator()

    def test_get_group(self):
        """Check the default group generation."""
        activity = activities.FeedActivity(
            actor=self.user,
            verb=CommentVerb,
            object=self.comment,
            target=self.article
        )

        group = self.aggregator.get_group(activity)
        # Default format: verb_id object_id object_content type-date
        self.assertEqual(group, '2-2-articles.article-{date}'.format(date=activity.time.date()))

    def test_custom_grouping(self):
        """Check the custom group aggregate."""

        class TestVerb(Verb):
            id = 999
            infinitive = 'test'
            past_tense = infinitive
            aggregation_group = '{verb}-{target_id}'

        register(TestVerb)

        activity = activities.FeedActivity(
            actor=self.user,
            verb=TestVerb,
            object=self.comment,
            target=self.article
        )

        group = self.aggregator.get_group(activity)
        self.assertEqual(group, '999-2')
