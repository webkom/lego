import hashlib
import hmac
import json
import time

from django.conf import settings
from django.urls import reverse
from rest_framework import status

from lego.apps.achievements.constants import CHARITY_CASINO_2026_IDENTIFIER
from lego.apps.achievements.models import Achievement
from lego.apps.users.models import User
from lego.utils.test_utils import BaseAPITestCase


def _url():
    return reverse("api:v1:achievement-azart")


class AzartAchievementTestCase(BaseAPITestCase):
    fixtures = ["test_abakus_groups.yaml", "test_users.yaml"]

    def setUp(self):
        self.user = User.objects.get(username="test1")

    def _post(self, payload, timestamp=None, key=None):
        body = json.dumps(payload).encode()
        timestamp = str(int(time.time()) if timestamp is None else timestamp)
        signature = hmac.new(
            (key or settings.AZART_SECRET_KEY).encode(),
            timestamp.encode() + b"." + body,
            hashlib.sha256,
        ).hexdigest()
        return self.client.post(
            _url(),
            body,
            content_type="application/json",
            HTTP_X_AZART_TIMESTAMP=timestamp,
            HTTP_X_AZART_SIGNATURE=signature,
        )

    def _has_achievement(self):
        return Achievement.objects.filter(
            user=self.user, identifier=CHARITY_CASINO_2026_IDENTIFIER, level=0
        ).exists()

    def test_valid_signature_grants_once(self):
        self.assertEqual(
            self._post({"username": "test1"}).status_code, status.HTTP_201_CREATED
        )
        self.assertEqual(
            self._post({"username": "test1"}).status_code, status.HTTP_200_OK
        )
        self.assertEqual(
            Achievement.objects.filter(
                user=self.user, identifier=CHARITY_CASINO_2026_IDENTIFIER
            ).count(),
            1,
        )

    def test_wrong_key_rejected(self):
        response = self._post({"username": "test1"}, key="wrong")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertFalse(self._has_achievement())

    def test_stale_timestamp_rejected(self):
        response = self._post({"username": "test1"}, timestamp=int(time.time()) - 3600)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_malformed_timestamp_rejected(self):
        response = self._post({"username": "test1"}, timestamp="²")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_missing_signature_rejected(self):
        response = self.client.post(_url(), {"username": "test1"}, format="json")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_missing_username(self):
        response = self._post({})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_unknown_user(self):
        response = self._post({"username": "nobody"})
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
