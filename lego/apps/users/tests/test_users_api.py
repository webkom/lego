from datetime import date
from unittest import mock

from django.contrib.auth import authenticate
from django.urls import reverse
from rest_framework import status

from lego.apps.events.models import Event
from lego.apps.files.models import File
from lego.apps.users import constants
from lego.apps.users.constants import AUTUMN, SOCIAL_MEDIA_DOMAIN, WEBSITE_DOMAIN
from lego.apps.users.models import AbakusGroup, Penalty, PhotoConsent, User
from lego.apps.users.registrations import Registrations
from lego.utils.test_utils import BaseAPITestCase, fake_time

_test_user_data = {
    "username": "new_testuser",
    "first_name": "new",
    "last_name": "test_user",
    "email": "new@testuser.com",
    "gender": "male",
}

_test_pool = {
    "event": 1,
    "name": "Initial Pool",
    "capacity": 10,
    "activation_date": "2012-09-01T10:20:30Z",
    "permission_groups": [1],
}

_test_password = "test123"


def _get_list_url():
    return reverse("api:v1:user-list")


def _get_registration_token_url(token):
    return f"{_get_list_url()}?token={token}"


def _get_detail_url(username):
    return reverse("api:v1:user-detail", kwargs={"username": username})


def _get_delete_url():
    return "/api/v1/user-delete"


def get_test_user():
    user = User(**_test_user_data)
    user.save()

    return user


class ListUsersAPITestCase(BaseAPITestCase):
    fixtures = ["test_abakus_groups.yaml", "test_users.yaml"]

    def setUp(self):
        self.all_users = User.objects.all()
        self.with_permission = self.all_users.get(username="useradmin_test")
        self.useradmin_test_group = AbakusGroup.objects.get(name="UserAdminTest")
        self.useradmin_test_group.add_user(self.with_permission)
        self.without_permission = self.all_users.exclude(
            pk=self.with_permission.pk
        ).first()

    def successful_list(self, user):
        self.client.force_authenticate(user=user)
        response = self.client.get(_get_list_url())

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.json()["results"]), len(self.all_users))

    def test_without_auth(self):
        response = self.client.get(_get_list_url())
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_with_normal_user(self):
        self.client.force_authenticate(user=self.without_permission)
        response = self.client.get(_get_list_url())

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_with_useradmin(self):
        self.successful_list(self.with_permission)

    def test_with_super_user(self):
        self.successful_list(self.with_permission)


class RetrieveUsersAPITestCase(BaseAPITestCase):
    fixtures = ["test_abakus_groups.yaml", "test_users.yaml"]

    def setUp(self):
        self.all_users = User.objects.all()

        self.with_perm = self.all_users.get(username="useradmin_test")
        self.useradmin_test_group = AbakusGroup.objects.get(name="UserAdminTest")
        self.useradmin_test_group.add_user(self.with_perm)
        self.without_perm = self.all_users.exclude(pk=self.with_perm.pk).first()

        self.test_user = get_test_user()

    def successful_retrieve(self, user):
        self.client.force_authenticate(user=user)
        response = self.client.get(_get_detail_url(self.test_user.username))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_without_auth(self):
        response = self.client.get(_get_detail_url(self.all_users.first().username))
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_with_normal_user(self):
        self.client.force_authenticate(user=self.without_perm)
        response = self.client.get(_get_detail_url(self.test_user.username))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_self_with_normal_user(self):
        self.client.force_authenticate(user=self.without_perm)
        response = self.client.get(_get_detail_url(self.without_perm.username))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_with_useradmin(self):
        self.successful_retrieve(self.with_perm)


