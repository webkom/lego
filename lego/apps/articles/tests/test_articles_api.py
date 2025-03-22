from datetime import datetime, timedelta
from unittest import mock

from django.urls import reverse
from rest_framework import status
from rest_framework.response import Response

from lego.apps.articles.models import Article
from lego.apps.articles.serializers import PublicArticleSerializer
from lego.apps.users.models import AbakusGroup, User
from lego.utils.test_utils import BaseAPITestCase


def get_list_url():
    return reverse("api:v1:article-list")


def get_detail_url(pk):
    return reverse("api:v1:article-detail", kwargs={"pk": pk})


def get_statistics_url(pk):
    return reverse("api:v1:article-statistics", kwargs={"pk": pk})


def create_user():
    return User.objects.create(username="testuser")


def create_other_user():
    return User.objects.create(username="othertestuser", email="otheremail")


def get_data_with_author(author_pk):
    return {
        "title": "test article",
        "description": "good article",
        "content": "the best article",
        "authors": [author_pk],
    }


def create_article(**kwargs):
    return Article.objects.create(
        title="test article", description="good article", text="long text", **kwargs
    )


group_name_suffix = 1


def create_group(**kwargs):
    global group_name_suffix
    group = AbakusGroup.objects.create(
        name="group_{}".format(group_name_suffix), **kwargs
    )
    group_name_suffix += 1
    return group


class ListArticlesTestCase(BaseAPITestCase):
    def setUp(self):
        self.user = create_user()
        self.group = create_group()
        self.group.add_user(self.user)
        self.permission_group = create_group()
        self.public_article = create_article(require_auth=False)

        self.auth_article = create_article(require_auth=True)
        self.auth_article.can_view_groups.add(self.group)

        self.object_permission_article = create_article(require_auth=True)
        self.object_permission_article.can_view_groups.add(self.permission_group)

    def test_unauthenticated_user(self):
        response = self.client.get(get_list_url())
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.json()["results"]), 1)

    def test_fields(self):
        response = self.client.get(get_list_url())
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        article = response.json()["results"][0]
        self.assertEqual(len(PublicArticleSerializer.Meta.fields), len(article.keys()))

    def test_authenticated(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.get(get_list_url())
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.json()["results"]), 2)

    def test_with_keyword_permissions(self):
        self.group.permissions = ["/sudo/admin/articles/list/"]
        self.group.save()

        self.client.force_authenticate(user=self.user)
        response = self.client.get(get_list_url())
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.json()["results"]), 3)

    def test_with_object_permissions(self):
        self.permission_group.add_user(self.user)
        self.client.force_authenticate(user=self.user)
        response = self.client.get(get_list_url())
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.json()["results"]), 3)


class RetrieveArticlesTestCase(BaseAPITestCase):
    def setUp(self):
        self.user = create_user()
        self.group = create_group()
        self.group.add_user(self.user)
        self.permission_group = create_group()
        self.public_article = create_article(require_auth=False)

        self.auth_article = create_article(require_auth=True)
        self.auth_article.can_view_groups.add(self.group)

        self.object_permission_article = create_article(require_auth=True)
        self.object_permission_article.can_view_groups.add(self.permission_group)

    def test_unauthenticated_public(self):
        response = self.client.get(get_detail_url(self.public_article.pk))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_unauthenticated(self):
        response = self.client.get(get_detail_url(self.auth_article.pk))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_authenticated(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.get(get_detail_url(self.auth_article.pk))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json()["id"], self.auth_article.id)

    def test_unauthorized(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.get(get_detail_url(self.object_permission_article.pk))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_with_keyword_permissions(self):
        self.group.permissions = ["/sudo/admin/articles/view/"]
        self.group.save()

        self.client.force_authenticate(user=self.user)
        response = self.client.get(get_detail_url(self.object_permission_article.pk))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_with_object_permissions(self):
        self.permission_group.add_user(self.user)
        self.client.force_authenticate(user=self.user)
        response = self.client.get(get_detail_url(self.object_permission_article.pk))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json()["id"], self.object_permission_article.pk)


