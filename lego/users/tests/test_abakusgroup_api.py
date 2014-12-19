# -*- coding: utf8 -*-
from rest_framework.test import APITestCase, APIRequestFactory, force_authenticate

from lego.users.serializers import AbakusGroupSerializer, PublicAbakusGroupSerializer
from lego.users.views.abakus_groups import AbakusGroupViewSet
from lego.users.models import User, AbakusGroup

test_group_data = {
    'name': 'testgroup',
    'description': 'test group',
}


class ListAbakusGroupAPITestCase(APITestCase):
    fixtures = ['initial_permission_groups.yaml', 'test_abakus_groups.yaml', 'test_users.yaml']

    def setUp(self):
        self.all_groups = AbakusGroup.objects.all()

        self.with_permission = User.objects.get(username='abakusgroupadmin_test')
        self.without_permission = (User.objects
                                   .exclude(pk=self.with_permission.pk, is_superuser=True)
                                   .first())

        self.groupadmin_test_group = AbakusGroup.objects.get(name='AbakusGroupAdminTest')
        self.groupadmin_test_group.add_user(self.with_permission)

        self.factory = APIRequestFactory()
        self.request = self.factory.get('/api/groups/')
        self.view = AbakusGroupViewSet.as_view({'get': 'list'})

    def successful_list(self, user):
        force_authenticate(self.request, user=user)
        response = self.view(self.request)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), len(self.all_groups))

    def test_without_auth(self):
        response = self.view(self.request)
        self.assertEqual(response.status_code, 401)

    def test_with_permission(self):
        self.successful_list(self.with_permission)

    def test_without_permission(self):
        test_group = AbakusGroup.objects.get(name='TestGroup')
        test_group.add_user(self.without_permission)

        force_authenticate(self.request, user=self.without_permission)
        response = self.view(self.request)
        groups = response.data

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(groups), 1)
        self.assertEqual(groups[0]['id'], test_group.pk)


class RetrieveAbakusGroupAPITestCase(APITestCase):
    fixtures = ['initial_permission_groups.yaml', 'test_abakus_groups.yaml', 'test_users.yaml']

    def setUp(self):
        self.all_groups = AbakusGroup.objects.all()

        self.with_permission = User.objects.get(username='abakusgroupadmin_test')
        self.without_permission = (User.objects
                                   .exclude(pk=self.with_permission.pk, is_superuser=True)
                                   .first())

        self.groupadmin_test_group = AbakusGroup.objects.get(name='AbakusGroupAdminTest')
        self.groupadmin_test_group.add_user(self.with_permission)

        self.test_group = AbakusGroup.objects.get(name='TestGroup')
        self.test_group.add_user(self.without_permission)

        self.factory = APIRequestFactory()
        self.request = self.factory.get('/api/groups/')
        self.view = AbakusGroupViewSet.as_view({'get': 'retrieve'})

    def successful_retrieve(self, user, pk):
        force_authenticate(self.request, user=user)
        response = self.view(self.request, pk=pk)
        user = response.data
        keys = set(user.keys())

        self.assertEqual(response.status_code, 200)
        self.assertEqual(keys, set(AbakusGroupSerializer.Meta.fields))

    def test_without_auth(self):
        response = self.view(self.request)
        self.assertEqual(response.status_code, 401)

    def test_with_permission(self):
        self.successful_retrieve(self.with_permission, self.test_group.pk)

    def test_own_group(self):
        force_authenticate(self.request, user=self.without_permission)
        response = self.view(self.request, pk=self.test_group.pk)
        group = response.data
        keys = set(group.keys())

        self.assertEqual(response.status_code, 200)
        self.assertEqual(keys, set(AbakusGroupSerializer.Meta.fields))

    def test_without_permission(self):
        new_group = AbakusGroup.objects.create(name='new_group')

        force_authenticate(self.request, user=self.without_permission)
        response = self.view(self.request, pk=new_group.pk)
        group = response.data
        keys = set(group.keys())

        self.assertEqual(response.status_code, 200)
        self.assertEqual(keys, set(PublicAbakusGroupSerializer.Meta.fields))


class CreateAbakusGroupAPITestCase(APITestCase):
    fixtures = ['initial_permission_groups.yaml', 'test_abakus_groups.yaml', 'test_users.yaml']

    def setUp(self):
        self.all_groups = AbakusGroup.objects.all()

        self.with_permission = User.objects.get(username='abakusgroupadmin_test')
        self.without_permission = (User.objects
                                   .exclude(pk=self.with_permission.pk, is_superuser=True)
                                   .first())

        self.groupadmin_test_group = AbakusGroup.objects.get(name='AbakusGroupAdminTest')
        self.groupadmin_test_group.add_user(self.with_permission)

        self.test_group = AbakusGroup.objects.get(name='TestGroup')
        self.test_group.add_user(self.without_permission)

        self.factory = APIRequestFactory()
        self.request = self.factory.post('/api/groups/', test_group_data)
        self.view = AbakusGroupViewSet.as_view({'post': 'create'})

    def successful_create(self, user):
        force_authenticate(self.request, user=user)
        response = self.view(self.request)

        self.assertEqual(response.status_code, 201)
        created_group = AbakusGroup.objects.get(name=test_group_data['name'])

        for key, value in test_group_data.items():
            self.assertEqual(getattr(created_group, key), value)

    def test_without_auth(self):
        response = self.view(self.request)
        self.assertEqual(response.status_code, 401)

    def test_with_permission(self):
        self.successful_create(self.with_permission)

    def test_without_permission(self):
        force_authenticate(self.request, user=self.without_permission)
        response = self.view(self.request)

        self.assertEqual(response.status_code, 403)
        self.assertRaises(AbakusGroup.DoesNotExist, AbakusGroup.objects.get,
                          name=test_group_data['name'])
