from django.core.urlresolvers import reverse
from rest_framework.test import APITestCase

from lego.apps.social_groups.models import InterestGroup
from lego.apps.users.models import AbakusGroup, Membership, User

_test_group_data = {
    'name': 'testnewinterestgroup',
    'description': 'test new interest group',
    'description_long': 'hooooooly moly'
}

_serializer_fields = (
    'id',
    'name',
    'number_of_users',
    'description',
    'description_long',
    'permissions'
)

_rendered_serializer_fields = (
    'id',
    'name',
    'numberOfUsers',
    'description',
    'descriptionLong',
    'permissions'
)


def _get_list_url():
    return reverse('api:v1:interestgroup-list')


def _get_detail_url(pk):
    return reverse('api:v1:interestgroup-detail', kwargs={'pk': pk})


class ListInterestGroupAPITestCase(APITestCase):
    fixtures = ['test_abakus_groups.yaml', 'test_users.yaml', 'test_interest_groups.yaml']

    def setUp(self):
        self.interest_groups = InterestGroup.objects.all()
        self.user = User.objects.get(username='test1')

    def successful_list(self, user):
        self.client.force_authenticate(user=user)
        response = self.client.get(_get_list_url())

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), len(self.interest_groups))

        for group in response.data:
            keys = set(group.keys())
            self.assertEqual(keys, set(_rendered_serializer_fields))

    def test_without_auth(self):
        response = self.client.get(_get_list_url())
        self.assertEqual(response.status_code, 401)

    def test_with_auth(self):
        self.successful_list(self.user)


class RetrieveInterestGroupAPITestCase(APITestCase):
    fixtures = ['test_abakus_groups.yaml', 'test_users.yaml', 'test_interest_groups.yaml']

    def setUp(self):
        self.interest_groups = InterestGroup.objects.all()

        self.with_permission = User.objects.get(username='interestgroupadmin_test')
        self.without_permission = (User.objects
                                   .exclude(pk=self.with_permission.pk)
                                   .first())

        self.groupadmin_test_group = AbakusGroup.objects.get(name='InterestGroupAdminTest')
        self.groupadmin_test_group.add_user(self.with_permission)

        self.test_interest_group = InterestGroup.objects.get(name='TestInterestGroup')
        self.test_interest_group.add_user(self.without_permission)

    def successful_retrieve(self, user, pk):
        self.client.force_authenticate(user=user)
        response = self.client.get(_get_detail_url(pk))
        group = response.data
        keys = set(group.keys())

        self.assertEqual(group['number_of_users'], 1)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(keys, set(_serializer_fields))

    def test_without_auth(self):
        response = self.client.get(_get_detail_url(1))
        self.assertEqual(response.status_code, 401)

    def test_with_permission(self):
        self.successful_retrieve(self.with_permission, self.test_interest_group.pk)

    def test_own_group(self):
        self.client.force_authenticate(user=self.without_permission)
        response = self.client.get(_get_detail_url(self.test_interest_group.pk))
        group = response.data
        keys = set(group.keys())

        self.assertEqual(response.status_code, 200)
        self.assertEqual(keys, set(_serializer_fields))

    def test_without_permission(self):
        new_group = InterestGroup.objects.create(name='new_group')

        self.client.force_authenticate(user=self.without_permission)
        response = self.client.get(_get_detail_url(new_group.pk))
        group = response.data
        keys = set(group.keys())

        self.assertEqual(response.status_code, 200)
        self.assertEqual(keys, set(_serializer_fields))


