from datetime import timedelta
from unittest import mock

from django.core.urlresolvers import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from lego.apps.events.models import Event
from lego.apps.users import constants
from lego.apps.users.models import AbakusGroup, Penalty, User
from lego.apps.users.serializers.users import DetailedUserSerializer
from lego.utils.test_utils import fake_time

_test_user_data = {
    'username': 'new_testuser',
    'first_name': 'new',
    'last_name': 'test_user',
    'email': 'new@testuser.com',
    'gender': 'male'
}


def _get_list_url():
    return reverse('api:v1:user-list')


def _get_registration_token_url(token):
    return f'{_get_list_url()}?token={token}'


def _get_detail_url(username):
    return reverse('api:v1:user-detail', kwargs={'username': username})


def get_test_user():
    user = User(**_test_user_data)
    user.save()

    return user


class ListUsersAPITestCase(APITestCase):
    fixtures = ['test_abakus_groups.yaml', 'test_users.yaml']

    def setUp(self):
        self.all_users = User.objects.all()
        self.with_permission = self.all_users.get(username='useradmin_test')
        self.useradmin_test_group = AbakusGroup.objects.get(name='UserAdminTest')
        self.useradmin_test_group.add_user(self.with_permission)
        self.without_permission = self.all_users.exclude(pk=self.with_permission.pk).first()

    def successful_list(self, user):
        self.client.force_authenticate(user=user)
        response = self.client.get(_get_list_url())

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data['results']), len(self.all_users))

    def test_without_auth(self):
        response = self.client.get(_get_list_url())
        self.assertEqual(response.status_code, 401)

    def test_with_normal_user(self):
        self.client.force_authenticate(user=self.without_permission)
        response = self.client.get(_get_list_url())

        self.assertEqual(response.status_code, 403)

    def test_with_useradmin(self):
        self.successful_list(self.with_permission)

    def test_with_super_user(self):
        self.successful_list(self.with_permission)


class RetrieveUsersAPITestCase(APITestCase):
    fixtures = ['test_abakus_groups.yaml', 'test_users.yaml']

    def setUp(self):
        self.all_users = User.objects.all()

        self.with_perm = self.all_users.get(username='useradmin_test')
        self.useradmin_test_group = AbakusGroup.objects.get(name='UserAdminTest')
        self.useradmin_test_group.add_user(self.with_perm)
        self.without_perm = self.all_users.exclude(pk=self.with_perm.pk).first()

        self.test_user = get_test_user()

    def successful_retrieve(self, user):
        self.client.force_authenticate(user=user)
        response = self.client.get(_get_detail_url(self.test_user.username))
        self.assertEqual(response.status_code, 200)

    def test_without_auth(self):
        response = self.client.get(_get_detail_url(self.all_users.first().username))
        self.assertEqual(response.status_code, 401)

    def test_with_normal_user(self):
        self.client.force_authenticate(user=self.without_perm)
        response = self.client.get(_get_detail_url(self.test_user.username))
        self.assertEqual(response.status_code, 200)

    def test_self_with_normal_user(self):
        self.client.force_authenticate(user=self.without_perm)
        response = self.client.get(_get_detail_url(self.without_perm.username))
        self.assertEqual(response.status_code, 200)

    def test_with_useradmin(self):
        self.successful_retrieve(self.with_perm)


