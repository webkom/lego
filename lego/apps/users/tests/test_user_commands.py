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
        for i in range(1, 6):
            self.record(f"cmd{i}")
        self.user.refresh_from_db()
        self.assertEqual(len(self.user.command_suggestions), 5)
        self.assertEqual(
            self.user.command_suggestions, ["cmd1", "cmd2", "cmd3", "cmd4", "cmd5"]
        )

    def test_replaces_last_when_full(self):
        for i in range(1, 6):
            self.record(f"cmd{i}")
        self.record("newcmd")
        self.user.refresh_from_db()
        self.assertEqual(
            self.user.command_suggestions, ["cmd1", "cmd2", "cmd3", "cmd4", "newcmd"]
        )

    def test_swap_up_on_reuse(self):
        for cid in ["cmd1", "cmd2", "cmd3"]:
            self.record(cid)
        self.record("cmd3")  # reuse last
        self.user.refresh_from_db()
        self.assertEqual(self.user.command_suggestions, ["cmd1", "cmd3", "cmd2"])

    def test_suggestions_endpoint(self):
        for cid in ["a", "b", "c", "d", "e"]:
            self.record(cid)
        response = self.client.get(get_suggestions_url())
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        data = response.json()
        visible_ids = data["visible"]
        buffer_ids = data["buffer"]

        self.assertEqual(visible_ids, ["a", "b", "c"])
        self.assertEqual(buffer_ids, ["d", "e"])

    def test_repeated_command_bubbles_to_front(self):
        for cid in ["cmd1", "cmd2", "cmd3"]:
            self.record(cid)
        # reuse cmd3 multiple times
        self.record("cmd3")
        self.record("cmd3")
        self.user.refresh_from_db()
        self.assertEqual(self.user.command_suggestions[0], "cmd3")

    def test_command_from_buffer_moves_into_visible(self):
        # Fill 5 slots
        for cid in ["a", "b", "c", "d", "e"]:
            self.record(cid)
        self.record("d")
        self.user.refresh_from_db()
        self.assertIn("d", self.user.command_suggestions[:3])

    def test_command_not_in_list_appends_to_end(self):
        for cid in ["a", "b", "c", "d", "e"]:
            self.record(cid)
        self.record("z")
        self.user.refresh_from_db()
        self.assertEqual(self.user.command_suggestions[-1], "z")
        self.assertNotIn("e", self.user.command_suggestions)

    def test_command_already_first_stays_first(self):
        for cid in ["x", "y", "z"]:
            self.record(cid)
        self.record("x")
        self.user.refresh_from_db()
        self.assertEqual(self.user.command_suggestions[0], "x")

    def test_buffer_to_front_chain(self):
        for cid in ["a", "b", "c", "d", "e"]:
            self.record(cid)
        # reuse "e" - should climb gradually towards front
        self.record("e")
        self.user.refresh_from_db()
        self.assertIn("e", self.user.command_suggestions[:4])  # no longer last