class CreateInterestGroupAPITestCase(APITestCase):
    fixtures = ['test_abakus_groups.yaml', 'test_users.yaml', 'test_interest_groups.yaml']

    def setUp(self):
        self.interest_groups = InterestGroup.objects.all()

        self.with_permission = User.objects.get(username='interestgroupadmin_test')
        self.without_permission = (User.objects
                                   .exclude(pk=self.with_permission.pk)
                                   .first())

        self.groupadmin_test_group = AbakusGroup.objects.get(name='InterestGroupAdminTest')
        self.groupadmin_test_group.add_user(self.with_permission)

        self.test_interest_group = InterestGroup.objects.get(name='TestInterestGroup')
        self.test_interest_group.add_user(self.without_permission)

    def successful_create(self, user):
        self.client.force_authenticate(user=user)
        response = self.client.post(_get_list_url(), _test_group_data)

        self.assertEqual(response.status_code, 201)
        created_group = InterestGroup.objects.get(name=_test_group_data['name'])

        for key, value in _test_group_data.items():
            self.assertEqual(getattr(created_group, key), value)

    def test_create_validate_permissions(self):
        self.client.force_authenticate(user=self.with_permission)
        group = {
            'name': 'permissiontestinterestgroup',
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
        self.assertRaises(InterestGroup.DoesNotExist, InterestGroup.objects.get,
                          name=_test_group_data['name'])


class UpdateInterestGroupAPITestCase(APITestCase):
    fixtures = ['test_abakus_groups.yaml', 'test_users.yaml', 'test_interest_groups.yaml']

    def setUp(self):
        self.interest_groups = InterestGroup.objects.all()
        parent_group = AbakusGroup.objects.get(name='Interessegrupper')
        self.modified_group = {
            'name': 'modified_interest_group',
            'description': 'this is a modified interest group',
            'description_long': 'this is a modified interest group with a larger description',
            'parent': parent_group.pk
        }

        self.with_permission = User.objects.get(username='interestgroupadmin_test')
        self.without_permission = (User.objects
                                   .exclude(pk=self.with_permission.pk)
                                   .first())

        self.test_interest_group = InterestGroup.objects.get(name='TestInterestGroup')
        self.leader = User.objects.create(username='leader')
        self.test_interest_group.add_user(self.leader, role=Membership.LEADER)

        self.groupadmin_test_group = AbakusGroup.objects.get(name='InterestGroupAdminTest')
        self.groupadmin_test_group.add_user(self.with_permission)

    def successful_update(self, user):
        self.client.force_authenticate(user=user)
        response = self.client.put(_get_detail_url(self.test_interest_group.pk),
                                   self.modified_group)
        group = InterestGroup.objects.get(pk=self.test_interest_group.pk)

        self.assertEqual(response.status_code, 200)

        self.assertEqual(group.name, self.modified_group['name'])
        self.assertEqual(group.description, self.modified_group['description'])
        self.assertEqual(group.parent.pk, self.modified_group['parent'])

    def test_without_auth(self):
        response = self.client.put(_get_detail_url(self.test_interest_group.pk),
                                   self.modified_group)
        self.assertEqual(response.status_code, 401)

    def test_with_permission(self):
        self.successful_update(self.with_permission)

    def test_without_permission(self):
        self.client.force_authenticate(user=self.without_permission)
        response = self.client.put(_get_detail_url(self.test_interest_group.pk),
                                   self.modified_group)

        self.assertEqual(response.status_code, 403)

    def test_as_leader(self):
        self.successful_update(self.leader)


class DeleteInterestGroupAPITestCase(APITestCase):
    fixtures = ['test_abakus_groups.yaml', 'test_users.yaml', 'test_interest_groups.yaml']

    def setUp(self):
        self.interest_groups = InterestGroup.objects.all()

        self.with_permission = User.objects.get(username='interestgroupadmin_test')
        self.without_permission = (User.objects
                                   .exclude(pk=self.with_permission.pk)
                                   .first())

        self.test_interest_group = InterestGroup.objects.get(name='TestInterestGroup')
        self.leader = User.objects.create(username='leader')
        self.test_interest_group.add_user(self.leader, role=Membership.LEADER)

        self.groupadmin_test_group = AbakusGroup.objects.get(name='InterestGroupAdminTest')
        self.groupadmin_test_group.add_user(self.with_permission)

    def successful_delete(self, user):
        self.client.force_authenticate(user=user)
        response = self.client.delete(_get_detail_url(self.test_interest_group.pk))

        self.assertEqual(response.status_code, 204)
        self.assertRaises(InterestGroup.DoesNotExist, InterestGroup.group_objects.get,
                          pk=self.test_interest_group.pk)

    def test_without_auth(self):
        response = self.client.delete(_get_detail_url(self.test_interest_group.pk))
        self.assertEqual(response.status_code, 401)

    def test_with_permission(self):
        self.successful_delete(self.with_permission)

    def test_without_permission(self):
        self.client.force_authenticate(user=self.without_permission)
        response = self.client.delete(_get_detail_url(self.test_interest_group.pk))

        self.assertEqual(response.status_code, 403)

    def test_unsuccessful_delete_as_leader(self):
        self.client.force_authenticate(user=self.leader)
        response = self.client.delete(_get_detail_url(self.test_interest_group.pk))

        self.assertEqual(response.status_code, 403)
