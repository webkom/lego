import datetime
from unittest import mock

from lego.utils.test_utils import BaseAPITestCase, fake_time
from lego.apps.users.models import User
from django.urls import reverse
from datetime import datetime


class UserChristmasSlotsTestCase(BaseAPITestCase):
    fixtures = ["test_users.yaml"]

    def setUp(self):
        self.user = User.objects.get(id=1)
        self.client.force_authenticate(self.user)
        self.url = reverse("api:v1:user-detail", kwargs={"username": self.user.username})
        
    def test_initial_christmas_slots(self):
        response = self.client.get(reverse("api:v1:user-me"))
        self.assertEqual(response.json()["christmasSlots"], [])
        self.assertEqual(self.user.christmas_slots, [])

    @mock.patch("django.utils.timezone.now", return_value=fake_time(2026, 12, 10))
    def test_valid_christmas_slots(self, mock_now):
        valid_christmas_slots = [1, 2, 3, 6, 7]
        response = self.client.patch(self.url, {"christmasSlots": valid_christmas_slots}, format="json")
        
        self.user.refresh_from_db()
        self.assertEqual([int(mock_now.return_value.timestamp() * 100) + s for s in valid_christmas_slots], self.user.christmas_slots)
        self.assertEqual(response.json()["christmasSlots"], valid_christmas_slots)

    def test_invalid_christmas_slots(self):
        invalid_christmas_slots1 = [0, 6, 7]
        invalid_christmas_slots2 = [6, 7, 25]

        response1 = self.client.patch(self.url, {"christmasSlots": invalid_christmas_slots1}, format="json")
        response2 = self.client.patch(self.url, {"christmasSlots": invalid_christmas_slots2}, format="json")

        self.assertEqual(response1.status_code, 400)
        self.assertEqual(response2.status_code, 400)

    @mock.patch("django.utils.timezone.now", return_value=fake_time(2027, 1, 1))
    def test_submit_after_deadline(self, mock_now):
        valid_christmas_slots = [6, 7]
        response = self.client.patch(self.url, {"christmasSlots": valid_christmas_slots})
        
        self.assertEqual(response.status_code, 400)
