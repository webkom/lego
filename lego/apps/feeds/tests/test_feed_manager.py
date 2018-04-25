from django.test import TransactionTestCase

from lego.apps.feeds.activity import Activity
from lego.apps.feeds.feed_manager import feed_manager
from lego.apps.feeds.models import NotificationFeed
from lego.apps.feeds.verbs import MeetingInvitationVerb
from lego.apps.meetings.models import Meeting
from lego.apps.users.models import User


class FeedManagerTestCase(TransactionTestCase):

    fixtures = ['test_abakus_groups.yaml', 'test_meetings.yaml', 'test_users.yaml']

    def setUp(self):
        self.manager = feed_manager

    def test_meeting_invitation_activity(self):
        meeting = Meeting.objects.get(id=1)
        user = User.objects.get(id=1)
        meeting_invitation, _ = meeting.invite_user(user)

        activity = Activity(
            actor=user, verb=MeetingInvitationVerb, object=meeting_invitation,
            target=meeting_invitation.user, time=meeting_invitation.created_at
        )
        self.manager.add_activity(activity, [user.id], [NotificationFeed])
        self.assertEqual(1, NotificationFeed.objects.count())

        self.manager.remove_activity(activity, [], [NotificationFeed])
        self.assertEqual(0, NotificationFeed.objects.count())