class CreateUsersAPITestCase(APITestCase):
    fixtures = ['initial_abakus_groups.yaml', 'test_users.yaml']

    _test_registration_data = {
        'username': 'test_username',
        'first_name': 'Fornavn',
        'last_name': 'Etternavn',
        'gender': constants.OTHER,
        'password': 'TestPassord'
    }

    def setUp(self):
        self.existing_user = User.objects.all().first()
        self.new_email = 'testemail@test.com'
        self.new_email_other = 'testemailother@test.com'

    def create_token(self, email=None):
        token_email = email or self.new_email
        return User.generate_registration_token(token_email)

    def test_with_authenticated_user(self):
        self.client.force_authenticate(user=self.existing_user)
        response = self.client.post(_get_registration_token_url('randomToken'))
        self.assertEqual(response.status_code, 403)

    def test_without_token(self):
        response = self.client.post(_get_list_url())
        self.assertEqual(response.status_code, 400)

    def test_with_empty_token(self):
        response = self.client.post(_get_registration_token_url(''))
        self.assertEqual(response.status_code, 400)

    def test_with_invalid_token(self):
        response = self.client.post(_get_registration_token_url('InvalidToken'))
        self.assertEqual(response.status_code, 400)

    def test_with_no_data(self):
        token = self.create_token()
        response = self.client.post(_get_registration_token_url(token), {})
        self.assertEqual(response.status_code, 400)

    def test_with_existing_email(self):
        token = self.create_token('test1@user.com')
        response = self.client.post(
            _get_registration_token_url(token),
            self._test_registration_data
        )
        self.assertEqual(response.status_code, 400)

    def test_with_existing_username(self):
        token = self.create_token(self.new_email_other)
        invalid_data = self._test_registration_data.copy()
        invalid_data['username'] = 'test1'
        response = self.client.post(
            _get_registration_token_url(token),
            invalid_data
        )
        self.assertEqual(response.status_code, 400)

    def test_with_invalid_username(self):
        token = self.create_token(self.new_email_other)
        invalid_data = self._test_registration_data.copy()
        invalid_data['username'] = '$@@@@'
        response = self.client.post(
            _get_registration_token_url(token),
            invalid_data
        )
        self.assertEqual(response.status_code, 400)

    def test_with_valid_data(self):
        token = self.create_token(self.new_email_other)
        response = self.client.post(
            _get_registration_token_url(token),
            self._test_registration_data
        )
        self.assertEqual(response.status_code, 201)

        new_user = User.objects.get(email=self.new_email_other)

        # Test user data
        self.assertEqual(new_user.username, self._test_registration_data['username'])
        self.assertEqual(new_user.first_name, self._test_registration_data['first_name'])
        self.assertEqual(new_user.last_name, self._test_registration_data['last_name'])
        self.assertEqual(new_user.gender, self._test_registration_data['gender'])
        self.assertEqual(new_user.email, self.new_email_other)
        self.assertEqual(new_user.is_staff, False)
        self.assertEqual(new_user.is_superuser, False)
        self.assertEqual(new_user.is_abakus_member, False)
        self.assertEqual(new_user.is_abakom_member, False)

        # Test member groups
        user_group = AbakusGroup.objects.get(name=constants.USER_GROUP)
        self.assertEqual(user_group in new_user.all_groups, True)


class UpdateUsersAPITestCase(APITestCase):
    fixtures = ['test_abakus_groups.yaml', 'test_users.yaml']

    modified_user = {
        'username': 'modified_user',
        'first_name': 'modified',
        'last_name': 'user',
        'email': 'modified@testuser.com',
    }

    def setUp(self):
        self.all_users = User.objects.all()

        self.with_perm = self.all_users.get(username='useradmin_test')
        self.useradmin_test_group = AbakusGroup.objects.get(name='UserAdminTest')
        self.useradmin_test_group.add_user(self.with_perm)
        self.without_perm = self.all_users.exclude(pk=self.with_perm.pk).first()

        self.test_user = get_test_user()

    def successful_update(self, updater, update_object):
        self.client.force_authenticate(user=updater)
        response = self.client.patch(_get_detail_url(update_object.username), self.modified_user)
        user = User.objects.get(pk=update_object.pk)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(set(response.data.keys()), set(DetailedUserSerializer.Meta.fields))

        for key, value in self.modified_user.items():
            self.assertEqual(getattr(user, key), value)

    def test_self(self):
        self.successful_update(self.without_perm, self.without_perm)

    def test_with_useradmin(self):
        self.successful_update(self.with_perm, self.test_user)

    def test_other_with_normal_user(self):
        self.client.force_authenticate(user=self.without_perm)
        response = self.client.patch(_get_detail_url(self.test_user.username), self.modified_user)
        user = User.objects.get(pk=self.test_user.pk)

        self.assertEqual(response.status_code, 403)
        self.assertEqual(user, self.test_user)

    def test_update_with_super_user(self):
        self.successful_update(self.with_perm, self.test_user)

    def test_update_with_super_user_invalid_email(self):
        """It is not possible to set an email with our GSuite domain as the address domain."""
        self.client.force_login(self.with_perm)
        response = self.client.patch(_get_detail_url(self.test_user), {
            'email': 'webkom@abakus.no'
        })
        self.assertEquals(status.HTTP_400_BAD_REQUEST, response.status_code)


