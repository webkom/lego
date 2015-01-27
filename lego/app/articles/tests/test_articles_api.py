# -*- coding: utf--8 -*-
from rest_framework.test import APITestCase, APIRequestFactory, force_authenticate

from lego.users.models import User, AbakusGroup
from lego.users.views.users import UsersViewSet


class ListArticlesTestCase(APITestCase):
    fixtures = ['initial_abakus_groups.yaml', 'test_articles.yaml',
                'test_users.yaml']

    def setUp(self):
        self.all_users = User.objects.all()

        self.factory = APIRequestFactory()
        self.request = self.factory.get('/api/articles/')
        self.view = UsersViewSet.as_view({'get': 'list'})

    def test_with_abakus_user(self):
        user1 = self.all_users.get(id=3)

        force_authenticate(self.request, user=user1)
        response = self.view(self.request)

        self.assertEqual(response.status_code, 200)


class RetrieveArticlesTestCase(APITestCase):
    fixtures = ['initial_abakus_groups.yaml', 'test_articles.yaml',
                'test_users.yaml']

    def setUp(self):
        self.all_users = User.objects.all()
        self.super_user = User.objects.filter(is_superuser=True).first()
        self.abakus_user = User.objects.filter(is_superuser=False).first()

        self.abakus_group = AbakusGroup.objects.get(name='Abakus')
        self.abakus_group.add_user(self.abakus_user)

        self.factory = APIRequestFactory()
        self.view = UsersViewSet.as_view({'get': 'list'})

    def test_with_group_permission(self):
        request = self.factory.get('/api/articles/1')
        force_authenticate(request, user=self.abakus_user)
        response = self.view(request)
        self.assertEqual(response.status_code, 200)

    def test_without_group_permission(self):
        request = self.factory.get('/api/articles/2')
        force_authenticate(request, user=self.abakus_user)
        response = self.view(request)
        self.assertEqual(response.status_code, 403)

    def test_with_superuser(self):
        request = self.factory.get('/api/articles/2')
        force_authenticate(request, user=self.super_user)
        response = self.view(request)
        self.assertEqual(response.status_code, 200)