class CreateUsersAPITestCase(BaseAPITestCase):
    fixtures = ["test_abakus_groups.yaml", "test_users.yaml"]

    _test_registration_data = {
        "username": "test_username",
        "first_name": "Fornavn",
        "last_name": "Etternavn",
        "gender": constants.OTHER,
        "password": "TestPassord",
    }

    def setUp(self):
        self.existing_user = User.objects.all().first()
        self.new_email = "testemail@test.com"
        self.new_email_other = "testemailother@test.com"

    def create_token(self, email=None):
        token_email = email or self.new_email
        return Registrations.generate_registration_token(token_email)

    def test_with_authenticated_user(self):
        self.client.force_authenticate(user=self.existing_user)
        response = self.client.post(_get_registration_token_url("randomToken"))
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_without_token(self):
        response = self.client.post(_get_list_url())
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_with_empty_token(self):
        response = self.client.post(_get_registration_token_url(""))
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_with_invalid_token(self):
        response = self.client.post(_get_registration_token_url("InvalidToken"))
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_with_no_data(self):
        token = self.create_token()
        response = self.client.post(_get_registration_token_url(token), {})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_with_existing_email(self):
        token = self.create_token("test1@user.com")
        response = self.client.post(
            _get_registration_token_url(token), self._test_registration_data
        )
        self.assertEqual(response.status_code, status.HTTP_409_CONFLICT)

    def test_with_existing_username(self):
        token = self.create_token(self.new_email_other)
        invalid_data = self._test_registration_data.copy()
        invalid_data["username"] = "test1"
        response = self.client.post(_get_registration_token_url(token), invalid_data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_with_invalid_username(self):
        token = self.create_token(self.new_email_other)
        invalid_data = self._test_registration_data.copy()
        invalid_data["username"] = "$@@@@"
        response = self.client.post(_get_registration_token_url(token), invalid_data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_with_email_as_username(self):
        token = self.create_token(self.new_email_other)
        invalid_data = self._test_registration_data.copy()
        invalid_data["username"] = self.new_email_other
        response = self.client.post(_get_registration_token_url(token), invalid_data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_with_blank_username(self):
        token = self.create_token(self.new_email_other)
        invalid_data = self._test_registration_data.copy()
        invalid_data["username"] = ""
        response = self.client.post(_get_registration_token_url(token), invalid_data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_with_blank_password(self):
        token = self.create_token(self.new_email_other)
        invalid_data = self._test_registration_data.copy()
        invalid_data["password"] = ""
        response = self.client.post(_get_registration_token_url(token), invalid_data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_with_valid_data(self):
        token = self.create_token(self.new_email_other)
        response = self.client.post(
            _get_registration_token_url(token), self._test_registration_data
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        new_user = User.objects.get(email=self.new_email_other)

        # Test user data
        self.assertEqual(new_user.username, self._test_registration_data["username"])
        self.assertEqual(
            new_user.first_name, self._test_registration_data["first_name"]
        )
        self.assertEqual(new_user.last_name, self._test_registration_data["last_name"])
        self.assertEqual(new_user.gender, self._test_registration_data["gender"])
        self.assertEqual(new_user.email, self.new_email_other)
        self.assertEqual(new_user.is_staff, False)
        self.assertEqual(new_user.is_superuser, False)
        self.assertEqual(new_user.is_abakus_member, False)
        self.assertEqual(new_user.is_abakom_member, False)
        self.assertNotEqual(new_user.crypt_password_hash, "")

        # Test member groups
        user_group = AbakusGroup.objects.get(name=constants.USER_GROUP)
        self.assertEqual(user_group in new_user.all_groups, True)

        # Try to login with the user.
        self.assertTrue(authenticate(username="test_username", password="TestPassord"))


class UpdateUsersAPITestCase(BaseAPITestCase):
    fixtures = ["test_abakus_groups.yaml", "test_users.yaml", "test_files.yaml"]

    modified_user = {
        "username": "Modified_User",
        "firstName": "modified",
        "lastName": "user",
        "email": "modified@testuser.com",
    }

    def setUp(self):
        self.all_users = User.objects.all()

        self.with_perm = self.all_users.get(username="useradmin_test")
        self.useradmin_test_group = AbakusGroup.objects.get(name="UserAdminTest")
        self.abakom = AbakusGroup.objects.get(name="Abakom")
        self.abakom.add_user(self.with_perm)
        self.useradmin_test_group.add_user(self.with_perm)
        self.without_perm = self.all_users.exclude(pk=self.with_perm.pk).first()

        self.abakom.add_user(self.without_perm)

        self.test_user = get_test_user()

    def successful_update(self, updater, update_object):
        self.client.force_authenticate(user=updater)
        response = self.client.patch(
            _get_detail_url(update_object.username), self.modified_user
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        for key, value in self.modified_user.items():
            self.assertEqual(response.json()[key], value)

    def test_self(self):
        self.successful_update(self.without_perm, self.without_perm)

    def test_with_useradmin(self):
        self.successful_update(self.with_perm, self.test_user)

    def test_other_with_normal_user(self):
        self.client.force_authenticate(user=self.without_perm)
        response = self.client.patch(
            _get_detail_url(self.test_user.username), self.modified_user
        )
        user = User.objects.get(pk=self.test_user.pk)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(user, self.test_user)

    def test_update_with_super_user(self):
        self.successful_update(self.with_perm, self.test_user)

    def test_update_with_invalid_email(self):
        self.client.force_authenticate(self.with_perm)
        response = self.client.patch(
            _get_detail_url(self.test_user), {"email": "cat@gmail"}
        )

        self.assertEqual(["Enter a valid email address."], response.json()["email"])
        self.assertEqual(status.HTTP_400_BAD_REQUEST, response.status_code)

    def test_update_with_super_user_invalid_email(self):
        """It is not possible to set an email with our GSuite domain as the address domain."""
        self.client.force_authenticate(self.with_perm)
        response = self.client.patch(
            _get_detail_url(self.test_user), {"email": "webkom@abakus.no"}
        )

        self.assertEqual(status.HTTP_400_BAD_REQUEST, response.status_code)
        self.assertEqual(
            ["You can't use a abakus.no email for your personal account."],
            response.json()["email"],
        )

    def test_update_username_used_by_other(self):
        """Try to change username to something used by another user with different casing"""
        self.client.force_authenticate(self.without_perm)
        response = self.client.patch(
            _get_detail_url(self.without_perm.username),
            {"username": "usEradmin_TeSt"},  # Existing username with other casing
        )
        self.assertEqual(status.HTTP_400_BAD_REQUEST, response.status_code)

    def test_update_username_to_self(self):
        """Try to change casing on the current username"""
        self.client.force_authenticate(self.without_perm)
        response = self.client.patch(
            _get_detail_url(self.without_perm.username),
            {"username": self.without_perm.username.upper()},
        )
        self.assertEqual(status.HTTP_200_OK, response.status_code)

    def test_update_abakus_membership(self):
        """Try to change the is_abakus_member"""
        self.client.force_authenticate(self.without_perm)

        response = self.client.patch(
            _get_detail_url(self.without_perm.username), {"isAbakusMember": True}
        )
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        response = self.client.patch(
            _get_detail_url(self.without_perm.username), {"isAbakusMember": False}
        )
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        response = self.client.patch(
            _get_detail_url(self.without_perm.username), {"isAbakusMember": True}
        )
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual(response.json()["isAbakusMember"], True)

    def test_update_abakus_membership_when_not_student(self):
        """Try to change the is_abakus_member when user is not a student"""
        user = self.all_users.exclude(student_username__isnull=False).first()
        self.client.force_authenticate(user)
        response = self.client.patch(
            _get_detail_url(user.username), {"is_abakus_member": True}
        )
        self.assertEqual(status.HTTP_400_BAD_REQUEST, response.status_code)

    def test_update_not_failing_when_not_student(self):
        """Test the update method not failing when the user is not a student"""
        user = self.all_users.exclude(student_username__isnull=False).first()
        self.successful_update(user, user)

    def test_update_to_remove_profile_picture(self):
        """Try to remove profile picture by updating user with profilePicture equals null"""
        user = self.all_users.exclude(student_username__isnull=False).first()
        user.profile_picture = File.objects.get(key="abakus.png")
        user.save()
        self.client.force_authenticate(user)
        response = self.client.patch(
            _get_detail_url(user.username), {"profilePicture": None}
        )
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertTrue(
            response.json()["profilePicture"].endswith(user.get_default_picture())
        )


class DeleteUsersAPITestCase(BaseAPITestCase):
    fixtures = ["test_abakus_groups.yaml", "test_users.yaml"]

    def setUp(self):
        self.test_user = User.objects.create_user(
            **_test_user_data, password=_test_password
        )
        self.test_pass = _test_password

    def successful_delete(self):
        self.client.force_authenticate(user=self.test_user)
        response = self.client.post(_get_delete_url(), {"password": self.test_pass})

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertRaises(User.DoesNotExist, User.objects.get, pk=self.test_user.pk)

    def unsuccessful_delete(self):
        self.client.force_authenticate(user=self.test_user)
        response = self.client.post(_get_delete_url(), {"password": "wrongPassword123"})
        users = User.objects.filter(pk=self.test_user.pk)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertTrue(len(users))

    def test_obsolete_endpoint(self):
        self.with_perm = User.objects.all().get(username="useradmin_test")
        self.useradmin_test_group = AbakusGroup.objects.get(name="UserAdminTest")
        self.useradmin_test_group.add_user(self.with_perm)
        self.client.force_authenticate(user=self.with_perm)
        response = self.client.delete(_get_detail_url(self.test_user.username))
        users = User.objects.filter(pk=self.test_user.pk)

        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
        self.assertTrue(len(users))


class RetrieveSelfTestCase(BaseAPITestCase):
    fixtures = [
        "test_abakus_groups.yaml",
        "test_users.yaml",
        "test_companies.yaml",
        "test_events.yaml",
    ]

    def setUp(self):
        self.user = User.objects.get(pk=1)

    def test_self_authed(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.get(reverse("api:v1:user-me"))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            len(self.user.penalties.valid()), len(response.json()["penalties"])
        )
        data = response.json()
        self.assertEqual(self.user.id, data["id"])

        self.assertEqual(self.user.username, data["username"])
        self.assertEqual(self.user.first_name, data["firstName"])
        self.assertEqual(self.user.last_name, data["lastName"])
        self.assertEqual(self.user.full_name, data["fullName"])
        self.assertEqual(self.user.email, data["email"])
        self.assertEqual(self.user.is_active, data["isActive"])

    def test_self_unauthed(self):
        response = self.client.get(reverse("api:v1:user-me"))
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    @mock.patch("django.utils.timezone.now", return_value=fake_time(2016, 10, 1))
    def test_own_penalties_serializer(self, mock_now):
        event1 = Event.objects.create(
            title="A simple event",
            event_type=0,
            start_time=mock_now(),
            end_time=mock_now(),
        )

        Penalty.objects.create(
            user=self.user,
            reason="test",
            weight=1,
            source_event=event1,
        )

        self.client.force_authenticate(user=self.user)
        response = self.client.get(reverse("api:v1:user-me"))

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.assertEqual(
            len(self.user.penalties.valid()), len(response.json()["penalties"])
        )
        self.assertEqual(len(response.json()["penalties"]), 1)
        self.assertEqual(len(response.json()["penalties"][0]), 7)


class UpdatePhotoConsentTestCase(BaseAPITestCase):
    fixtures = [
        "test_users.yaml",
    ]

    def setUp(self):
        self.current_semester = AUTUMN
        self.current_year = date.today().year
        self.test_user = User.objects.get(pk=1)
        self.other_user = User.objects.get(pk=2)
        self.test_user_url = (
            f"/api/v1/users/{self.test_user.username}/update_photo_consent/"
        )
        PhotoConsent.objects.create(
            user=self.test_user,
            year=self.current_year,
            semester=self.current_semester,
            domain=WEBSITE_DOMAIN,
            is_consenting=None,
        )

    def test_update_own_existing_consent(self):
        self.client.force_authenticate(user=self.test_user)
        response = self.client.post(
            self.test_user_url,
            {
                "user": self.test_user.id,
                "year": self.current_year,
                "semester": self.current_semester,
                "domain": WEBSITE_DOMAIN,
                "isConsenting": True,
            },
        )
        updated_consent = self.test_user.photo_consents.get(
            year=self.current_year,
            semester=self.current_semester,
            domain=WEBSITE_DOMAIN,
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(updated_consent.is_consenting)
        self.assertIsNotNone(updated_consent.updated_at)

    def test_update_own_non_existing_consent(self):
        self.client.force_authenticate(user=self.test_user)
        consent_exists = self.test_user.photo_consents.filter(
            year=self.current_year,
            semester=self.current_semester,
            domain=SOCIAL_MEDIA_DOMAIN,
        ).exists()
        self.assertFalse(consent_exists)

        response = self.client.post(
            self.test_user_url,
            {
                "user": self.test_user.id,
                "year": self.current_year,
                "semester": self.current_semester,
                "domain": SOCIAL_MEDIA_DOMAIN,
                "isConsenting": False,
            },
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        created_consent = self.test_user.photo_consents.get(
            year=self.current_year,
            semester=self.current_semester,
            domain=SOCIAL_MEDIA_DOMAIN,
        )
        self.assertFalse(created_consent.is_consenting)

    def test_update_other_user_consent(self):
        self.client.force_authenticate(user=self.other_user)

        response = self.client.post(
            self.test_user_url,
            {
                "user": self.test_user.id,
                "year": self.current_year,
                "semester": self.current_semester,
                "domain": WEBSITE_DOMAIN,
                "isConsenting": False,
            },
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        consent = self.test_user.photo_consents.get(
            year=self.current_year,
            semester=self.current_semester,
            domain=WEBSITE_DOMAIN,
        )
        self.assertIsNone(consent.is_consenting)
