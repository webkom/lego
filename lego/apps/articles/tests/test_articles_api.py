from django.urls import reverse

from lego.apps.articles.models import Article
from lego.apps.articles.serializers import PublicArticleSerializer
from lego.apps.users.models import AbakusGroup, User
from lego.utils.test_utils import BaseAPITestCase


def get_list_url():
    return reverse("api:v1:article-list")


def get_detail_url(pk):
    return reverse("api:v1:article-detail", kwargs={"pk": pk})


def create_user():
    return User.objects.create(username="testuser")


def get_data_with_author(author_pk):
    return {
        "title": "test article",
        "description": "good article",
        "content": "the best article",
        "author": author_pk,
        "youtube_url": "https://www.youtube.com/watch?v=KrzIaRwAMvc",
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
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data["results"]), 1)

    def test_fields(self):
        response = self.client.get(get_list_url())
        self.assertEqual(response.status_code, 200)
        article = response.data["results"][0]
        self.assertEqual(len(PublicArticleSerializer.Meta.fields), len(article.keys()))

    def test_authenticated(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.get(get_list_url())
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data["results"]), 2)

    def test_with_keyword_permissions(self):
        self.group.permissions = ["/sudo/admin/articles/list/"]
        self.group.save()

        self.client.force_authenticate(user=self.user)
        response = self.client.get(get_list_url())
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data["results"]), 3)

    def test_with_object_permissions(self):
        self.permission_group.add_user(self.user)
        self.client.force_authenticate(user=self.user)
        response = self.client.get(get_list_url())
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data["results"]), 3)


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
        self.assertEqual(response.status_code, 200)

    def test_unauthenticated(self):
        response = self.client.get(get_detail_url(self.auth_article.pk))
        self.assertEqual(response.status_code, 404)

    def test_authenticated(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.get(get_detail_url(self.auth_article.pk))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["id"], self.auth_article.id)

    def test_unauthorized(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.get(get_detail_url(self.object_permission_article.pk))
        self.assertEqual(response.status_code, 404)

    def test_with_keyword_permissions(self):
        self.group.permissions = ["/sudo/admin/articles/view/"]
        self.group.save()

        self.client.force_authenticate(user=self.user)
        response = self.client.get(get_detail_url(self.object_permission_article.pk))
        self.assertEqual(response.status_code, 200)

    def test_with_object_permissions(self):
        self.permission_group.add_user(self.user)
        self.client.force_authenticate(user=self.user)
        response = self.client.get(get_detail_url(self.object_permission_article.pk))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["id"], self.object_permission_article.pk)


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
        self.assertEqual(response.status_code, 401)

    def test_authenticated(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.post(get_list_url())
        self.assertEqual(response.status_code, 403)

    def test_with_keyword_permissions(self):
        self.group.permissions = ["/sudo/admin/articles/create/"]
        self.group.save()

        self.client.force_authenticate(user=self.user)
        data = get_data_with_author(self.user.pk)
        response = self.client.post(get_list_url(), data)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data["title"], data["title"])

    def test_no_title(self):
        self.group.permissions = ["/sudo/admin/articles/create/"]
        self.group.save()

        self.client.force_authenticate(user=self.user)
        data = get_data_with_author(self.user.pk)
        del data["title"]
        response = self.client.post(get_list_url(), data)
        self.assertEqual(response.data, {"title": ["This field is required."]})
        self.assertEqual(response.status_code, 400)

    def test_wrong_youtube_url(self):
        self.group.permissions = ["/sudo/admin/articles/create/"]
        self.group.save()

        self.client.force_authenticate(user=self.user)
        data = get_data_with_author(self.user.pk)
        data["youtube_url"] = "https://www.skra.com/watch?v=KrzIaRwAMvc"
        response = self.client.post(get_list_url(), data)
        self.assertEqual(response.data["youtube_url"][0].code, "invalid")
        self.assertEqual(response.status_code, 400)

    def test_correct_youtube_url(self):
        self.group.permissions = ["/sudo/admin/articles/create/"]
        self.group.save()

        self.client.force_authenticate(user=self.user)
        data = get_data_with_author(self.user.pk)
        data["youtube_url"] = "https://www.youtube.com/watch?v=KrzIaRwAMvc"
        response = self.client.post(get_list_url(), data)
        self.assertEqual(response.status_code, 201)


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
        self.assertEqual(response.status_code, 404)

    def test_authenticated(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.patch(
            get_detail_url(self.article.pk), get_data_with_author(self.user.pk)
        )
        self.assertEqual(response.status_code, 404)

    def test_with_keyword_permissions(self):
        self.group.permissions = ["/sudo/admin/articles/edit/"]
        self.group.save()

        self.client.force_authenticate(user=self.user)
        response = self.client.patch(
            get_detail_url(self.article.pk), get_data_with_author(self.user.pk)
        )
        self.assertEqual(response.status_code, 200)

    def test_with_object_permissions(self):
        self.permission_group.add_user(self.user)
        self.client.force_authenticate(user=self.user)
        response = self.client.patch(
            get_detail_url(self.article.pk), get_data_with_author(self.user.pk)
        )
        self.assertEqual(response.status_code, 200)


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
        self.assertEqual(response.status_code, 404)

    def test_authenticated(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.delete(get_detail_url(self.article.pk))
        self.assertEqual(response.status_code, 404)

    def test_with_keyword_permissions(self):
        self.group.permissions = ["/sudo/admin/articles/delete/"]
        self.group.save()

        self.client.force_authenticate(user=self.user)
        response = self.client.delete(get_detail_url(self.article.pk))
        self.assertEqual(response.status_code, 204)

    def test_with_object_permissions(self):
        self.permission_group.add_user(self.user)
        self.client.force_authenticate(user=self.user)
        response = self.client.delete(get_detail_url(self.article.pk))
        self.assertEqual(response.status_code, 204)
