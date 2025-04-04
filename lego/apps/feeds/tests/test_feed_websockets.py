import json
from unittest import mock

from lego.apps.action_handlers.registry import get_handler
from lego.apps.comments.action_handlers import CommentHandler
from lego.apps.comments.models import Comment
from lego.apps.events.action_handlers import EventHandler
from lego.apps.events.models import Event
from lego.apps.feeds.models import NotificationFeed, UserFeed
from lego.apps.feeds.utils import add_to_feed
from lego.apps.meetings.action_handlers import MeetingInvitationHandler
from lego.apps.meetings.models import Meeting
from lego.apps.notifications.models import Announcement
from lego.apps.users.action_handlers import PenaltyHandler
from lego.apps.users.models import Penalty, User
from lego.utils.content_types import instance_to_string
from lego.utils.test_utils import BaseTestCase


class FeedWebsocketsTestCase(BaseTestCase):
    fixtures = [
        "test_abakus_groups.yaml",
        "test_users.yaml",
        "test_companies.yaml",
        "test_events.yaml",
    ]

    mock_channel_layer = mock.Mock()
    mock_group_send = mock.AsyncMock()
    mock_channel_layer.group_send = mock_group_send

    def setUp(self):
        self.user = User.objects.get(username="test1")
        self.other_user = User.objects.get(username="test2")

    def tearDown(self):
        # Reset the mock after each test
        self.mock_group_send.reset_mock()

    def check_notify_group_args(
        self,
        verb: str,
        actor: str,
        context_entities: set[str],
        extra_context: dict = None,
    ):
        self.mock_group_send.assert_called_once()
        # Get the first call arguments
        group, socket_data = self.mock_group_send.call_args[0]
        # Check the group name and data
        self.assertEqual(group, f"user-{self.user.pk}")
        self.assertEqual(socket_data["type"], "notification.message")
        data = json.loads(socket_data["text"])
        self.assertEqual(data["type"], "SOCKET_NEW_NOTIFICATION")
        payload = data["payload"]
        self.assertEqual(payload["verb"], verb)
        self.assertEqual(payload["activityCount"], 1)
        self.assertEqual(len(payload["activities"]), 1)
        activity = payload["activities"][0]
        self.assertEqual(activity["actor"], actor)
        self.assertEqual(activity["extraContext"], extra_context or {})
        context = payload["context"]
        self.assertEqual(set(context.keys()), context_entities)

    @mock.patch(
        "lego.apps.websockets.notifiers.get_channel_layer",
        return_value=mock_channel_layer,
    )
    def test_ignores_non_notifications(self, _):
        event = Event.objects.first()
        activity = EventHandler.get_activity(event)
        add_to_feed(activity, UserFeed, [self.user.pk])

        # Check that notify_group was not called
        self.mock_group_send.assert_not_called()

    @mock.patch(
        "lego.apps.websockets.notifiers.get_channel_layer",
        return_value=mock_channel_layer,
    )
    def test_comment_reply_notification(self, _):
        event = Event.objects.first()

        parent_comment = Comment.objects.create(
            text="Test parent comment",
            current_user=self.user,
            content_object=event,
        )
        comment = Comment.objects.create(
            text="Test comment",
            current_user=self.other_user,
            content_object=parent_comment.content_object,
            parent=parent_comment,
        )

        new_comment_activity = CommentHandler.get_activity(comment, reply=True)
        add_to_feed(new_comment_activity, NotificationFeed, [self.user.pk])

        self.check_notify_group_args(
            verb="comment_reply",
            actor=instance_to_string(self.other_user),
            extra_context={"content": "Test comment"},
            context_entities={
                instance_to_string(event),
                instance_to_string(self.other_user),
            },
        )

    @mock.patch(
        "lego.apps.websockets.notifiers.get_channel_layer",
        return_value=mock_channel_layer,
    )
    def test_meeting_invitation_notification(self, _):
        meeting = Meeting.objects.create(
            title="Test meeting",
            current_user=self.other_user,
            start_time="2023-10-01T12:00:00Z",
        )

        invitation, created = meeting.invite_user(
            user=self.user, created_by=self.other_user
        )
        activity = MeetingInvitationHandler.get_activity(invitation)
        add_to_feed(activity, NotificationFeed, [self.user.pk])

        self.check_notify_group_args(
            verb="meeting_invitation",
            actor=instance_to_string(self.other_user),
            context_entities={
                instance_to_string(invitation),
                instance_to_string(self.user),
                instance_to_string(self.other_user),
            },
        )

    @mock.patch(
        "lego.apps.websockets.notifiers.get_channel_layer",
        return_value=mock_channel_layer,
    )
    def test_penalty_notification(self, _):
        event = Event.objects.first()
        penalty = Penalty.objects.create(
            user=self.user,
            source_event=event,
            reason="Test penalty",
            weight=1,
        )
        activity = PenaltyHandler.get_activity(penalty)
        add_to_feed(activity, NotificationFeed, [self.user.pk])

        self.check_notify_group_args(
            verb="penalty",
            actor=instance_to_string(event),
            extra_context={"reason": "Test penalty", "weight": 1},
            context_entities={
                instance_to_string(event),
                instance_to_string(self.user),
            },
        )

    @mock.patch(
        "lego.apps.websockets.notifiers.get_channel_layer",
        return_value=mock_channel_layer,
    )
    def test_announcement_notification(self, _):
        announcement = Announcement.objects.create(
            message="Test announcement",
            current_user=self.other_user,
        )
        announcement.users.add(self.user)
        get_handler(Announcement).handle_send(announcement)

        self.check_notify_group_args(
            verb="announcement",
            actor=instance_to_string(self.other_user),
            context_entities={
                instance_to_string(announcement),
                instance_to_string(self.other_user),
            },
        )