class DeleteUsersAPITestCase(APITestCase):
    fixtures = ['test_abakus_groups.yaml', 'test_users.yaml']

    _test_user_data = {
        'username': 'new_testuser',
        'first_name': 'new',
        'last_name': 'test_user',
        'email': 'new@testuser.com',
    }

    def setUp(self):
        self.all_users = User.objects.all()

        self.with_perm = self.all_users.get(username='useradmin_test')
        self.useradmin_test_group = AbakusGroup.objects.get(name='UserAdminTest')
        self.useradmin_test_group.add_user(self.with_perm)
        self.without_perm = self.all_users.exclude(pk=self.with_perm.pk).first()

        self.test_user = get_test_user()

    def successful_delete(self, user):
        self.client.force_authenticate(user=user)
        response = self.client.delete(_get_detail_url(self.test_user.username))

        self.assertEqual(response.status_code, 204)
        self.assertRaises(User.DoesNotExist, User.objects.get, pk=self.test_user.pk)

    def test_with_normal_user(self):
        self.client.force_authenticate(user=self.without_perm)
        response = self.client.delete(_get_detail_url(self.test_user.username))
        users = User.objects.filter(pk=self.test_user.pk)

        self.assertEqual(response.status_code, 403)
        self.assertTrue(len(users))

    def test_with_useradmin(self):
        self.successful_delete(self.with_perm)


class RetrieveSelfTestCase(APITestCase):
    fixtures = ['initial_abakus_groups.yaml', 'test_users.yaml', 'test_companies.yaml',
                'test_events.yaml']

    def setUp(self):
        self.user = User.objects.get(pk=1)

    def test_self_authed(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.get(reverse('api:v1:user-me'))

        self.assertEqual(response.status_code, 200)
        fields = (
            'id',
            'username',
            'first_name',
            'last_name',
            'full_name',
            'email',
            'is_staff',
            'is_active',
            'penalties'
        )
        for field in fields:
            if field == 'penalties':
                self.assertEqual(len(self.user.penalties.valid()), len(response.data['penalties']))
            else:
                self.assertEqual(getattr(self.user, field), response.data[field])

    def test_self_unauthed(self):
        response = self.client.get(reverse('api:v1:user-me'))
        self.assertEqual(response.status_code, 401)

    @mock.patch('django.utils.timezone.now', return_value=fake_time(2016, 10, 1))
    def test_own_penalties_serializer(self, mock_now):
        source = Event.objects.all().first()
        Penalty.objects.create(created_at=mock_now()-timedelta(days=20),
                               user=self.user, reason='test', weight=1, source_event=source)
        Penalty.objects.create(created_at=mock_now()-timedelta(days=19,
                                                               hours=23,
                                                               minutes=59),
                               user=self.user, reason='test', weight=1, source_event=source)
        self.client.force_authenticate(user=self.user)
        response = self.client.get(reverse('api:v1:user-me'))

        self.assertEqual(response.status_code, 200)

        self.assertEqual(len(self.user.penalties.valid()), len(response.data['penalties']))
        self.assertEqual(len(response.data['penalties']), 1)
        self.assertEqual(len(response.data['penalties'][0]), 5)
