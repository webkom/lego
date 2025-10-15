from unittest.mock import AsyncMock, MagicMock

from lego.apps.comments.models import Comment
from lego.apps.meetings.models import Meeting
from lego.apps.users.models import User
from lego.apps.websockets import constants
from lego.apps.websockets.consumers import GroupConsumer
from lego.apps.websockets.groups import group_for_content_model, group_for_user
from lego.utils.test_utils import BaseTestCase


def create_user(username="testuser", **kwargs):
    return User.objects.create(
        username=username, email=username + "@abakus.no", **kwargs
    )


class MockConsumer(GroupConsumer):

    def __init__(self, user):
        super().__init__(user)
        self.scope = {"user": user}
        self.channel_name = "channel-123"
        self.channel_layer = MagicMock()
        self.channel_layer.group_add = AsyncMock()
        self.channel_layer.group_discard = AsyncMock()
        self.accept = MagicMock()
        self.close = MagicMock()
        self.send_json = MagicMock()

    def recieve_group_join(self, group):
        content = {
            "type": constants.WS_GROUP_JOIN_BEGIN,
            "payload": {"group": group},
        }
        self.receive_json(content)

    def recieve_group_leave(self, group):
        content = {
            "type": constants.WS_GROUP_LEAVE_BEGIN,
            "payload": {"group": group},
        }
        self.receive_json(content)


def get_restricted_groups(user):

    def comment_group():
        meeting = Meeting.objects.get(id=1)
        meeting.invite_user(user)
        comment = Comment.objects.create(text="test", content_object=meeting)
        return group_for_content_model(comment)

    return [comment_group()]


class WebsocketGroupTests(BaseTestCase):

    fixtures = ["test_users.yaml", "test_meetings.yaml"]

    def setUp(self):
        self.user = User.objects.get(username="abakommer")
        self.consumer = MockConsumer(self.user)

        # Should test all group types that can be restricted
        # and is being validatet using lego.apps.websockets.groups.verify_group_access
        self.restricted_groups = get_restricted_groups(self.user)

    def test_initial_groups(self):
        """User should have certain groups initially"""
        initial_groups = set(["global", group_for_user(self.user.pk)])

        self.assertEquals(len(self.consumer.user_groups), 0)
        self.consumer.connect()
        self.assertEqual(self.consumer.user_groups & initial_groups, initial_groups)

    def test_join_group(self):
        """User should be able to join a group"""
        self.consumer.connect()

        for group in self.restricted_groups:
            self.assertNotIn(group, self.consumer.user_groups)
            self.consumer.recieve_group_join(group)
            self.assertIn(group, self.consumer.user_groups)

    def test_leave_group(self):
        """User should be able to leave a group they have joined"""
        self.consumer.connect()

        for group in self.restricted_groups:
            self.assertNotIn(group, self.consumer.user_groups)
            self.consumer.recieve_group_join(group)
            self.consumer.recieve_group_leave(group)
            self.assertNotIn(group, self.consumer.user_groups)

    def test_join_group_without_permissions(self):
        """User should not be able to join a group they do not have permission to join"""
        uninvited_user = User.objects.get(username="abakule")
        consumer = MockConsumer(uninvited_user)
        consumer.connect()

        for group in self.restricted_groups:
            self.assertNotIn(group, consumer.user_groups)
            consumer.recieve_group_join(group)
            self.assertNotIn(group, consumer.user_groups)
