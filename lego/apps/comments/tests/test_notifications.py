from unittest.mock import patch

from lego.apps.articles.models import Article
from lego.apps.comments.models import Comment
from lego.apps.comments.notifications import CommentReplyNotification
from lego.apps.users.models import User
from lego.utils.test_utils import BaseTestCase


@patch("lego.utils.email.django_send_mail")
class CommentReplyNotificationTestCase(BaseTestCase):
    fixtures = [
        "test_abakus_groups.yaml",
        "test_comments.yaml",
        "test_users.yaml",
        "test_articles.yaml",
        "initial_files.yaml",
    ]

    def setUp(self):
        self.author = User.objects.all().first()
        self.recipient = User.objects.all()[1]
        self.article = Article.objects.all().first()
        self.comment = Comment.objects.all().first()
        self.comment.created_by = self.author
        self.comment.object_id = self.article.pk
        self.comment.save()
        self.notifier = CommentReplyNotification(
            user=self.recipient,
            author=self.author,
            text=self.comment.text,
            target=self.article,
        )

    def assertEmailContains(self, send_mail_mock, content):
        self.notifier.generate_mail()
        email_args = send_mail_mock.call_args[1]
        self.assertIn(content, email_args["message"])
        self.assertIn(content, email_args["html_message"])

    def test_generate_email_comment(self, send_mail_mock):
        comment = self.comment.text
        self.assertEmailContains(send_mail_mock, comment)

    def test_generate_email_content(self, send_mail_mock):
        content = (
            self.author.first_name
            + " "
            + self.author.last_name
            + " har svart på din kommentar på "
            + self.article.title
            + ":"
        )
        self.assertEmailContains(send_mail_mock, content)

    def test_generate_email_name(self, send_mail_mock):
        opening = "Hei, " + self.recipient.first_name + "!"
        self.assertEmailContains(send_mail_mock, opening)

    def test_generate_email_url(self, send_mail_mock):
        url = self.article.get_absolute_url()
        self.assertEmailContains(send_mail_mock, url)
