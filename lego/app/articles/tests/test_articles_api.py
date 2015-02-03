# -*- coding: utf--8 -*-
from django.core.urlresolvers import reverse
from rest_framework.test import APITestCase

from lego.users.models import AbakusGroup, User
from lego.users.views.users import UsersViewSet

get_list_url = lambda: reverse('article-list')
get_detail_url = lambda pk: reverse('article-detail', kwargs={'pk': pk})


class ListArticlesTestCase(APITestCase):
    fixtures = ['initial_abakus_groups.yaml', 'test_articles.yaml',
                'test_users.yaml']

    def setUp(self):
        self.all_users = User.objects.all()
        self.view = UsersViewSet.as_view({'get': 'list'})

    def test_with_abakus_user(self):
        user1 = self.all_users.all().filter(is_superuser=False).first()
        self.client.force_authenticate(user=user1)
        response = self.client.get(get_list_url())
        self.assertEqual(response.status_code, 200)


class RetrieveArticlesTestCase(APITestCase):
    fixtures = ['initial_abakus_groups.yaml', 'test_articles.yaml',
                'test_users.yaml']

    def setUp(self):
        self.abakus_user = User.objects.filter(is_superuser=False).first()

        self.abakus_group = AbakusGroup.objects.get(name='Abakus')
        self.abakus_group.add_user(self.abakus_user)

    def test_with_group_permission(self):
        self.client.force_authenticate(user=self.abakus_user)
        response = self.client.get(get_detail_url(1))
        self.assertEqual(response.status_code, 200)

    def test_without_group_permission(self):
        self.client.force_authenticate(user=self.abakus_user)
        response = self.client.get(get_detail_url(2))
        self.assertEqual(response.status_code, 404)
