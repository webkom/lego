from django.core.urlresolvers import reverse
from rest_framework.test import APITestCase

from lego.apps.social_groups.models import InterestGroup
from lego.apps.users import constants
from lego.apps.users.constants import LEADER
from lego.apps.users.models import AbakusGroup, User, Membership
from lego.apps.users.serializers.abakus_groups import (DetailedAbakusGroupSerializer,
                                                       PublicAbakusGroupSerializer)

_test_group_data = {
    'name': 'testgroup',
    'description': 'test group',
}


def _get_list_url():
    return reverse('api:v1:abakusgroup-list')


def _get_membership_url(pk):
    return reverse('api:v1:abakusgroup-memberships-list', kwargs={'group_pk': pk})


def _get_detail_url(pk):
    return reverse('api:v1:abakusgroup-detail', kwargs={'pk': pk})


class ListAbakusGroupAPITestCase(APITestCase):
    fixtures = ['test_abakus_groups.yaml', 'test_users.yaml']

    def setUp(self):
        self.all_groups = AbakusGroup.objects.all()
        self.user = User.objects.get(username='test1')

    def successful_list(self, user):
        self.client.force_authenticate(user=user)
        response = self.client.get(_get_list_url())

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data['results']), len(self.all_groups))

        for group in response.data['results']:
            keys = set(group.keys())
            self.assertEqual(keys, set(PublicAbakusGroupSerializer.Meta.fields))

    def test_without_auth(self):
        response = self.client.get(_get_list_url())
        self.assertEqual(response.status_code, 401)

    def test_with_auth(self):
        self.successful_list(self.user)


class RetrieveAbakusGroupAPITestCase(APITestCase):
    fixtures = ['test_abakus_groups.yaml', 'test_users.yaml']

    def setUp(self):
        self.all_groups = AbakusGroup.objects.all()

        self.with_permission = User.objects.get(username='abakusgroupadmin_test')
        self.without_permission = (User.objects
                                   .exclude(pk=self.with_permission.pk)
                                   .first())

        self.groupadmin_test_group = AbakusGroup.objects.get(name='AbakusGroupAdminTest')
        self.groupadmin_test_group.add_user(self.with_permission)

        self.test_group = AbakusGroup.objects.get(name='TestGroup')
        self.test_group.add_user(self.without_permission, role=LEADER)

    def successful_retrieve(self, user, pk):
        self.client.force_authenticate(user=user)
        response = self.client.get(_get_detail_url(pk))
        user = response.data
        keys = set(user.keys())
        keys.remove('action_grant')

        self.assertEqual(len(user['memberships']), 1)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(keys, set(DetailedAbakusGroupSerializer.Meta.fields))

    def test_without_auth(self):
        response = self.client.get(_get_detail_url(1))
        self.assertEqual(response.status_code, 401)

    def test_with_permission(self):
        self.successful_retrieve(self.with_permission, self.test_group.pk)

    def test_own_group(self):
        self.client.force_authenticate(user=self.without_permission)
        response = self.client.get(_get_detail_url(self.test_group.pk))
        group = response.data
        keys = set(group.keys())
        keys.remove('action_grant')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(keys, set(DetailedAbakusGroupSerializer.Meta.fields))

    def test_without_permission(self):
        new_group = AbakusGroup.objects.create(name='new_group')

        self.client.force_authenticate(user=self.without_permission)
        response = self.client.get(_get_detail_url(new_group.pk))
        group = response.data
        keys = set(group.keys())
        keys.remove('action_grant')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(keys, set(PublicAbakusGroupSerializer.Meta.fields))


class CreateAbakusGroupAPITestCase(APITestCase):
    fixtures = ['test_abakus_groups.yaml', 'test_users.yaml']

    def setUp(self):
        self.all_groups = AbakusGroup.objects.all()

        self.with_permission = User.objects.get(username='abakusgroupadmin_test')
        self.without_permission = (User.objects
                                   .exclude(pk=self.with_permission.pk)
                                   .first())

        self.groupadmin_test_group = AbakusGroup.objects.get(name='AbakusGroupAdminTest')
        self.groupadmin_test_group.add_user(self.with_permission)

        self.test_group = AbakusGroup.objects.get(name='TestGroup')
        self.test_group.add_user(self.without_permission)

    def successful_create(self, user):
        self.client.force_authenticate(user=user)
        response = self.client.post(_get_list_url(), _test_group_data)

        self.assertEqual(response.status_code, 201)
        created_group = AbakusGroup.objects.get(name=_test_group_data['name'])

        for key, value in _test_group_data.items():
            self.assertEqual(getattr(created_group, key), value)

    def test_create_validate_permissions(self):
        self.client.force_authenticate(user=self.with_permission)
        group = {
            'name': 'permissiontestgroup',
            'permissions': ['/valid/', '/invalid123']
        }

        expected_data = {'permissions': [
            'Keyword permissions can only contain forward slashes and letters and must begin '
            'and end with a forward slash'
        ]}

        response = self.client.post(_get_list_url(), group)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(expected_data, response.data)

    def test_without_auth(self):
        response = self.client.post(_get_list_url(), _test_group_data)
        self.assertEqual(response.status_code, 401)

    def test_with_permission(self):
        self.successful_create(self.with_permission)

    def test_without_permission(self):
        self.client.force_authenticate(user=self.without_permission)
        response = self.client.post(_get_list_url(), _test_group_data)

        self.assertEqual(response.status_code, 403)
        self.assertRaises(AbakusGroup.DoesNotExist, AbakusGroup.objects.get,
                          name=_test_group_data['name'])


