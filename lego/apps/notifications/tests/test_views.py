from rest_framework import status
from rest_framework.test import APITestCase

from lego.apps.notifications import constants
from lego.apps.users.models import User


class NotificationSettingsViewSetTestCase(APITestCase):

    fixtures = ['test_abakus_groups.yaml', 'test_users.yaml', 'test_notification_settings.yaml']

    def setUp(self):
        self.url = '/api/v1/notification-settings/'
        self.user = User.objects.get(pk=2)

    def test_no_auth(self):
        response = self.client.get(self.url)
        self.assertEquals(response.status_code, status.HTTP_401_UNAUTHORIZED)

        response = self.client.post(self.url, {
            'notification_type': 'weekly_mail',
            'enabled': True,
            'channels': ['email']
        })
        self.assertEquals(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_list(self):
        self.client.force_login(self.user)

    def test_alternatives(self):
        self.client.force_login(self.user)
        response = self.client.get(f'{self.url}alternatives/')
        self.assertEquals(response.data, {
            'notification_types': constants.NOTIFICATION_TYPES,
            'channels': constants.CHANNELS
        })

    def test_change_setting(self):
        self.client.force_login(self.user)

        response = self.client.post(self.url, {
            'notification_type': 'weekly_mail',
            'enabled': True
        })
        self.assertEquals(response.data, {
            'notification_type': 'weekly_mail',
            'enabled': True,
            'channels': ['email', 'push']
        })

    def test_change_setting_defaults(self):
        """Make sure a new setting is created with correct defaults"""
        self.client.force_login(self.user)

        response = self.client.post(self.url, {
            'notification_type': constants.MEETING_INVITE,
        })

        self.assertEquals(response.data, {
            'notification_type': constants.MEETING_INVITE,
            'enabled': True,
            'channels': constants.CHANNELS
        })
