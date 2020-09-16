import uuid

from lego.apps.flatpages.models import Page
from lego.apps.users.models import AbakusGroup, User
from lego.apps.users.tests.utils import (
    create_normal_user,
    create_super_user,
    create_user_with_permissions,
)
from lego.utils.test_utils import BaseAPITestCase


def get_new_unique_page():
    return {
        "title": str(uuid.uuid4()),
        "slug": str(uuid.uuid4()),
        "content": str(uuid.uuid4()),
    }


def create_group(**kwargs):
    group = AbakusGroup.objects.create(name=str(uuid.uuid4()), **kwargs)
    return group


class PageAPITestCase(BaseAPITestCase):
    fixtures = ["test_pages.yaml"]

    def setUp(self):
        self.pages = Page.objects.all().order_by("created_at")

    def test_get_pages(self):
        response = self.client.get("/api/v1/pages/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()["results"]), 4)
        first = response.json()["results"][0]
        self.assertEqual(first["title"], self.pages.first().title)
        self.assertEqual(first["slug"], self.pages.first().slug)
        self.assertFalse("content" in first)

    def test_get_page_with_id(self):
        slug = "webkom"
        response = self.client.get("/api/v1/pages/{0}/".format(slug))
        expected = self.pages.get(slug=slug)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["title"], expected.title)
        self.assertEqual(response.json()["slug"], expected.slug)
        self.assertEqual(response.json()["content"], expected.content)

    def test_non_existing_retrieve(self):
        response = self.client.get("/api/v1/pages/badslug/")
        self.assertEqual(response.status_code, 404)

    def test_unauthenticated(self):
        slug = "webkom"
        methods = ["post", "patch", "put", "delete"]
        for method in methods:
            call = getattr(self.client, method)
            response = call("/api/v1/pages/{0}/".format(slug))
            self.assertEqual(response.status_code, 401)

    def test_unauthorized(self):
        slug = "webkom"
        methods = ["post", "patch", "put", "delete"]
        user = create_normal_user()
        self.client.force_authenticate(user)
        for method in methods:
            call = getattr(self.client, method)
            response = call("/api/v1/pages/{0}/".format(slug))
            self.assertEqual(response.status_code, 403)

    def test_create_page(self):
        page = {"title": "cat", "content": "hei"}
        user = create_user_with_permissions("/sudo/admin/pages/")
        self.client.force_authenticate(user)
        response = self.client.post("/api/v1/pages/", data=page)
        self.assertEqual(response.status_code, 201)

    def test_list_with_keyword_permissions(self):
        user = create_user_with_permissions("/sudo/admin/pages/list/")
        self.client.force_authenticate(user)
        response = self.client.get("/api/v1/pages/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()["results"]), 5)

    def test_edit_with_object_permissions(self):
        slug = "webkom"
        page = self.pages.get(slug=slug)
        user = create_normal_user()
        group = create_group()
        group.add_user(user)
        group.save()
        page.can_edit_groups.add(group)
        self.client.force_authenticate(user)
        response = self.client.patch(
            "/api/v1/pages/{0}/".format(slug), get_new_unique_page()
        )
        self.assertEqual(response.status_code, 200)

    def test_edit_without_object_permissions(self):
        slug = "webkom"
        page = self.pages.get(slug=slug)
        user = create_normal_user()
        group = create_group()
        page.can_edit_groups.add(group)
        wrong_group = create_group()
        wrong_group.add_user(user)
        wrong_group.save()
        self.client.force_authenticate(user)
        response = self.client.patch(
            "/api/v1/pages/{0}/".format(slug), get_new_unique_page()
        )
        self.assertEqual(response.status_code, 403)
