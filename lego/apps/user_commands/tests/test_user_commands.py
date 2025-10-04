from django.urls import reverse
from rest_framework import status

from lego.apps.user_commands.models import UserCommand
from lego.apps.users.models import User
from lego.utils.test_utils import BaseAPITestCase


def get_record_usage_url():
    return reverse("api:v1:user-command-record-usage")


def get_suggestions_url():
    return reverse("api:v1:user-command-suggestions")


def create_user(username="testuser"):
    return User.objects.create(username=username, email=f"{username}@abakus.no")


class UserCommandSuggestionsTestCase(BaseAPITestCase):
    def setUp(self):
        self.user = create_user()
        self.client.force_authenticate(user=self.user)

    def test_initial_record_usage_creates_command(self):
        response = self.client.post(
            get_record_usage_url(), {"command_id": "home"}, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        cmd = UserCommand.objects.get(user=self.user, command_id="home")
        self.assertEqual(cmd.position, 0)
        self.assertEqual(cmd.command_id, "home")

    def test_fill_up_to_five_slots(self):
        for i in range(5):
            self.client.post(
                get_record_usage_url(),
                {"command_id": f"cmd{i}"},
                format="json",
            )

        cmds = UserCommand.objects.filter(user=self.user).order_by("position")
        self.assertEqual(cmds.count(), 5)
        self.assertEqual(
            [c.command_id for c in cmds], ["cmd0", "cmd1", "cmd2", "cmd3", "cmd4"]
        )

    def test_replaces_last_when_full(self):
        for i in range(5):
            self.client.post(
                get_record_usage_url(), {"command_id": f"cmd{i}"}, format="json"
            )

        # Use a new one, should replace last
        self.client.post(
            get_record_usage_url(), {"command_id": "new_cmd"}, format="json"
        )

        cmds = UserCommand.objects.filter(user=self.user).order_by("position")
        self.assertEqual(cmds.count(), 5)
        self.assertEqual(
            [c.command_id for c in cmds], ["cmd0", "cmd1", "cmd2", "cmd3", "new_cmd"]
        )

    def test_swap_up_on_reuse(self):
        for cid in ["a", "b", "c"]:
            self.client.post(get_record_usage_url(), {"command_id": cid}, format="json")

        # Use "c" again, should swap with "b"
        self.client.post(get_record_usage_url(), {"command_id": "c"}, format="json")

        cmds = UserCommand.objects.filter(user=self.user).order_by("position")
        self.assertEqual([c.command_id for c in cmds], ["a", "c", "b"])

    def test_suggestions_endpoint(self):
        for cid in ["one", "two", "three", "four", "five"]:
            self.client.post(get_record_usage_url(), {"command_id": cid}, format="json")

        response = self.client.get(get_suggestions_url())
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        data = response.json()
        visible_ids = [c["commandId"] for c in data["visible"]]
        buffer_ids = [c["commandId"] for c in data["buffer"]]

        # First 3 are visible, last 2 are buffer
        self.assertEqual(visible_ids, ["one", "two", "three"])
        self.assertEqual(buffer_ids, ["four", "five"])
        self.assertEqual(len(visible_ids), 3)
        self.assertEqual(len(buffer_ids), 2)
