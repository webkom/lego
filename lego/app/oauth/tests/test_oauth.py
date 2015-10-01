import json

from django.core.urlresolvers import reverse
from django.test import TestCase

from lego.app.oauth.models import APIApplication


class TestWebappToken(TestCase):

    fixtures = ['initial_users.yaml', 'initial_applications.yaml']

    def test_get_token(self):

        self.api_app = APIApplication.objects.get(name='webapp')
        request_data = {
            'username': 'webkom',
            'password': 'webkom',
            'grant_type': 'password',
            'client_id': self.api_app.client_id
        }

        res = self.client.post(reverse('oauth2_provider:token'), data=request_data)

        content = json.loads(res.content.decode('utf-8'))

        self.assertTrue('access_token' in content)
        self.assertTrue('refresh_token' in content)
