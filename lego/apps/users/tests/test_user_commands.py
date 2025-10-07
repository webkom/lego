from django.urls import reverse
from rest_framework import status

from lego.apps.users.models import User
from lego.utils.test_utils import BaseAPITestCase


def get_record_usage_url():
    return reverse("api:v1:user-command-use")


def get_suggestions_url():
    return reverse("api:v1:user-command-suggestions")


def create_user(username="testuser"):
    return User.objects.create(username=username, email=f"{username}@abakus.no")


class UserCommandSuggestionsTestCase(BaseAPITestCase):
    def setUp(self):
        self.user = create_user()
        self.client.force_authenticate(user=self.user)

    def record(self, cmd_id: str):
        return self.client.post(
            get_record_usage_url(), {"command_id": cmd_id}, format="json"
        )

    def test_initial_record_usage_creates_command(self):
        self.record("home")
        self.user.refresh_from_db()
        self.assertEqual(self.user.command_suggestions, ["home"])

    def test_fill_up_to_five_slots(self):
        for cid in ["home", "profile", "events", "meetings", "lending"]:
            self.record(cid)
        self.user.refresh_from_db()
        self.assertEqual(len(self.user.command_suggestions), 5)
        self.assertEqual(
            self.user.command_suggestions,
            ["home", "profile", "events", "meetings", "lending"],
        )

    def test_replaces_last_when_full(self):
        for cid in ["home", "profile", "events", "meetings", "lending"]:
            self.record(cid)
        self.record("quotes")
        self.user.refresh_from_db()
        self.assertEqual(
            self.user.command_suggestions,
            ["home", "profile", "events", "meetings", "quotes"],
        )

    def test_swap_up_on_reuse(self):
        for cid in ["home", "profile", "events"]:
            self.record(cid)
        self.record("events")  # reuse last
        self.user.refresh_from_db()
        self.assertEqual(self.user.command_suggestions, ["home", "events", "profile"])   

    def test_repeated_command_bubbles_to_front(self):
        for cid in ["home", "profile", "events"]:
            self.record(cid)
        self.record("events")
        self.record("events")
        self.user.refresh_from_db()
        self.assertEqual(self.user.command_suggestions[0], "events")

    def test_command_from_buffer_moves_into_visible(self):
        for cid in ["home", "profile", "events", "meetings", "lending"]:
            self.record(cid)
        self.record("meetings")
        self.user.refresh_from_db()
        self.assertIn("meetings", self.user.command_suggestions[:3])

    def test_command_not_in_list_appends_to_end(self):
        for cid in ["home", "profile", "events", "meetings", "lending"]:
            self.record(cid)
        self.record("quotes")
        self.user.refresh_from_db()
        self.assertEqual(self.user.command_suggestions[-1], "quotes")
        self.assertNotIn("lending", self.user.command_suggestions)

    def test_command_already_first_stays_first(self):
        for cid in ["home", "profile", "events"]:
            self.record(cid)
        self.record("home")
        self.user.refresh_from_db()
        self.assertEqual(self.user.command_suggestions[0], "home")

    def test_buffer_to_front_chain(self):
        for cid in ["home", "profile", "events", "meetings", "lending"]:
            self.record(cid)
        self.record("lending")
        self.user.refresh_from_db()
        self.assertIn("lending", self.user.command_suggestions[:4])

    def test_missing_command_id_returns_400(self):
        response = self.client.post(get_record_usage_url(), {}, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        data = response.json()
        self.assertIn("error", data)
        self.assertIn("Missing", data["error"])

    def test_valid_command_succeeds(self):
        response = self.record("home")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.user.refresh_from_db()
        self.assertIn("home", self.user.command_suggestions)
