# -*- coding: utf8 -*-
from rest_framework.test import APITestCase, APIRequestFactory, force_authenticate

from lego.users.serializers import DetailedAbakusGroupSerializer, PublicAbakusGroupSerializer
from lego.users.views.abakus_groups import AbakusGroupViewSet
from lego.users.models import User, AbakusGroup, Membership

test_group_data = {
    'name': 'testgroup',
    'description': 'test group',
}


class ListAbakusGroupAPITestCase(APITestCase):
    fixtures = ['initial_permission_groups.yaml', 'test_abakus_groups.yaml', 'test_users.yaml']

    def setUp(self):
        self.all_groups = AbakusGroup.objects.all()

        self.user = User.objects.get(username='test1')

        self.factory = APIRequestFactory()
        self.request = self.factory.get('/api/groups/')
        self.view = AbakusGroupViewSet.as_view({'get': 'list'})

    def successful_list(self, user):
        force_authenticate(self.request, user=user)
        response = self.view(self.request)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), len(self.all_groups))

        for group in response.data:
            keys = set(group.keys())
            self.assertEqual(keys, set(PublicAbakusGroupSerializer.Meta.fields))

    def test_without_auth(self):
        response = self.view(self.request)
        self.assertEqual(response.status_code, 401)

    def test_with_auth(self):
        self.successful_list(self.user)


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
        self.assertEqual(keys, set(DetailedAbakusGroupSerializer.Meta.fields))

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
        self.assertEqual(keys, set(DetailedAbakusGroupSerializer.Meta.fields))

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


class UpdateAbakusGroupAPITestCase(APITestCase):
    fixtures = ['initial_permission_groups.yaml', 'test_abakus_groups.yaml', 'test_users.yaml']

    def setUp(self):
        self.all_groups = AbakusGroup.objects.all()
        parent_group = AbakusGroup.objects.create(name='parent_group')
        self.modified_group = {
            'name': 'modified_group',
            'description': 'this is a modified group',
            'parent': parent_group.pk
        }

        self.with_permission = User.objects.get(username='abakusgroupadmin_test')
        self.without_permission = (User.objects
                                   .exclude(pk=self.with_permission.pk, is_superuser=True)
                                   .first())

        self.test_group = AbakusGroup.objects.get(name='TestGroup')
        self.leader = User.objects.create(username='leader')
        self.test_group.add_user(self.leader, role=Membership.LEADER)

        self.groupadmin_test_group = AbakusGroup.objects.get(name='AbakusGroupAdminTest')
        self.groupadmin_test_group.add_user(self.with_permission)

        self.factory = APIRequestFactory()
        self.request = self.factory.put('/api/groups/{0}/'.format(self.test_group.pk)
                                        , self.modified_group)
        self.view = AbakusGroupViewSet.as_view({'put': 'update'})

    def successful_update(self, user):
        force_authenticate(self.request, user=user)
        response = self.view(self.request, pk=self.test_group.pk)
        group = AbakusGroup.objects.get(pk=self.test_group.pk)

        self.assertEqual(response.status_code, 200)

        self.assertEqual(group.name, self.modified_group['name'])
        self.assertEqual(group.description, self.modified_group['description'])
        self.assertEqual(group.parent.pk, self.modified_group['parent'])

    def test_without_auth(self):
        response = self.view(self.request, pk=self.test_group.pk)
        self.assertEqual(response.status_code, 401)

    def test_with_permission(self):
        self.successful_update(self.with_permission)

    def test_without_permission(self):
        force_authenticate(self.request, user=self.without_permission)
        response = self.view(self.request, pk=self.test_group.pk)

        self.assertEqual(response.status_code, 403)

    def test_as_leader(self):
        self.successful_update(self.leader)
