# -*- coding: utf8 -*-
from django.core.urlresolvers import reverse
from rest_framework.test import APITestCase

from lego.users.models import AbakusGroup, Membership, User
from lego.users.serializers import DetailedAbakusGroupSerializer, PublicAbakusGroupSerializer

test_group_data = {
    'name': 'testgroup',
    'description': 'test group',
}


get_detail_url = lambda pk: reverse('abakusgroup-detail', kwargs={'pk': pk})
get_list_url = lambda: reverse('abakusgroup-list')


class ListAbakusGroupAPITestCase(APITestCase):
    fixtures = ['initial_permission_groups.yaml', 'test_abakus_groups.yaml', 'test_users.yaml']

    def setUp(self):
        self.all_groups = AbakusGroup.objects.all()
        self.user = User.objects.get(username='test1')

    def successful_list(self, user):
        self.client.force_authenticate(user=user)
        response = self.client.get(get_list_url())

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), len(self.all_groups))

        for group in response.data:
            keys = set(group.keys())
            self.assertEqual(keys, set(PublicAbakusGroupSerializer.Meta.fields))

    def test_without_auth(self):
        response = self.client.get(get_list_url())
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

    def successful_retrieve(self, user, pk):
        self.client.force_authenticate(user=user)
        response = self.client.get(get_detail_url(pk))
        user = response.data
        keys = set(user.keys())

        self.assertEqual(response.status_code, 200)
        self.assertEqual(keys, set(DetailedAbakusGroupSerializer.Meta.fields))

    def test_without_auth(self):
        response = self.client.get(get_detail_url(1))
        self.assertEqual(response.status_code, 401)

    def test_with_permission(self):
        self.successful_retrieve(self.with_permission, self.test_group.pk)

    def test_own_group(self):
        self.client.force_authenticate(user=self.without_permission)
        response = self.client.get(get_detail_url(self.test_group.pk))
        group = response.data
        keys = set(group.keys())

        self.assertEqual(response.status_code, 200)
        self.assertEqual(keys, set(DetailedAbakusGroupSerializer.Meta.fields))

    def test_without_permission(self):
        new_group = AbakusGroup.objects.create(name='new_group')

        self.client.force_authenticate(user=self.without_permission)
        response = self.client.get(get_detail_url(new_group.pk))
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

    def successful_create(self, user):
        self.client.force_authenticate(user=user)
        response = self.client.post(get_list_url(), test_group_data)

        self.assertEqual(response.status_code, 201)
        created_group = AbakusGroup.objects.get(name=test_group_data['name'])

        for key, value in test_group_data.items():
            self.assertEqual(getattr(created_group, key), value)

    def test_without_auth(self):
        response = self.client.post(get_list_url(), test_group_data)
        self.assertEqual(response.status_code, 401)

    def test_with_permission(self):
        self.successful_create(self.with_permission)

    def test_without_permission(self):
        self.client.force_authenticate(user=self.without_permission)
        response = self.client.post(get_list_url(), test_group_data)

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

    def successful_update(self, user):
        self.client.force_authenticate(user=user)
        response = self.client.put(get_detail_url(self.test_group.pk),
                                   self.modified_group)
        group = AbakusGroup.objects.get(pk=self.test_group.pk)

        self.assertEqual(response.status_code, 200)

        self.assertEqual(group.name, self.modified_group['name'])
        self.assertEqual(group.description, self.modified_group['description'])
        self.assertEqual(group.parent.pk, self.modified_group['parent'])

    def test_without_auth(self):
        response = self.client.put(get_detail_url(self.test_group.pk),
                                   self.modified_group)
        self.assertEqual(response.status_code, 401)

    def test_with_permission(self):
        self.successful_update(self.with_permission)

    def test_without_permission(self):
        self.client.force_authenticate(user=self.without_permission)
        response = self.client.put(get_detail_url(self.test_group.pk),
                                   self.modified_group)

        self.assertEqual(response.status_code, 403)

    def test_as_leader(self):
        self.successful_update(self.leader)


class DeleteAbakusGroupAPITestCase(APITestCase):
    fixtures = ['initial_permission_groups.yaml', 'test_abakus_groups.yaml', 'test_users.yaml']

    def setUp(self):
        self.all_groups = AbakusGroup.objects.all()

        self.with_permission = User.objects.get(username='abakusgroupadmin_test')
        self.without_permission = (User.objects
                                   .exclude(pk=self.with_permission.pk, is_superuser=True)
                                   .first())

        self.test_group = AbakusGroup.objects.get(name='TestGroup')
        self.leader = User.objects.create(username='leader')
        self.test_group.add_user(self.leader, role=Membership.LEADER)

        self.groupadmin_test_group = AbakusGroup.objects.get(name='AbakusGroupAdminTest')
        self.groupadmin_test_group.add_user(self.with_permission)

    def successful_delete(self, user):
        self.client.force_authenticate(user=user)
        response = self.client.delete(get_detail_url(self.test_group.pk))

        self.assertEqual(response.status_code, 204)
        self.assertRaises(AbakusGroup.DoesNotExist, AbakusGroup.objects.get, pk=self.test_group.pk)

    def test_without_auth(self):
        response = self.client.delete(get_detail_url(self.test_group.pk))
        self.assertEqual(response.status_code, 401)

    def test_with_permission(self):
        self.successful_delete(self.with_permission)

    def test_without_permission(self):
        self.client.force_authenticate(user=self.without_permission)
        response = self.client.delete(get_detail_url(self.test_group.pk))

        self.assertEqual(response.status_code, 403)

    def test_unsuccessful_delete_as_leader(self):
        self.client.force_authenticate(user=self.leader)
        response = self.client.delete(get_detail_url(self.test_group.pk))

        self.assertEqual(response.status_code, 403)
