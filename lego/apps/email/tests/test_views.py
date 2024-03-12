from rest_framework import status

from lego.apps.email.models import EmailAddress, EmailList
from lego.apps.users.models import AbakusGroup, Membership, User
from lego.utils.test_utils import BaseAPITestCase


class EmailListTestCase(BaseAPITestCase):
    fixtures = [
        "test_abakus_groups.yaml",
        "test_users.yaml",
        "test_email_addresses.yaml",
        "test_email_lists.yaml",
    ]

    def setUp(self):
        self.url = "/api/v1/email-lists/"
        self.user = User.objects.get(username="test1")
        self.user2 = User.objects.get(username="test2")
        self.admin_group = AbakusGroup.objects.get(name="EmailAdminTest")
        self.admin_group.add_user(self.user)
        self.admin_group.add_user(self.user2, role="leader")

        self.client.force_authenticate(self.user)

    def test_list(self):
        """The list endpoint is available"""
        response = self.client.get(self.url)
        self.assertEqual(status.HTTP_200_OK, response.status_code)

    def test_create_list(self):
        """Create a new list with a new email"""
        response = self.client.post(
            self.url,
            {
                "name": "Jubileum",
                "email": "jubileum",
                "users": [3, 4],
                "groups": [self.admin_group.id],
                "groupRoles": ["member"],
                "additional_emails": [],
            },
        )
        self.assertEqual(status.HTTP_201_CREATED, response.status_code)

        email_list = EmailList.objects.get(email="jubileum")
        members = email_list.members()

        self.assertCountEqual(
            ["test1@user.com", "user@admin.com", "abakusgroup@admin.com"], members
        )

    def test_create_list_invalid_email(self):
        """Bad request when the user tries to create a list with an invalid email"""
        response = self.client.post(
            self.url,
            {
                "name": "Invalid",
                "email": "not valid email",
                "users": [1, 2],
                "groupRoles": ["member"],
            },
        )
        self.assertEqual(status.HTTP_400_BAD_REQUEST, response.status_code)

        response = self.client.post(
            self.url,
            {
                "name": "Invalid",
                "email": "admin",
                "users": [1, 2],
                "groupRoles": ["member"],
            },
        )
        self.assertEqual(status.HTTP_400_BAD_REQUEST, response.status_code)

    def test_create_list_duplicate_email(self):
        """No duplicate in members"""
        response = self.client.post(
            self.url,
            {
                "name": "Jubileum",
                "email": "jubileum",
                "users": [3, 4],
                "groups": [self.admin_group.id],
                "group_roles": ["member"],
                "additional_emails": ["additional@email.com", "additional@email.com"],
            },
        )
        self.assertEqual(status.HTTP_201_CREATED, response.status_code)

        email_list = EmailList.objects.get(email="jubileum")
        members = email_list.members()

        self.assertCountEqual(
            [
                "test1@user.com",
                "user@admin.com",
                "abakusgroup@admin.com",
                "additional@email.com",
            ],
            members,
        )

    def test_create_list_invalid_additional_email(self):
        """Bad request when user tries to create list with invalid additional email"""
        response = self.client.post(
            self.url,
            {
                "name": "Invalid",
                "email": "valid",
                "users": [1, 2],
                "group_roles": ["member"],
                "additional_emails": ["invalid"],
            },
        )
        self.assertEqual(status.HTTP_400_BAD_REQUEST, response.status_code)

    def test_create_list_no_recipients(self):
        """Bad request when user tries to create list with no recipients"""
        response = self.client.post(
            self.url,
            {
                "name": "Webkom",
                "email": "webbers",
                "users": [],
                "groups": [self.admin_group.id],
                "group_roles": ["recruiting"],
                "additional_emails": [],
            },
        )
        self.assertEqual(status.HTTP_400_BAD_REQUEST, response.status_code)

    def test_edit_additional_email(self):
        """Test ability to remove an additional email"""
        response = self.client.patch(
            f"{self.url}1/", {"additional_emails": ["test@test.no", "test2@test.no"]}
        )
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual(
            ["test@test.no", "test2@test.no"],
            EmailList.objects.get(id=1).additional_emails,
        )

        response = self.client.patch(
            f"{self.url}1/", {"additional_emails": ["test@test.no"]}
        )
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual(
            ["test@test.no"], EmailList.objects.get(id=1).additional_emails
        )

    def test_delete_additional_email(self):
        """Test ability to set additional emails to an empty array"""

        response = self.client.patch(
            f"{self.url}1/", {"additional_emails": [], "users": [1]}
        )
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual([], EmailList.objects.get(id=1).additional_emails)

    def test_change_assigned_email(self):
        """It is'nt possible to change the email after the list is created"""
        response = self.client.patch(f"{self.url}1/", {"email": "changed"})
        self.assertEqual(status.HTTP_200_OK, response.status_code)

        self.assertEqual("address", EmailList.objects.get(id=1).email_id)

    def test_edit_list_no_recipients(self):
        """Bad request when user tries to edit list with no recipients"""
        response = self.client.patch(
            f"{self.url}1/",
            {
                "users": [],
                "groups": [self.admin_group.id],
                "group_roles": ["recruiting"],
                "additional_emails": [],
            },
        )
        self.assertEqual(status.HTTP_400_BAD_REQUEST, response.status_code)

    def test_edit_list_no_recipients_partial(self):
        """Bad request when user tries to edit list with no recipients"""
        response = self.client.patch(
            f"{self.url}1/",
            {
                "additional_emails": [],
            },
        )
        self.assertEqual(status.HTTP_400_BAD_REQUEST, response.status_code)

    def test_delete_endpoint_not_available(self):
        """The delete endpoint isn't available."""
        response = self.client.delete(f"{self.url}1/")
        self.assertEqual(status.HTTP_403_FORBIDDEN, response.status_code)


