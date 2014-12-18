# -*- coding: utf8 -*-
from rest_framework.test import APITestCase, APIRequestFactory, force_authenticate

from lego.users.models import User, AbakusGroup
from lego.users.views.users import UsersViewSet
from lego.users.serializers import UserSerializer, PublicUserSerializer

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
    fixtures = ['initial_permission_groups.yaml', 'test_abakus_groups.yaml', 'test_users.yaml']

    def setUp(self):
        self.all_users = User.objects.all()
        self.super_user = self.all_users.filter(is_superuser=True).first()
        self.normal_user = self.all_users.filter(is_superuser=False).first()

        self.useradmin_user = self.all_users.get(username='useradmin_test')
        self.useradmin_test_group = AbakusGroup.objects.get(name='UserAdminTest')
        self.useradmin_test_group.add_user(self.useradmin_user)

        self.factory = APIRequestFactory()
        self.request = self.factory.get('/api/users/')
        self.view = UsersViewSet.as_view({'get': 'list'})

    def successful_list(self, user):
        force_authenticate(self.request, user=user)
        response = self.view(self.request)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), len(self.all_users))

    def test_without_auth(self):
        response = self.view(self.request)
        self.assertEqual(response.status_code, 401)

    def test_with_normal_user(self):
        force_authenticate(self.request, user=self.normal_user)
        response = self.view(self.request)

        self.assertEqual(response.status_code, 403)

    def test_with_useradmin(self):
        self.successful_list(self.useradmin_user)

    def test_with_super_user(self):
        self.successful_list(self.super_user)


class GetUsersAPITestCase(APITestCase):
    fixtures = ['initial_permission_groups.yaml', 'test_abakus_groups.yaml', 'test_users.yaml']

    def setUp(self):
        self.all_users = User.objects.all()
        self.super_user = self.all_users.filter(is_superuser=True).first()
        self.normal_user = self.all_users.filter(is_superuser=False).first()
        self.test_user = get_test_user()

        self.useradmin_user = self.all_users.get(username='useradmin_test')
        self.useradmin_test_group = AbakusGroup.objects.get(name='UserAdminTest')
        self.useradmin_test_group.add_user(self.useradmin_user)

        self.factory = APIRequestFactory()
        self.request = self.factory.get('/api/users/')
        self.view = UsersViewSet.as_view({'get': 'retrieve'})

    def successful_retrieve(self, user):
        force_authenticate(self.request, user=user)
        response = self.view(self.request, pk=self.test_user.pk)
        user = response.data
        keys = set(user.keys())

        self.assertEqual(response.status_code, 200)
        self.assertEqual(keys, set(UserSerializer.Meta.fields))

    def test_without_auth(self):
        response = self.view(self.request)
        self.assertEqual(response.status_code, 401)

    def test_with_normal_user(self):
        force_authenticate(self.request, user=self.normal_user)
        response = self.view(self.request, pk=self.test_user.pk)
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

    def test_with_useradmin(self):
        self.successful_retrieve(self.useradmin_user)

    def test_with_super_user(self):
        self.successful_retrieve(self.super_user)


class CreateUsersAPITestCase(APITestCase):
    fixtures = ['initial_permission_groups.yaml', 'test_abakus_groups.yaml', 'test_users.yaml']

    def setUp(self):
        self.all_users = User.objects.all()
        self.super_user = self.all_users.filter(is_superuser=True).first()
        self.normal_user = self.all_users.filter(is_superuser=False).first()

        self.useradmin_user = self.all_users.get(username='useradmin_test')
        self.useradmin_test_group = AbakusGroup.objects.get(name='UserAdminTest')
        self.useradmin_test_group.add_user(self.useradmin_user)

        self.factory = APIRequestFactory()
        self.view = UsersViewSet.as_view({'post': 'create'})
        self.request = self.factory.post('/api/users/', test_user_data)

    def successful_create(self, user):
        force_authenticate(self.request, user=user)
        response = self.view(self.request)

        self.assertEqual(response.status_code, 201)
        created_user = User.objects.get(username=test_user_data['username'])

        for key, value in test_user_data.items():
            self.assertEqual(getattr(created_user, key), value)

    def test_with_normal_user(self):
        force_authenticate(self.request, user=self.normal_user)
        response = self.view(self.request)

        self.assertEqual(response.status_code, 403)

    def test_with_useradmin(self):
        self.successful_create(self.useradmin_user)

    def test_with_super_user(self):
        self.successful_create(self.super_user)

    def test_username(self):
        get_test_user()
        force_authenticate(self.request, user=self.super_user)
        response = self.view(self.request)

        self.assertEqual(response.status_code, 400)


class UpdateUsersAPITestCase(APITestCase):
    fixtures = ['initial_permission_groups.yaml', 'test_abakus_groups.yaml', 'test_users.yaml']

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

        self.useradmin_user = self.all_users.get(username='useradmin_test')
        self.useradmin_test_group = AbakusGroup.objects.get(name='UserAdminTest')
        self.useradmin_test_group.add_user(self.useradmin_user)

        self.factory = APIRequestFactory()
        self.view = UsersViewSet.as_view({'put': 'update'})
        self.test_user = get_test_user()
        self.request = self.factory.put('/api/users/',
                                        self.modified_user)

    def successful_update(self, updater, update_object):
        force_authenticate(self.request, user=updater)
        response = self.view(self.request, pk=update_object.pk)
        user = User.objects.get(pk=update_object.pk)

        self.assertEqual(response.status_code, 200)

        for key, value in self.modified_user.items():
            self.assertEqual(getattr(user, key), value)

    def test_self(self):
        self.successful_update(self.normal_user, self.normal_user)

    def test_with_useradmin(self):
        self.successful_update(self.useradmin_user, self.test_user)

    def test_other_with_normal_user(self):
        force_authenticate(self.request, user=self.normal_user)
        response = self.view(self.request, pk=self.test_user.pk)
        user = User.objects.get(pk=self.test_user.pk)

        self.assertEqual(response.status_code, 403)
        self.assertEqual(user, self.test_user)

    def test_update_with_super_user(self):
        self.successful_update(self.super_user, self.test_user)


class DeleteUsersAPITestCase(APITestCase):
    fixtures = ['initial_permission_groups.yaml', 'test_abakus_groups.yaml', 'test_users.yaml']

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

        self.useradmin_user = self.all_users.get(username='useradmin_test')
        self.useradmin_test_group = AbakusGroup.objects.get(name='UserAdminTest')
        self.useradmin_test_group.add_user(self.useradmin_user)

        self.factory = APIRequestFactory()
        self.view = UsersViewSet.as_view({'delete': 'destroy'})
        self.test_user = get_test_user()
        self.request = self.factory.delete('/api/users/{0}/'.format(self.test_user.pk))

    def successful_delete(self, user):
        force_authenticate(self.request, user=user)
        response = self.view(self.request, pk=self.test_user.pk)

        self.assertEqual(response.status_code, 204)
        self.assertRaises(User.DoesNotExist, User.objects.get, pk=self.test_user.pk)

    def test_with_normal_user(self):
        force_authenticate(self.request, user=self.normal_user)
        response = self.view(self.request, pk=self.test_user.pk)
        users = User.objects.filter(pk=self.test_user.pk)

        self.assertEqual(response.status_code, 403)
        self.assertTrue(len(users))

    def test_with_useradmin(self):
        self.successful_delete(self.useradmin_user)

    def test_with_super_user(self):
        self.successful_delete(self.super_user)
