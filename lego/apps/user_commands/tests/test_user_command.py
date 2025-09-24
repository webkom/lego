from django.urls import reverse
from rest_framework import status

from lego.apps.user_commands.models import UserCommand
from lego.apps.users.models import User
from lego.utils.test_utils import BaseAPITestCase


def get_list_url():
    return reverse("api:user-command-list")


def get_set_pins_url():
    return reverse("api:user-command-set-pins")


def get_suggestions_url():
    return reverse("api:user-command-suggestions")


def create_user(username="testuser"):
    return User.objects.create(username=username, email=f"{username}@abakus.no")


class UserCommandPinsTestCase(BaseAPITestCase):
    def setUp(self):
        self.user = create_user()
        self.client.force_authenticate(user=self.user)

    def test_set_pins_initial(self):
        payload = {"pins": ["cmd1", "cmd2", "cmd3"]}
        response = self.client.post(get_set_pins_url(), payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        cmds = UserCommand.objects.filter(user=self.user).order_by("pinned_position")
        self.assertEqual([c.command_id for c in cmds], ["cmd1", "cmd2", "cmd3"])
        self.assertEqual([c.pinned_position for c in cmds], [1, 2, 3])

    def test_set_pins_unpin(self):
        # First pin 3 commands
        self.client.post(
            get_set_pins_url(), {"pins": ["cmd1", "cmd2", "cmd3"]}, format="json"
        )

        # Unpin cmd2 (send only cmd1 and cmd3)
        self.client.post(get_set_pins_url(), {"pins": ["cmd1", "cmd3"]}, format="json")

        cmds = UserCommand.objects.filter(user=self.user).order_by("command_id")
        self.assertEqual(cmds.get(command_id="cmd2").pinned_position, None)
        self.assertEqual(cmds.get(command_id="cmd1").pinned_position, 1)
        self.assertEqual(cmds.get(command_id="cmd3").pinned_position, 2)

    def test_set_pins_max_limit(self):
        payload = {"pins": ["c1", "c2", "c3", "c4", "c5", "c6"]}  # 6 commands
        response = self.client.post(get_set_pins_url(), payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("You can pin at most 5 commands", str(response.data))

    def test_reorder_pins(self):
        self.client.post(
            get_set_pins_url(), {"pins": ["cmd1", "cmd2", "cmd3"]}, format="json"
        )
        # Move cmd3 to the front
        self.client.post(
            get_set_pins_url(), {"pins": ["cmd3", "cmd1", "cmd2"]}, format="json"
        )

        cmds = UserCommand.objects.filter(user=self.user).order_by("pinned_position")
        self.assertEqual([c.command_id for c in cmds], ["cmd3", "cmd1", "cmd2"])

    def test_suggestions_endpoint(self):
        # Create usage counts manually
        for i in range(1, 6):
            UserCommand.objects.create(
                user=self.user, command_id=f"cmd{i}", usage_count=i
            )

        # Pin cmd1 and cmd2
        self.client.post(get_set_pins_url(), {"pins": ["cmd1", "cmd2"]}, format="json")

        response = self.client.get(get_suggestions_url())
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        data = response.json()
        pinned_ids = [c["command_id"] for c in data["pinned"]]
        suggested_ids = [c["command_id"] for c in data["suggested"]]

        self.assertEqual(pinned_ids, ["cmd1", "cmd2"])  # in pin order
        self.assertTrue(all(c not in pinned_ids for c in suggested_ids))  # no overlap
        self.assertEqual(len(suggested_ids), 3)
        # Highest usage_count (cmd5) should be first
        self.assertEqual(suggested_ids[0], "cmd5")