class CreateArticlesTestCase(BaseAPITestCase):
    def setUp(self):
        self.user = create_user()
        self.group = create_group()
        self.group.add_user(self.user)
        self.permission_group = create_group()

        self.article = create_article(require_auth=True)
        self.article.can_edit_groups.add(self.permission_group)

    def test_unauthenticated(self):
        response = self.client.post(get_list_url())
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_authenticated(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.post(get_list_url())
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_with_keyword_permissions(self):
        self.group.permissions = ["/sudo/admin/articles/create/"]
        self.group.save()

        self.client.force_authenticate(user=self.user)
        data = get_data_with_author(self.user.pk)
        response = self.client.post(get_list_url(), data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.json()["title"], data["title"])

    def test_no_title(self):
        self.group.permissions = ["/sudo/admin/articles/create/"]
        self.group.save()

        self.client.force_authenticate(user=self.user)
        data = get_data_with_author(self.user.pk)
        del data["title"]
        response = self.client.post(get_list_url(), data)
        self.assertEqual(response.json(), {"title": ["This field is required."]})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_wrong_youtube_url(self):
        self.group.permissions = ["/sudo/admin/articles/create/"]
        self.group.save()

        self.client.force_authenticate(user=self.user)
        data = get_data_with_author(self.user.pk)
        data["youtubeUrl"] = "https://www.skra.com/watch?v=KrzIaRwAMvc"
        response = self.client.post(get_list_url(), data)
        self.assertIn("youtubeUrl", response.json())
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_correct_youtube_url(self):
        self.group.permissions = ["/sudo/admin/articles/create/"]
        self.group.save()

        self.client.force_authenticate(user=self.user)
        data = get_data_with_author(self.user.pk)
        data["youtubeUrl"] = "https://www.youtube.com/watch?v=KrzIaRwAMvc"
        response = self.client.post(get_list_url(), data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)


class UpdateArticlesTestCase(BaseAPITestCase):
    def setUp(self):
        self.user = create_user()
        self.group = create_group()
        self.group.add_user(self.user)
        self.permission_group = create_group()

        self.article = create_article(require_auth=True)
        self.article.can_edit_groups.add(self.permission_group)

    def test_unauthenticated(self):
        response = self.client.patch(
            get_detail_url(self.article.pk), get_data_with_author(self.user.pk)
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_authenticated(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.patch(
            get_detail_url(self.article.pk), get_data_with_author(self.user.pk)
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_with_keyword_permissions(self):
        self.group.permissions = ["/sudo/admin/articles/edit/"]
        self.group.save()

        self.client.force_authenticate(user=self.user)
        response = self.client.patch(
            get_detail_url(self.article.pk), get_data_with_author(self.user.pk)
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_with_object_permissions(self):
        self.permission_group.add_user(self.user)
        self.client.force_authenticate(user=self.user)
        response = self.client.patch(
            get_detail_url(self.article.pk), get_data_with_author(self.user.pk)
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class RemoveArticlesTestCase(BaseAPITestCase):
    def setUp(self):
        self.user = create_user()
        self.group = create_group()
        self.group.add_user(self.user)
        self.permission_group = create_group()

        self.article = create_article(require_auth=True)
        self.article.can_edit_groups.add(self.permission_group)

    def test_unauthenticated(self):
        response = self.client.delete(get_detail_url(self.article.pk))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_authenticated(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.delete(get_detail_url(self.article.pk))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_with_keyword_permissions(self):
        self.group.permissions = ["/sudo/admin/articles/delete/"]
        self.group.save()

        self.client.force_authenticate(user=self.user)
        response = self.client.delete(get_detail_url(self.article.pk))
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_with_object_permissions(self):
        self.permission_group.add_user(self.user)
        self.client.force_authenticate(user=self.user)
        response = self.client.delete(get_detail_url(self.article.pk))
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)


class PinnedArticleTestCase(BaseAPITestCase):
    def setUp(self):
        self.user = create_user()
        self.group = create_group()
        self.group.add_user(self.user)
        self.permission_group = create_group()
        self.permission_group.add_user(self.user)

        self.article = create_article(require_auth=True)
        self.article.can_edit_groups.add(self.permission_group)

    def test_only_one_pinned(self):
        """
        When setting an article as pinned, any other pinned articles should set pinned=False
        """
        pinned = create_article(pinned=True)
        self.client.force_authenticate(user=self.user)
        self.client.patch(get_detail_url(self.article.pk), {"pinned": True})

        self.article.refresh_from_db()
        pinned.refresh_from_db()
        self.assertTrue(self.article.pinned)
        self.assertFalse(pinned.pinned)
        self.assertEqual(Article.objects.filter(pinned=True).count(), 1)


def generate_plausible_item(i):
    return {
        "bounce_rate": str(30),
        "date": (datetime.now() - timedelta(days=i)).strftime("%Y-%m-%d"),
        "pageviews": str(i * 2),
        "visit_duration": str(i * 10),
        "visitors": str(i),
    }


number_of_plausible_items = 3


def mocked_plausible_request(*args, **kwargs):
    class MockPlausibleResponse:
        def __init__(self, *args, **kwargs):
            self.status_code = status.HTTP_200_OK
            self.json_data = [
                generate_plausible_item(i) for i in range(number_of_plausible_items)
            ]

        def json(self):
            return self.json_data

    return MockPlausibleResponse()


@mock.patch(
    "lego.apps.articles.views.request_plausible_statistics",
    return_value=mocked_plausible_request(),
)
class ArticleStatisticsCase(BaseAPITestCase):
    def setUp(self):
        self.view_user = create_user()
        self.view_group = create_group()
        self.view_group.add_user(self.view_user)

        self.edit_user = create_other_user()
        self.edit_group = create_group()
        self.edit_group.add_user(self.edit_user)

        self.auth_article = create_article(require_auth=True)
        self.auth_article.can_view_groups.add(self.view_group)
        self.auth_article.can_edit_groups.add(self.edit_group)

    def test_unauthenticated(self, *args):
        response = self.client.get(get_statistics_url(self.auth_article.pk))
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_authenticated_view(self, *args):
        self.client.force_authenticate(user=self.view_user)
        response = self.client.get(get_statistics_url(self.auth_article.pk))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_authenticated_edit(self, *args):
        self.client.force_authenticate(user=self.edit_user)
        response = self.client.get(get_statistics_url(self.auth_article.pk))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.json())
        self.assertEqual(len(response.json()), number_of_plausible_items)
