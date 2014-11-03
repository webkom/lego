# -*- coding: utf8 -*-
from lego.users.serializers import UserSerializer, PublicUserSerializer
from rest_framework.test import APITestCase, APIRequestFactory, force_authenticate

from lego.users.models import User
from lego.users.views.users import UsersViewSet


test_user_data = {
    'username': 'new_testuser',
    'first_name': 'new',
    'last_name': 'test_user',
    'email': 'new@testuser.com',
}


def get_test_user():
    user = User(**test_user_data)
    user.save()

    return user


class ListUsersAPITestCase(APITestCase):
    fixtures = ['test_users.yaml']

    def setUp(self):
        self.all_users = User.objects.all()
        self.super_user = self.all_users.filter(is_superuser=True).first()
        self.normal_user = self.all_users.filter(is_superuser=False).first()

        self.factory = APIRequestFactory()
        self.request = self.factory.get('/api/users/')
        self.view = UsersViewSet.as_view({'get': 'list'})

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

    def setUp(self):
        self.all_users = User.objects.all()
        self.super_user = self.all_users.filter(is_superuser=True).first()
        self.normal_user = self.all_users.filter(is_superuser=False).first()

        self.factory = APIRequestFactory()
        self.request = self.factory.get('/api/users/')
        self.view = UsersViewSet.as_view({'get': 'retrieve'})

    def test_without_auth(self):
        response = self.view(self.request)
        self.assertEqual(response.status_code, 401)

    def test_with_normal_user(self):
        force_authenticate(self.request, user=self.normal_user)
        response = self.view(self.request, pk=1)
        user = response.data
        keys = set(user.keys())

        self.assertEqual(response.status_code, 200)
        self.assertEqual(keys, set(PublicUserSerializer.Meta.fields))

    def test_self_with_normal_user(self):
        force_authenticate(self.request, user=self.normal_user)
        response = self.view(self.request, pk=self.normal_user.pk)
        user = response.data
        keys = set(user.keys())

        self.assertEqual(response.status_code, 200)
        self.assertEqual(keys, set(UserSerializer.Meta.fields))

    def test_with_super_user(self):
        force_authenticate(self.request, user=self.super_user)
        response = self.view(self.request, pk=1)
        user = response.data
        keys = set(user.keys())

        self.assertEqual(response.status_code, 200)
        self.assertEqual(keys, set(UserSerializer.Meta.fields))


class CreateUsersAPITestCase(APITestCase):
    fixtures = ['test_users.yaml']

    def setUp(self):
        self.all_users = User.objects.all()
        self.super_user = self.all_users.filter(is_superuser=True).first()
        self.normal_user = self.all_users.filter(is_superuser=False).first()

        self.factory = APIRequestFactory()
        self.view = UsersViewSet.as_view({'post': 'create'})
        self.request = self.factory.post('/api/users', test_user_data)

    def test_create_with_normal_user(self):
        force_authenticate(self.request, user=self.normal_user)
        response = self.view(self.request)

        self.assertEqual(response.status_code, 403)

    def test_create_with_super_user(self):
        force_authenticate(self.request, user=self.super_user)
        response = self.view(self.request)

        self.assertEqual(response.status_code, 201)
        created_user = User.objects.get(username=test_user_data['username'])

        for key, value in test_user_data.items():
            self.assertEqual(getattr(created_user, key), value)

    def test_create_existing_username(self):
        existing_user = get_test_user()

        force_authenticate(self.request, user=self.super_user)
        response = self.view(self.request)

        self.assertEqual(response.status_code, 400)


class UpdateUsersAPITestCase(APITestCase):
    fixtures = ['test_users.yaml']

    modified_user = {
        'username': 'modified_user',
        'first_name': 'modified',
        'last_name': 'user',
        'email': 'modified@testuser.com',
    }

    def setUp(self):
        self.all_users = User.objects.all()
        self.super_user = self.all_users.filter(is_superuser=True).first()
        self.normal_user = self.all_users.filter(is_superuser=False).first()

        self.factory = APIRequestFactory()
        self.view = UsersViewSet.as_view({'put': 'update'})
        self.test_user = get_test_user()
        self.request = self.factory.put('/api/users/',
                                        self.modified_user)

    def test_update_self_with_normal_user(self):
        force_authenticate(self.request, user=self.normal_user)
        response = self.view(self.request, pk=self.normal_user.pk)
        user = User.objects.get(pk=self.normal_user.pk)

        self.assertEqual(response.status_code, 200)

        for key, value in self.modified_user.items():
            self.assertEqual(getattr(user, key), value)

    def test_update_other_with_normal_user(self):
        force_authenticate(self.request, user=self.normal_user)
        response = self.view(self.request, pk=self.test_user.pk)
        user = User.objects.get(pk=self.test_user.pk)

        self.assertEqual(response.status_code, 403)
        self.assertEqual(user, self.test_user)

    def test_update_with_super_user(self):
        force_authenticate(self.request, user=self.super_user)
        response = self.view(self.request, pk=self.test_user.pk)
        user = User.objects.get(pk=self.test_user.pk)

        self.assertEqual(response.status_code, 200)

        for key, value in self.modified_user.items():
            self.assertEqual(getattr(user, key), value)


class DeleteUsersAPITestCase(APITestCase):
    fixtures = ['test_users.yaml']

    test_user_data = {
        'username': 'new_testuser',
        'first_name': 'new',
        'last_name': 'test_user',
        'email': 'new@testuser.com',
    }

    def setUp(self):
        self.all_users = User.objects.all()
        self.super_user = self.all_users.filter(is_superuser=True).first()
        self.normal_user = self.all_users.filter(is_superuser=False).first()

        self.factory = APIRequestFactory()
        self.view = UsersViewSet.as_view({'delete': 'destroy'})
        self.test_user = get_test_user()
        self.request = self.factory.delete('/api/users/{0}/'.format(self.test_user.pk))

    def test_delete_with_normal_user(self):
        force_authenticate(self.request, user=self.normal_user)
        response = self.view(self.request, pk=self.test_user.pk)
        users = User.objects.filter(pk=self.test_user.pk)

        self.assertEqual(response.status_code, 403)
        self.assertTrue(len(users))

    def test_delete_with_super_user(self):
        force_authenticate(self.request, user=self.super_user)
        response = self.view(self.request, pk=self.test_user.pk)

        self.assertEqual(response.status_code, 204)
        self.assertRaises(User.DoesNotExist, User.objects.get, pk=self.test_user.pk)