class UserEmailTestCase(BaseAPITestCase):
    fixtures = [
        "test_abakus_groups.yaml",
        "test_email_addresses.yaml",
        "test_users.yaml",
        "test_email_lists.yaml",
    ]

    def setUp(self):
        self.url = "/api/v1/email-users/"
        self.user = User.objects.get(username="test1")
        self.user.internal_email_id = "test1"
        self.user.save()
        self.admin_group = AbakusGroup.objects.get(name="EmailAdminTest")
        self.admin_group.add_user(self.user)

        self.client.force_authenticate(self.user)

    def test_list(self):
        """The list endpoint is available"""
        response = self.client.get(self.url)
        self.assertEqual(status.HTTP_200_OK, response.status_code)

    def test_list_filter_groups(self):
        """The list endpoint can be filtered by group memberships"""
        webkom = AbakusGroup.objects.get(name="Webkom")
        webber = User.objects.create(
            username="Webber",
            email="webber",
            internal_email=EmailAddress.objects.create(email="webber"),
        )
        Membership.objects.create(abakus_group=webkom, user=webber)
        User.objects.create(
            username="Pleb",
            email="pleb",
            internal_email=EmailAddress.objects.create(email="pleb"),
        )
        response = self.client.get(self.url)
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual(3, len(response.json()["results"]))

        response = self.client.get(f"{self.url}?userGroups=Webkom")
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual(1, len(response.json()["results"]))

        response = self.client.get(f"{self.url}?userGroups=Webkom,EmailAdminTest")
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual(1, len(response.json()["results"]))

        response = self.client.get(f"{self.url}?userGroups=-")
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual(2, len(response.json()["results"]))

    def test_retrieve(self):
        """It is possible to retrieve the user"""
        response = self.client.get(f"{self.url}1/")
        self.assertEqual(status.HTTP_200_OK, response.status_code)

    def test_set_email(self):
        """It is possible to change from no email to one nobody has used"""
        response = self.client.patch(f"{self.url}2/", {"internalEmail": "testgroup"})
        self.assertEqual(status.HTTP_404_NOT_FOUND, response.status_code)

    def test_set_email_to_none(self):
        """It is not possible to set the email back to none"""
        User.objects.filter(id=1).update(internal_email="noassigned")

        response = self.client.patch(f"{self.url}1/", {"internalEmail": None})
        self.assertEqual(status.HTTP_400_BAD_REQUEST, response.status_code)

    def test_set_email_to_new(self):
        """
        It is not possible to change the email to a new one when you already gave an assigned email
        """
        User.objects.filter(id=1).update(internal_email="noassigned")

        response = self.client.patch(f"{self.url}1/", {"internalEmail": "unused"})
        self.assertEqual(status.HTTP_400_BAD_REQUEST, response.status_code)

    def test_set_email_to_an_assigned(self):
        """It is not possible to use an email used by another instance"""
        response = self.client.patch(f"{self.url}1/", {"internalEmail": "address"})
        self.assertEqual(status.HTTP_400_BAD_REQUEST, response.status_code)

    def test_set_address_on_new_user(self):
        """Set an address on a user that has no address assigned"""
        response = self.client.post(
            self.url,
            {"user": 2, "internalEmail": "test2", "internalEmailEnabled": True},
        )
        self.assertEqual(status.HTTP_201_CREATED, response.status_code)

    def test_set_address_on_capitalized_internal_email(self):
        """Set an address that is capitalized to make sure it is lowercased in input sanitation"""
        response = self.client.post(
            self.url,
            {"user": 2, "internalEmail": "TestEmail123", "internalEmailEnabled": True},
        )
        self.assertEqual(status.HTTP_201_CREATED, response.status_code)
        self.assertEqual("testemail123", response.json()["internalEmail"])
        self.assertEqual("testemail123", User.objects.get(pk=2).internal_email.email)

    def test_set_address_to_assigned(self):
        """Not possible to set an assigned email"""
        response = self.client.post(
            self.url,
            {"user": 2, "internalEmail": "address", "internalEmailEnabled": True},
        )
        self.assertEqual(status.HTTP_400_BAD_REQUEST, response.status_code)

    def test_set_address_on_user_with_address(self):
        """Not possible to post to a user that already have an address"""
        response = self.client.post(
            self.url,
            {"user": 1, "internalEmail": "unknown", "internalEmailEnabled": True},
        )
        self.assertEqual(status.HTTP_400_BAD_REQUEST, response.status_code)
