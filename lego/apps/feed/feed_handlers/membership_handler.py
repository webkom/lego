from lego.apps.feed.activities import Activity
from lego.apps.feed.feed_handlers import BaseHandler, PersonalFeed
from lego.apps.feed.feed_manager import feed_manager
from lego.apps.feed.feeds.user_feed import UserFeed
from lego.apps.feed.registry import register_handler
from lego.apps.feed.verbs import GroupJoinVerb
from lego.apps.users.constants import GROUP_COMMITTEE, GROUP_INTEREST
from lego.apps.users.models import Membership


class MembershipHandler(BaseHandler):
    model = Membership
    manager = feed_manager

    def handle_create(self, membership):
        group = membership.abakus_group
        if group.type not in (GROUP_COMMITTEE, GROUP_INTEREST):
            return

        activity = self.get_activity(membership)
        # Add activity to feed on the user profile site.
        self.manager.add_activity(activity, [membership.user_id], [UserFeed])
        # Add activity to followers timeline.
        followers = membership.user.followers\
            .exclude(follower_id=membership.user_id)\
            .values_list('follower_id', flat=True)

        self.manager.add_activity(activity, followers, [PersonalFeed])

    def handle_update(self, membership):
        pass

    def handle_delete(self, membership):
        pass

    def get_activity(self, membership):
        return Activity(
            verb=GroupJoinVerb,
            actor=membership.user,
            target=membership.abakus_group,
            object=membership,
            time=membership.created_at,
            extra_context={}
        )


register_handler(MembershipHandler)
