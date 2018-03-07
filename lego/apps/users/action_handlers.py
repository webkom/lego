from lego.apps.action_handlers.handler import Handler
from lego.apps.action_handlers.registry import register_handler
from lego.apps.feeds.activity import Activity
from lego.apps.feeds.feed_manager import feed_manager
from lego.apps.feeds.models import NotificationFeed, PersonalFeed, UserFeed
from lego.apps.feeds.verbs import GroupJoinVerb, PenaltyVerb
from lego.apps.users.constants import GROUP_COMMITTEE, GROUP_INTEREST
from lego.apps.users.models import Membership, Penalty
from lego.apps.users.notifications import PenaltyNotification


class MembershipHandler(Handler):
    model = Membership
    manager = feed_manager

    def handle_create(self, instance, **kwargs):
        group = instance.abakus_group
        if group.type not in (GROUP_COMMITTEE, GROUP_INTEREST):
            return

        activity = self.get_activity(instance)
        # Add activity to feed on the user profile site.
        self.manager.add_activity(activity, [instance.user_id], [UserFeed])
        # Add activity to followers timeline.
        followers = instance.user.followers\
            .exclude(follower_id=instance.user_id)\
            .values_list('follower_id', flat=True)

        self.manager.add_activity(activity, followers, [PersonalFeed])

    def get_activity(self, membership):
        return Activity(
            verb=GroupJoinVerb, actor=membership.user, target=membership.abakus_group,
            object=membership, time=membership.created_at, extra_context={}
        )


register_handler(MembershipHandler)


class PenaltyHandler(Handler):
    model = Penalty
    manager = feed_manager

    def get_activity(self, penalty):
        return Activity(
            actor=penalty.source_event, verb=PenaltyVerb, object=penalty, target=penalty.user,
            time=penalty.created_at, extra_context={
                'reason': penalty.reason,
                'weight': penalty.weight,
            }
        )

    def handle_create(self, instance, **kwargs):
        activity = self.get_activity(instance)
        self.manager.add_activity(activity, [instance.user.pk], [NotificationFeed])

        # Send Notification
        notification = PenaltyNotification(instance.user, penalty=instance)
        notification.notify()

    def handle_update(self, instance, **kwargs):
        activity = self.get_activity(instance)
        self.manager.add_activity(activity, [instance.user.pk], [NotificationFeed])

    def handle_delete(self, instance, **kwargs):
        activity = self.get_activity(instance)
        self.manager.remove_activity(activity, [instance.user.pk], [NotificationFeed])


register_handler(PenaltyHandler)
