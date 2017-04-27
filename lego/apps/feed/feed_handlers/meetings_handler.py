from lego.apps.feed.activities import Activity
from lego.apps.feed.feed_handlers.base_handler import BaseHandler
from lego.apps.feed.feed_manager import feed_manager
from lego.apps.feed.feeds.notification_feed import NotificationFeed
from lego.apps.feed.registry import register_handler
from lego.apps.feed.verbs import MeetingInvitationVerb
from lego.apps.meetings.models import MeetingInvitation
from lego.apps.meetings.notifications import MeetingInvitationNotification


class MeetingInvitationHandler(BaseHandler):
    model = MeetingInvitation
    manager = feed_manager

    def get_activity(self, meeting_invitation):
        return Activity(
            actor=meeting_invitation.created_by,
            verb=MeetingInvitationVerb,
            object=meeting_invitation,
            target=meeting_invitation.user,
            time=meeting_invitation.created_at
        )

    def handle_create(self, meeting_invitation):
        activity = self.get_activity(meeting_invitation)
        self.manager.add_activity(activity, [meeting_invitation.user.pk], [NotificationFeed])

        # Send notification
        notification = MeetingInvitationNotification(
            meeting_invitation.user, meeting_invitation=meeting_invitation
        )
        notification.notify()

    def handle_update(self, meeting_invitation):
        activity = self.get_activity(meeting_invitation)
        self.manager.add_activity(activity, [meeting_invitation.user.pk], [NotificationFeed])

    def handle_delete(self, meeting_invitation):
        activity = self.get_activity(meeting_invitation)
        self.manager.remove_activity(activity, [meeting_invitation.user.pk], [NotificationFeed])


register_handler(MeetingInvitationHandler)
