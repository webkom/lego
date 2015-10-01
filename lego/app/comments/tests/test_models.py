from django.test import TestCase

from lego.app.comments.models import Comment
from lego.users.models import User


class CommentTestCase(TestCase):

    def setUp(self):
        # Should be changed to an article/event or similar:
        self.target = User.objects.create(username='target')

        self.author = User.objects.create(username='comment_author')

        self.test_comment = Comment.objects.create(content='test', author=self.author,
                                                   content_object=self.target)

    def test_creation(self):
        created_comment = Comment.objects.get(content='test')

        self.assertEqual(created_comment.content_object, self.target)
        self.assertEqual(created_comment.author, self.author)

    def test_str(self):
        output = str(self.test_comment)
        formatted = '{0} - {1}'.format(self.test_comment.author, self.test_comment.content[:30])
        self.assertEqual(output, formatted)
