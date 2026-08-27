from django.test import TestCase

from lego.apps.feeds.activity import Activity
from lego.apps.feeds.models import PersonalFeed
from lego.apps.feeds.verbs import MeetingInvitationVerb
from lego.apps.meetings.models import Meeting
from lego.apps.users.models import User


class RemoveActivityTestCase(TestCase):
    fixtures = ["test_abakus_groups.yaml", "test_meetings.yaml", "test_users.yaml"]

    def _activity(self):
        meeting = Meeting.objects.get(id=1)
        user = User.objects.get(id=1)
        invitation, _ = meeting.invite_user(user)
        return Activity(
            actor=user,
            verb=MeetingInvitationVerb,
            object=invitation,
            target=invitation.user,
            time=invitation.created_at,
        )

    def test_removes_every_matching_entry(self):
        """add_activity does not deduplicate, so the store can hold the same one twice."""
        activity = self._activity()
        feed = PersonalFeed(feed_id="1", group="test")
        feed.add_activity(activity)
        feed.add_activity(activity)
        self.assertEqual(2, len(feed.activity_store))

        feed.remove_activity(activity)
        self.assertEqual([], feed.activity_store)
