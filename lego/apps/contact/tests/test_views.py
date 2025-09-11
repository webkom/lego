from unittest import mock

from rest_framework import status

from lego.apps.users.models import AbakusGroup, User
from lego.utils.test_utils import BaseAPITestCase


class ContactViewSetTestCase(BaseAPITestCase):
    fixtures = [
        "initial_files.yaml",
        "initial_abakus_groups.yaml",
        "development_users.yaml",
        "development_memberships.yaml",
    ]

    def setUp(self):
        self.url = "/api/v1/contact-form/"
        self.user = User.objects.first()

    @mock.patch("lego.apps.contact.views.send_message")
    @mock.patch("lego.apps.contact.serializers.verify_captcha", return_value=True)
    def test_without_auth(self, mock_verify_captcha, mock_send_message):
        response = self.client.post(
            self.url,
            {
                "title": "title",
                "message": "message",
                "captcha_response": "test",
                "recipient_group": None,
            },
        )
        self.assertEqual(status.HTTP_400_BAD_REQUEST, response.status_code)

    @mock.patch("lego.apps.contact.views.send_message")
    @mock.patch("lego.apps.contact.serializers.verify_captcha", return_value=True)
    def test_with_auth(self, mock_verify_captcha, mock_send_message):
        self.client.force_authenticate(self.user)
        response = self.client.post(
            self.url,
            {
                "title": "title",
                "message": "message",
                "captcha_response": "test",
                "recipient_group": None,
            },
        )
        self.assertEqual(status.HTTP_202_ACCEPTED, response.status_code)
        mock_verify_captcha.assert_called_once()
        mock_send_message.assert_called_once_with(
            "title", "message", self.user, None
        )

    @mock.patch("lego.apps.contact.views.send_message")
    @mock.patch("lego.apps.contact.serializers.verify_captcha", return_value=False)
    def test_with_auth_invalid_captcha(self, mock_verify_captcha, mock_send_message):
        self.client.force_authenticate(self.user)
        response = self.client.post(
            self.url,
            {
                "title": "title",
                "message": "message",
                "captcha_response": "test",
                "recipient_group": None,
            },
        )
        self.assertEqual(status.HTTP_400_BAD_REQUEST, response.status_code)
        mock_verify_captcha.assert_called_once()

    @mock.patch("lego.apps.contact.views.send_message")
    @mock.patch("lego.apps.contact.serializers.verify_captcha", return_value=True)
    def test_committee_as_recipient(self, mock_verify_captcha, mock_send_message):
        webkom = AbakusGroup.objects.get(name="Webkom")
        webkom_id = webkom.id

        self.client.force_authenticate(self.user)

        response = self.client.post(
            self.url,
            {
                "title": "title",
                "message": "message",
                "captcha_response": "test",
                "recipient_group": webkom_id,
            },
        )
        self.assertEqual(status.HTTP_202_ACCEPTED, response.status_code)
        mock_verify_captcha.assert_called_once()
        mock_send_message.assert_called_once_with(
            "title", "message", self.user, webkom
        )
