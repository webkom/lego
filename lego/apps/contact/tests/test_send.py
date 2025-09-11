from unittest import mock

from django.contrib.auth.models import AnonymousUser

from lego.apps.contact.send import send_message
from lego.apps.users.constants import LEADER, MEMBER
from lego.apps.users.models import AbakusGroup, User
from lego.utils.test_utils import BaseTestCase

default_values = {
    "from_email": None,
    "html_template": "contact/email/contact_form.html",
    "plain_template": "contact/email/contact_form.txt",
}


class SendTestCase(BaseTestCase):
    fixtures = [
        "initial_files.yaml",
        "initial_abakus_groups.yaml",
        "development_users.yaml",
        "development_memberships.yaml",
    ]

    def setUp(self):
        self.webkom_group = AbakusGroup.objects.get(name="Webkom")

        membership = self.webkom_group.memberships.first()
        membership.role = LEADER
        membership.save()

        self.webkom_leader = membership.user

    @mock.patch("lego.apps.contact.send.send_email.delay")
    def test_send_user(self, mock_send_email):
        """
        Send in a contact form as logged in user, showing name
        """
        logged_in_user = User.objects.first()

        send_message("title", "message", logged_in_user, self.webkom_group)
        mock_send_email.assert_called_with(
            to_email=[self.webkom_leader.email_address],
            context={
                "title": "title",
                "message": "message",
                "from_name": logged_in_user.full_name,
                "from_email": logged_in_user.email_address,
                "recipient_group": self.webkom_group.__str__(),
            },
            subject=f"Ny henvendelse fra kontaktskjemaet til {self.webkom_group.__str__()}",
            **default_values,
        )
        mock_send_email.assert_called_once()

    @mock.patch("lego.apps.contact.send.send_email.delay")
    def test_send_anonymous(self, mock_send_email):
        """
        Ensure anonymous users can not send messages
        """
        anonymus_user = AnonymousUser()
        
        with self.assertRaises(ValueError):
            send_message("title", "message", anonymus_user, self.webkom_group)
        mock_send_email.assert_not_called()

    @mock.patch("lego.apps.contact.send.send_email.delay")
    def test_send_to_hs(self, mock_send_email):
        """
        Send in a contact form to HS by passing `None` as recipient
        """
        logged_in_user = User.objects.first()
        hs_group = AbakusGroup.objects.get(name="Hovedstyret")

        send_message("title", "message", logged_in_user, None)
        mock_send_email.assert_called_with(
            to_email=["hs@abakus.no"],
            context={
                "title": "title",
                "message": "message",
                "from_name": logged_in_user.full_name,
                "from_email": logged_in_user.email_address,
                "recipient_group": hs_group.__str__(),
            },
            subject=f"Ny henvendelse fra kontaktskjemaet til {hs_group.__str__()}",
            **default_values,
        )
        mock_send_email.assert_called_once()

    @mock.patch("lego.apps.contact.send.send_email.delay")
    def test_send_to_group_with_several_leaders(self, mock_send_email):
        """
        Test that all leaders receive the form.
        """
        logged_in_user = User.objects.first()

        self.webkom_group.add_user(logged_in_user, role=LEADER)

        send_message("title", "message", logged_in_user, self.webkom_group)
        mock_send_email.assert_called_with(
            to_email=[self.webkom_leader.email_address, logged_in_user.email_address],
            context={
                "title": "title",
                "message": "message",
                "from_name": logged_in_user.full_name,
                "from_email": logged_in_user.email_address,
                "recipient_group": self.webkom_group.__str__(),
            },
            subject=f"Ny henvendelse fra kontaktskjemaet til {self.webkom_group.__str__()}",
            **default_values,
        )
        mock_send_email.assert_called_once()

    @mock.patch("lego.apps.contact.send.send_email.delay")
    def test_is_only_sent_to_leader(self, mock_send_email):
        """
        Test that form is only sent to leader, not other members.
        """
        logged_in_user = User.objects.first()

        self.webkom_group.add_user(logged_in_user, role=MEMBER)

        send_message("title", "message", logged_in_user, self.webkom_group)
        mock_send_email.assert_called_with(
            to_email=[self.webkom_leader.email_address],
            context={
                "title": "title",
                "message": "message",
                "from_name": logged_in_user.full_name,
                "from_email": logged_in_user.email_address,
                "recipient_group": self.webkom_group.__str__(),
            },
            subject=f"Ny henvendelse fra kontaktskjemaet til {self.webkom_group.__str__()}",
            **default_values,
        )
        mock_send_email.assert_called_once()
