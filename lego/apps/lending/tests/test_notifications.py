from unittest.mock import patch

from django.urls import reverse
from django.utils.timezone import now, timedelta

from lego.apps.lending.models import LendableObject, LendingRequest
from lego.apps.lending.notifications import LendingRequestNotification
from lego.apps.users.models import AbakusGroup, User
from lego.utils.test_utils import BaseAPITestCase


def get_lending_request_list_url():
    return reverse("api:v1:lending-request-list")


def create_user(username="testuser", **kwargs):
    return User.objects.create(
        username=username, email=f"{username}@abakus.no", **kwargs
    )


def create_lendable_object(**kwargs):
    return LendableObject.objects.create(
        title="Test Object", description="This is a test object", **kwargs
    )


@patch("lego.utils.email.django_send_mail")
class LendingRequestNotificationTestCase(BaseAPITestCase):

    def setUp(self):

        self.lendee = create_user("lendee")
        self.lender = create_user("lender")

        self.view_group = AbakusGroup.objects.create(name="view_group")
        self.edit_group = AbakusGroup.objects.create(name="edit_group")

        self.view_group.add_user(self.lendee)
        self.edit_group.add_user(self.lender)
        self.view_group.add_user(self.lender)

        self.lendable_object = LendableObject.objects.create(
            title="Test Object", description="This is a test object"
        )

        self.lendable_object.can_view_groups.add(self.view_group)
        self.lendable_object.can_edit_groups.add(self.edit_group)

        # Create LendingRequest instance
        self.client.force_authenticate(user=self.lendee)
        data = {
            "" "lendable_object": self.lendable_object.pk,
            "status": "unapproved",
            "start_date": (now() + timedelta(days=1)).isoformat(),
            "end_date": (now() + timedelta(days=2)).isoformat(),
        }

        self.client.post(get_lending_request_list_url(), data)

        # Create notifier
        self.notifier = LendingRequestNotification(
            self.lendee,
            lending_request=LendingRequest.objects.get(
                lendable_object__title="Test Object"
            ),
            lender=self.lender,
        )

    def assertEmailContains(self, send_mail_mock, content):
        self.notifier.generate_mail()
        email_args = send_mail_mock.call_args[1]
        self.assertIn(content, email_args["html_message"])

    def test_generate_email_comment(self, send_mail_mock):
        self.assertEmailContains(send_mail_mock, "Ny forespørsel om utlån")
