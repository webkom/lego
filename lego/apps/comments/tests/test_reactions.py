from lego.apps.articles.models import Article
from lego.apps.comments.models import Comment
from lego.apps.emojis.models import Emoji
from lego.apps.reactions.models import Reaction
from lego.apps.users.models import User
from lego.utils.test_utils import BaseTestCase


class CommentReactionsTestCase(BaseTestCase):
    fixtures = [
        "test_abakus_groups.yaml",
        "test_users.yaml",
        "test_emojis.yaml",
        "test_articles.yaml",
    ]

    def setUp(self):
        self.comment = Comment.objects.create(
            created_by_id=0,
            text="first comment",
            content_object=Article.objects.all().first(),
        )
        self.user = User.objects.all().first()
        self.comment.created_by = self.user
        self.comment.save()

        self.emoji = Emoji.objects.first()

    def test_add_reaction(self):
        test_reaction = Reaction.objects.create(
            content_object=self.comment, emoji=self.emoji
        )
        test_reaction.created_by = self.user
        test_reaction.save()

        reactions_grouped = self.comment.get_reactions_grouped(self.user)
        self.assertEqual(len(reactions_grouped), 1)
        self.assertEqual(reactions_grouped[0]["count"], 1)
        self.assertEqual(reactions_grouped[0]["has_reacted"], True)
        self.assertEqual(
            reactions_grouped[0]["unicode_string"], self.emoji.unicode_string
        )

    def test_remove_reaction(self):
        test_reaction = Reaction.objects.create(
            content_object=self.comment, emoji=self.emoji
        )

        reactions_grouped = self.comment.get_reactions_grouped(self.user)
        self.assertEqual(len(reactions_grouped), 1)
        self.assertEqual(reactions_grouped[0]["count"], 1)

        test_reaction.delete()

        reactions_grouped = self.comment.get_reactions_grouped(self.user)
        self.assertEqual(len(reactions_grouped), 0)
