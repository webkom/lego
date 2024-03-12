from django.urls import reverse
from rest_framework import status

from lego.apps.comments.models import Comment
from lego.apps.forums.models import Forum, Thread
from lego.apps.users.models import AbakusGroup, User
from lego.utils.test_utils import BaseAPITestCase


# Helper Functions
def get_forum_list_url():
    return reverse("api:v1:forum-list")


def get_forum_detail_url(pk):
    return reverse("api:v1:forum-detail", kwargs={"pk": pk})


def create_forum(**kwargs):
    return Forum.objects.create(
        title="Test Forum", description="Discussion forum", **kwargs
    )


def get_comment_list_url():
    return reverse("api:v1:comment-list")


def create_comment(thread, text="Test comment"):
    return Comment.objects.create(content_object=thread, text=text)


def create_thread(forum, **kwargs):
    return Thread.objects.create(
        title="Sample Thread",
        description="A thread in a forum",
        forum=forum,
        **kwargs,
    )


# Test Cases
class ForumTestCase(BaseAPITestCase):
    fixtures = ["test_abakus_groups.yaml", "test_users.yaml", "test_articles.yaml"]

    def setUp(self):
        self.all_comments = Comment.objects.all()
        self.all_users = User.objects.all()
        self.with_permission = self.all_users.get(username="useradmin_test")
        self.comments_test_group = AbakusGroup.objects.get(name="CommentTest")
        self.comments_test_group.add_user(self.with_permission)
        self.without_permission = self.all_users.exclude(
            pk=self.with_permission.pk
        ).first()
        self.forum = create_forum()

    def test_forum_creation(self):
        self.client.force_authenticate(self.with_permission)
        self.assertEqual(Forum.objects.count(), 1)
        self.assertEqual(Forum.objects.first(), self.forum)

    def test_forum_list_view(self):
        response = self.client.get(get_forum_list_url())
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_forum_detail_view_unauthenticated(self):
        self.client.force_authenticate(self.without_permission)
        response = self.client.get(get_forum_detail_url(self.forum.pk))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_forum_detail_view_authenticated(self):
        self.client.force_authenticate(user=self.with_permission)
        response = self.client.get(get_forum_detail_url(self.forum.pk))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["id"], self.forum.pk)


class ThreadTestCase(BaseAPITestCase):
    fixtures = ["test_abakus_groups.yaml", "test_users.yaml", "test_articles.yaml"]

    def setUp(self):
        self.all_users = User.objects.all()
        self.with_permission = self.all_users.get(username="useradmin_test")
        self.comments_test_group = AbakusGroup.objects.get(name="CommentTest")
        self.comments_test_group.add_user(self.with_permission)
        self.forum = create_forum()

    def test_thread_creation(self):
        self.client.force_authenticate(self.with_permission)
        thread = create_thread(self.forum)
        self.assertEqual(Thread.objects.count(), 1)
        self.assertEqual(Thread.objects.first(), thread)


class CommentTestCase(BaseAPITestCase):
    fixtures = ["test_abakus_groups.yaml", "test_users.yaml", "test_articles.yaml"]

    def setUp(self):
        self.all_users = User.objects.all()

        self.with_permission = self.all_users.get(username="useradmin_test")
        self.comments_test_group = AbakusGroup.objects.get(name="CommentTest")
        self.comments_test_group.add_user(self.with_permission)
        self.forum = create_forum()
        self.thread = create_thread(self.forum)

    def test_post_comment_to_thread(self):
        self.client.force_authenticate(user=self.with_permission)
        comment_data = {
            "text": "Test comment",
            "content_target": f"forums.thread-{self.thread.id}",
        }
        response = self.client.post(get_comment_list_url(), comment_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Comment.objects.count(), 1)
        self.assertEqual(Comment.objects.first().text, "Test comment")


class AccessAndPermissionTestCase(BaseAPITestCase):
    fixtures = ["test_abakus_groups.yaml", "test_users.yaml", "test_articles.yaml"]

    def setUp(self):
        self.all_users = User.objects.all()

        self.with_permission = self.all_users.get(username="useradmin_test")
        self.comments_test_group = AbakusGroup.objects.get(name="CommentTest")
        self.comments_test_group.add_user(self.with_permission)
        self.without_permission = self.all_users.exclude(
            pk=self.with_permission.pk
        ).first()
        self.forum = create_forum()
        self.thread = create_thread(self.forum)
        self.comment = create_comment(thread=self.thread)

    def test_forum_access_unauthenticated_user(self):
        response = self.client.get(get_forum_list_url())
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_forum_access_authenticated_user(self):
        self.client.force_authenticate(user=self.with_permission)
        response = self.client.get(get_forum_list_url())
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_thread_access_unauthenticated_user(self):
        response = self.client.get(get_forum_detail_url(self.forum.id))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_thread_access_authenticated_user(self):
        self.client.force_authenticate(user=self.with_permission)
        response = self.client.get(get_forum_detail_url(self.forum.id))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_post_comment_unauthenticated_user(self):
        comment_data = {
            "text": "Test comment",
            "content_target": f"forums.thread-{self.thread.id}",
        }
        response = self.client.post(get_comment_list_url(), comment_data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_post_comment_authenticated_user(self):
        self.client.force_authenticate(user=self.with_permission)
        comment_data = {
            "text": "Test comment",
            "content_target": f"forums.thread-{self.thread.id}",
        }
        response = self.client.post(get_comment_list_url(), comment_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