class UpdateAbakusGroupAPITestCase(APITestCase):
    fixtures = ['test_abakus_groups.yaml', 'test_users.yaml']

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
                                   .exclude(pk=self.with_permission.pk)
                                   .first())

        self.test_group = AbakusGroup.objects.get(name='TestGroup')
        self.leader = User.objects.create(username='leader')
        self.test_group.add_user(self.leader, role=constants.LEADER)

        self.groupadmin_test_group = AbakusGroup.objects.get(name='AbakusGroupAdminTest')
        self.groupadmin_test_group.add_user(self.with_permission)

    def successful_update(self, user):
        self.client.force_authenticate(user=user)
        response = self.client.put(_get_detail_url(self.test_group.pk),
                                   self.modified_group)
        group = AbakusGroup.objects.get(pk=self.test_group.pk)

        self.assertEqual(response.status_code, 200)

        self.assertEqual(group.name, self.modified_group['name'])
        self.assertEqual(group.description, self.modified_group['description'])
        self.assertEqual(group.parent.pk, self.modified_group['parent'])

    def test_without_auth(self):
        response = self.client.put(_get_detail_url(self.test_group.pk),
                                   self.modified_group)
        self.assertEqual(response.status_code, 401)

    def test_with_permission(self):
        self.successful_update(self.with_permission)

    def test_without_permission(self):
        self.client.force_authenticate(user=self.without_permission)
        response = self.client.put(_get_detail_url(self.test_group.pk),
                                   self.modified_group)

        self.assertEqual(response.status_code, 403)

    def test_as_leader(self):
        self.successful_update(self.leader)


class DeleteAbakusGroupAPITestCase(APITestCase):
    fixtures = ['test_abakus_groups.yaml', 'test_users.yaml']

    def setUp(self):
        self.all_groups = AbakusGroup.objects.all()

        self.with_permission = User.objects.get(username='abakusgroupadmin_test')
        self.without_permission = (User.objects
                                   .exclude(pk=self.with_permission.pk)
                                   .first())

        self.test_group = AbakusGroup.objects.get(name='TestGroup')
        self.leader = User.objects.create(username='leader')
        self.test_group.add_user(self.leader, role=constants.LEADER)

        self.groupadmin_test_group = AbakusGroup.objects.get(name='AbakusGroupAdminTest')
        self.groupadmin_test_group.add_user(self.with_permission)

    def successful_delete(self, user):
        self.client.force_authenticate(user=user)
        response = self.client.delete(_get_detail_url(self.test_group.pk))

        self.assertEqual(response.status_code, 204)
        self.assertRaises(AbakusGroup.DoesNotExist, AbakusGroup.objects.get,
                          pk=self.test_group.pk)

    def test_without_auth(self):
        response = self.client.delete(_get_detail_url(self.test_group.pk))
        self.assertEqual(response.status_code, 401)

    def test_with_permission(self):
        self.successful_delete(self.with_permission)

    def test_without_permission(self):
        self.client.force_authenticate(user=self.without_permission)
        response = self.client.delete(_get_detail_url(self.test_group.pk))

        self.assertEqual(response.status_code, 403)

    def test_unsuccessful_delete_as_leader(self):
        self.client.force_authenticate(user=self.leader)
        response = self.client.delete(_get_detail_url(self.test_group.pk))

        self.assertEqual(response.status_code, 403)


class InterestGroupAPITestCase(APITestCase):
    fixtures = ['test_abakus_groups.yaml', 'test_users.yaml']

    def setUp(self):
        self.abakus = AbakusGroup.objects.get(name='Abakus')
        self.interest_group = InterestGroup.objects.get(name='AbaBrygg')
        self.abakule = User.objects.get(username='abakule')
        self.leader = User.objects.get(username='test2')

        self.abakus.add_user(self.abakule)
        self.abakus.add_user(self.leader)

        self.interest_group.add_user(self.leader, role='leader')

    def test_can_list_memberships(self):
        self.client.force_authenticate(user=self.abakule)
        response = self.client.get(_get_membership_url(self.interest_group.pk))

        self.assertEquals(response.status_code, 200)

    def test_can_join_interest_group(self):
        self.client.force_authenticate(user=self.abakule)
        response = self.client.post(_get_membership_url(self.interest_group.pk), {
            'user': self.abakule.pk,
            'role': 'member'
        })
        self.assertEquals(response.status_code, 201)

    def test_cannot_join_for_another(self):
        self.client.force_authenticate(user=self.abakule)
        other = User.objects.exclude(id=self.abakule.pk).first()
        response = self.client.post(_get_membership_url(self.interest_group.pk), {
            'user': other.pk,
            'role': 'member'
        })
        self.assertEquals(response.status_code, 403)

    def test_leader_can_do_whatever(self):
        self.client.force_authenticate(user=self.leader)
        response = self.client.post(_get_membership_url(self.interest_group.pk), {
            'user': self.abakule.pk,
            'role': 'member'
        })
        self.assertEquals(response.status_code, 201)

        response = self.client.delete(_get_membership_url(self.interest_group.pk), {
            'user': self.abakule.pk,
            'role': 'member'
        })
        # TODO(mht): return value here ?
        self.assertEquals(response.status_code, 201)

