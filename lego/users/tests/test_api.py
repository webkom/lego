# -*- coding: utf8 -*-
from lego.users.serializers import UserSerializer, PublicUserSerializer
from rest_framework.test import APITestCase, APIRequestFactory, force_authenticate

from lego.users.models import User
from lego.users.views.user import UserViewSet


class ListUsersAPITestCase(APITestCase):
    fixtures = ['test_users.yaml']

    all_users = User.objects.all()
    super_user = all_users.filter(is_superuser=True)[0]
    normal_user = all_users.filter(is_superuser=False)[0]

    def setUp(self):
        self.factory = APIRequestFactory()
        self.request = self.factory.get('/api/users/')
        self.view = UserViewSet.as_view({'get': 'list'})

    def test_without_auth(self):
        response = self.view(self.request)
        self.assertEqual(response.status_code, 401)

    def test_with_normal_user(self):
        force_authenticate(self.request, user=self.normal_user)
        response = self.view(self.request)

        self.assertEqual(response.status_code, 403)

    def test_with_super_user(self):
        force_authenticate(self.request, user=self.super_user)
        response = self.view(self.request)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), len(self.all_users))


class GetUsersAPITestCase(APITestCase):
    fixtures = ['test_users.yaml']
    super_user = User.objects.filter(is_superuser=True)[0]
    normal_user = User.objects.filter(is_superuser=False)[0]

    def setUp(self):
        self.factory = APIRequestFactory()
        self.request = self.factory.get('/api/users/')
        self.view = UserViewSet.as_view({'get': 'retrieve'})

    def test_without_auth(self):
        response = self.view(self.request)
        self.assertEqual(response.status_code, 401)

    def test_with_normal_user(self):
        force_authenticate(self.request, user=self.normal_user)
        response = self.view(self.request, 1)
        user = response.data
        keys = set(user.keys())

        self.assertEqual(response.status_code, 200)
        self.assertEqual(keys, set(PublicUserSerializer.Meta.fields))

    def test_with_super_user(self):
        force_authenticate(self.request, user=self.super_user)
        response = self.view(self.request, 1)
        user = response.data
        keys = set(user.keys())

        self.assertEqual(response.status_code, 200)
        self.assertEqual(keys, set(UserSerializer.Meta.fields))


class ModifyUsersAPITestCase(APITestCase):
    fixtures = ['test_users.yaml']
    super_user = User.objects.filter(is_superuser=True)[0]
    normal_user = User.objects.filter(is_superuser=False)[0]

    test_user_json = {
        'username': 'new_testuser',
        'first_name': 'new',
        'last_name': 'test_user',
        'email': 'new@testuser.com',
    }

    def setUp(self):
        self.factory = APIRequestFactory()

    def test_create_with_normal_user(self):
        request = self.factory.post('/api/users/', self.test_user_json)
        force_authenticate(request, user=self.normal_user)
        view = UserViewSet.as_view({'post': 'create'})
        response = view(request)

        self.assertEqual(response.status_code, 403)

    def test_create_with_super_user(self):
        request = self.factory.post('/api/users/', self.test_user_json)
        force_authenticate(request, user=self.super_user)
        view = UserViewSet.as_view({'post': 'create'})
        response = view(request)

        self.assertEqual(response.status_code, 201)
        created_user = User.objects.get(username=self.test_user_json['username'])

        for key, value in self.test_user_json.items():
            self.assertEqual(getattr(created_user, key), value)

    def test_create_existing_username(self):
        existing_user = User(**self.test_user_json)
        existing_user.save()

        request = self.factory.post('/api/users/', self.test_user_json)
        force_authenticate(request, user=self.super_user)
        view = UserViewSet.as_view({'post': 'create'})
        response = view(request)

        self.assertEqual(response.status_code, 400)
