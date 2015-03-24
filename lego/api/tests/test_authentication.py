# -*- coding: utf8 -*-
from rest_framework.reverse import reverse
from rest_framework.test import APITestCase

from lego.users.models import User


class JSONWebTokenTestCase(APITestCase):
    fixtures = ['initial_users']

    def setUp(self):
        self.user = User.objects.get(pk=1)
        self.user_data = {
            'username': self.user.username,
            'password': 'webkom'
        }

    def test_authenticate(self):
        response = self.client.post(reverse('obtain_jwt_token'), self.user_data)
        self.assertContains(response, 'token')

    def test_refresh(self):
        token_response = self.client.post(reverse('obtain_jwt_token'), self.user_data)
        token_data = {
            'token': token_response.data['token']
        }
        refresh_response = self.client.post(reverse('refresh_jwt_token'), token_data)
        self.assertContains(refresh_response, 'token')
