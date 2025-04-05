from unittest import mock

from lego.apps.comments.action_handlers import CommentHandler
from lego.apps.comments.models import Comment
from lego.apps.events.action_handlers import EventHandler
from lego.apps.events.models import Event
from lego.apps.feeds.models import NotificationFeed, UserFeed
from lego.apps.feeds.utils import add_to_feed
from lego.apps.meetings.action_handlers import MeetingInvitationHandler
from lego.apps.meetings.models import Meeting
from lego.apps.users.models import User
from lego.utils.content_types import instance_to_string
from lego.utils.test_utils import BaseTestCase


class FeedWebsocketsTestCase(BaseTestCase):
    fixtures = [
        "test_abakus_groups.yaml",
        "test_users.yaml",
        "test_companies.yaml",
        "test_events.yaml",
    ]

    def setUp(self):
        self.user = User.objects.get(username="test1")
        self.other_user = User.objects.get(username="test2")

    def check_notify_group_args(
        self,
        args,
        verb: str,
        actor: str,
        context_entities: set[str],
        extra_context: dict = {},
    ):
        [group, data] = args
        # Check if the first argument is the expected group
        self.assertEqual(group, f"user-{self.user.pk}")
        self.assertEqual(data["type"], "SOCKET_NEW_NOTIFICATION")
        payload = data["payload"]
        print(payload)
        self.assertEqual(payload["verb"], verb)
        self.assertEqual(payload["activity_count"], 1)
        self.assertEqual(len(payload["activities"]), 1)
        activity = payload["activities"][0]
        self.assertEqual(activity["actor"], actor)
        self.assertEqual(activity["extra_context"], extra_context)
        context = payload["context"]
        self.assertEqual(set(context.keys()), context_entities)

    @mock.patch("lego.apps.feeds.websockets.notify_group")
    def test_ignores_non_notifications(self, mock_notify_group):
        event = Event.objects.first()
        activity = EventHandler.get_activity(event)
        add_to_feed(activity, UserFeed, [self.user.pk])

        # Check that notify_group was not called
        mock_notify_group.assert_not_called()

    @mock.patch("lego.apps.feeds.websockets.notify_group")
    def test_comment_reply_notification(self, mock_notify_group):
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

        mock_notify_group.assert_called_once()
        # Get the first call arguments
        self.check_notify_group_args(
            mock_notify_group.call_args[0],
            verb="comment_reply",
            actor=instance_to_string(self.other_user),
            extra_context={"content": "Test comment"},
            context_entities={
                instance_to_string(event),
                instance_to_string(self.other_user),
            },
        )

    @mock.patch("lego.apps.feeds.websockets.notify_group")
    def test_meeting_invitation_notification(self, mock_notify_group):
        meeting = Meeting.objects.create(
            title="Test meeting",
            current_user=self.other_user,
            start_time="2023-10-01T12:00:00Z",
            users=[User.objects.get(username="test1")],
        )

        invitation, created = meeting.invite_user(
            user=self.user, created_by=self.other_user
        )
        activity = MeetingInvitationHandler.get_activity(invitation)
        add_to_feed(activity, NotificationFeed, [self.user.pk])

        mock_notify_group.assert_called_once()
        # Get the first call arguments
        self.check_notify_group_args(
            mock_notify_group.call_args[0],
            verb="meeting_invitation",
            actor=instance_to_string(self.other_user),
            context_entities={
                instance_to_string(invitation),
                instance_to_string(self.user),
                instance_to_string(self.other_user),
            },
        )
