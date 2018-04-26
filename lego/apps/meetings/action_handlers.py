from lego.apps.action_handlers.handler import Handler
from lego.apps.action_handlers.registry import register_handler
from lego.apps.feeds.activity import Activity
from lego.apps.feeds.feed_manager import feed_manager
from lego.apps.feeds.models import NotificationFeed
from lego.apps.feeds.verbs import MeetingInvitationVerb
from lego.apps.meetings.models import MeetingInvitation
from lego.apps.meetings.notifications import MeetingInvitationNotification


class MeetingInvitationHandler(Handler):

    model = MeetingInvitation
    manager = feed_manager

    def get_activity(self, meeting_invitation):
        return Activity(
            actor=meeting_invitation.created_by, verb=MeetingInvitationVerb,
            object=meeting_invitation, target=meeting_invitation.user,
            time=meeting_invitation.created_at
        )

    def handle_create(self, instance, **kwargs):
        activity = self.get_activity(instance)
        self.manager.add_activity(activity, [instance.user.pk], [NotificationFeed])

        # Send notification
        notification = MeetingInvitationNotification(instance.user, meeting_invitation=instance)
        notification.notify()

    def handle_update(self, instance, **kwargs):
        activity = self.get_activity(instance)
        self.manager.add_activity(activity, [instance.user.pk], [NotificationFeed])

    def handle_delete(self, instance, **kwargs):
        activity = self.get_activity(instance)
        self.manager.remove_activity(activity, [instance.user.pk], [NotificationFeed])


register_handler(MeetingInvitationHandler)
