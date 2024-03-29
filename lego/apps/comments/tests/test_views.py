from typing import Iterator

from django.contrib.contenttypes.models import ContentType
from django.urls import reverse
from rest_framework import status

from lego.apps.articles.models import Article
from lego.apps.comments.models import Comment
from lego.apps.users.models import AbakusGroup, User
from lego.utils.test_utils import BaseAPITestCase


def _get_list_url():
    return reverse("api:v1:comment-list")


def _get_detail_url(pk):
    return reverse("api:v1:comment-detail", kwargs={"pk": pk})


class CreateCommentsAPITestCase(BaseAPITestCase):
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

    def test_without_auth(self):
        content_type = ContentType.objects.get_for_model(Article)
        post_data = {
            "text": "Hey",
            "content_target": "{0}.{1}-{2}".format(
                content_type.app_label, content_type.model, Article.objects.first().pk
            ),
        }
        response = self.client.post(_get_list_url(), post_data)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_without_view_permissions(self):
        self.client.force_authenticate(user=self.without_permission)
        post_data = {
            "text": "Hey",
            "content_target": "{0}-{1}".format(
                ContentType.objects.get_for_model(Article).app_label,
                Article.objects.first().pk,
            ),
        }
        response = self.client.post(_get_list_url(), post_data)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_with_view_permissions(self):
        self.client.force_authenticate(user=self.with_permission)
        content_type = ContentType.objects.get_for_model(Article)
        post_data = {
            "text": "Hey",
            "content_target": "{0}.{1}-{2}".format(
                content_type.app_label, content_type.model, Article.objects.first().pk
            ),
        }
        response = self.client.post(_get_list_url(), post_data)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        comment = Comment.objects.get(pk=response.json()["id"])

        self.assertEqual(comment.text, post_data["text"])
        self.assertEqual(comment.created_by.pk, self.with_permission.pk)

    def test_with_empty_text(self):
        self.client.force_authenticate(user=self.with_permission)
        content_type = ContentType.objects.get_for_model(Article)
        post_data = {
            "text": "",
            "content_target": "{0}.{1}-{2}".format(
                content_type.app_label, content_type.model, Article.objects.first().pk
            ),
        }
        response = self.client.post(_get_list_url(), post_data)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_with_empty_text_and_source(self):
        self.client.force_authenticate(user=self.with_permission)
        post_data = {"text": "", "content_target": ""}
        response = self.client.post(_get_list_url(), post_data)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_with_invalid_contenttype(self):
        self.client.force_authenticate(user=self.with_permission)
        content_type = ContentType.objects.get_for_model(Article)
        post_data = {
            "text": "Hey",
            "content_target": "{0}.{1}-{2}".format(
                content_type.app_label + "xyz",
                content_type.model,
                Article.objects.first().pk,
            ),
        }
        response = self.client.post(_get_list_url(), post_data)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_with_invalid_objectid(self):
        self.client.force_authenticate(user=self.with_permission)
        post_data = {
            "text": "Hey",
            "content_target": "{0}-{1}".format(
                ContentType.objects.get_for_model(Article).app_label,
                Article.objects.last().pk + 1000,
            ),
        }
        response = self.client.post(_get_list_url(), post_data)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_with_parent(self):
        self.client.force_authenticate(user=self.with_permission)
        content_type = ContentType.objects.get_for_model(Article)
        content_target = "{0}.{1}-{2}".format(
            content_type.app_label, content_type.model, Article.objects.last().pk
        )

        response = self.client.post(
            _get_list_url(), {"content_target": content_target, "text": "first comment"}
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        pk = response.json()["id"]

        response2 = self.client.post(
            _get_list_url(),
            {"content_target": content_target, "text": "second comment", "parent": pk},
        )
        self.assertEqual(response2.status_code, status.HTTP_201_CREATED)

    def test_with_invalid_parent(self):
        self.client.force_authenticate(user=self.with_permission)
        content_type = ContentType.objects.get_for_model(Article)
        content_target = "{0}.{1}-{2}".format(
            content_type.app_label, content_type.model, Article.objects.last().pk
        )
        content_target_2 = "{0}.{1}-{2}".format(
            content_type.app_label, content_type.model, Article.objects.first().pk
        )

        response = self.client.post(
            _get_list_url(), {"content_target": content_target, "text": "first comment"}
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        pk = response.json()["id"]

        response2 = self.client.post(
            _get_list_url(),
            {
                "content_target": content_target_2,
                "text": "second comment",
                "parent": pk,
            },
        )
        self.assertEqual(response2.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("parent", response2.json())

    def test_with_nonexistent_parent(self):
        self.client.force_authenticate(user=self.with_permission)
        content_type = ContentType.objects.get_for_model(Article)
        content_target = "{0}.{1}-{2}".format(
            content_type.app_label, content_type.model, Article.objects.last().pk
        )

        response = self.client.post(
            _get_list_url(), {"content_target": content_target, "text": "first comment"}
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        pk = response.json()["id"]

        response2 = self.client.post(
            _get_list_url(),
            {
                "content_target": content_target,
                "text": "second comment",
                "parent": pk + 1000,
            },
        )
        self.assertEqual(response2.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("parent", response2.json())

    def test_with_user_who_cannot_see_parent(self):
        self.client.force_authenticate(user=self.with_permission)

        with_permission_group_ids: Iterator[int] = (
            group.id for group in self.with_permission.all_groups
        )

        group = AbakusGroup.objects.exclude(id__in=with_permission_group_ids).first()
        """
            create an article which has a different owner and a group which with_permission does not
            belong to. The user should then not be allowed to post a comment on this article
        """

        article = Article.objects.create(
            text="hello world", current_user=self.without_permission
        )
        article.can_view_groups.add(group)

        content_type = ContentType.objects.get_for_model(Article)

        content_target = "{0}.{1}-{2}".format(
            content_type.app_label, content_type.model, article.id
        )

        response = self.client.post(
            _get_list_url(), {"content_target": content_target, "text": "first comment"}
        )

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class UpdateCommentsAPITestCase(BaseAPITestCase):
    fixtures = ["test_abakus_groups.yaml", "test_users.yaml", "test_articles.yaml"]

    def setUp(self):
        Comment.objects.create(
            created_by_id=4,
            text="first comment",
            content_object=Article.objects.get(id=1),
        )
        Comment.objects.create(
            created_by_id=3,
            text="second comment",
            content_object=Article.objects.get(id=2),
        )

        self.all_comments = Comment.objects.all()
        self.all_users = User.objects.all()
        self.with_permission = self.all_users.get(username="useradmin_test")
        self.comments_test_group = AbakusGroup.objects.get(name="CommentTest")
        self.comments_test_group.add_user(self.with_permission)
        self.without_permission = self.all_users.exclude(
            pk=self.with_permission.pk
        ).first()
        self.test_comment = Comment.objects.first()

    modified_comment = {"text": "whats up"}

    def successful_update(self, updater, update_object):
        self.client.force_authenticate(user=updater)
        response = self.client.patch(
            _get_detail_url(update_object.pk), self.modified_comment
        )
        comment = Comment.objects.get(pk=update_object.pk)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        for key, value in self.modified_comment.items():
            self.assertEqual(getattr(comment, key), value)

    def test_self(self):
        self.successful_update(self.test_comment.created_by, self.test_comment)

    def test_with_useradmin(self):
        self.successful_update(self.with_permission, self.test_comment)

    def test_with_new_content_target(self):
        comment_update = self.modified_comment.copy()

        content_type = ContentType.objects.get_for_model(Article)
        content_target = "{0}.{1}-{2}".format(
            content_type.app_label, content_type.model, Article.objects.last().pk
        )

        comment_update["content_target"] = content_target
        self.client.force_authenticate(user=self.with_permission)
        response = self.client.put(
            _get_detail_url(self.test_comment.pk), comment_update
        )
        comment = Comment.objects.get(pk=self.test_comment.pk)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(comment.content_object, self.test_comment.content_object)

    def test_other_with_normal_user(self):
        self.client.force_authenticate(user=self.without_permission)
        response = self.client.put(
            _get_detail_url(self.test_comment.pk), self.modified_comment
        )
        comment = Comment.objects.get(pk=self.test_comment.pk)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(comment, self.test_comment)


class DeleteUsersAPITestCase(BaseAPITestCase):
    fixtures = ["test_abakus_groups.yaml", "test_users.yaml", "test_articles.yaml"]

    def setUp(self):
        self.test_comment = Comment.objects.create(
            created_by_id=4,
            text="first comment",
            content_object=Article.objects.get(id=1),
        )
        self.test_comment_2 = Comment.objects.create(
            created_by_id=3,
            text="second comment",
            content_object=Article.objects.get(id=2),
        )

        self.all_comments = Comment.objects.all()
        self.all_users = User.objects.all()
        self.with_permission = self.all_users.get(username="useradmin_test")
        self.comments_test_group = AbakusGroup.objects.get(name="CommentTest")
        self.comments_test_group.add_user(self.with_permission)
        self.without_permission = self.all_users.exclude(
            pk=self.with_permission.pk
        ).first()

    def successful_delete(self, user):
        self.client.force_authenticate(user=user)
        response = self.client.delete(_get_detail_url(self.test_comment.pk))

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertRaises(
            Comment.DoesNotExist, Comment.objects.get, pk=self.test_comment.pk
        )

    def test_with_normal_user(self):
        self.client.force_authenticate(user=self.without_permission)
        response = self.client.delete(_get_detail_url(self.test_comment_2.pk))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_with_owner(self):
        user = User.objects.get(username="pleb")
        self.test_comment.created_by = user
        self.test_comment.save()
        self.successful_delete(self.test_comment.created_by)

    def test_with_useradmin(self):
        self.successful_delete(self.with_permission)
