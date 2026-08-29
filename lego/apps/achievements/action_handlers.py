from lego.apps.achievements.models import Achievement
from lego.apps.action_handlers.handler import Handler
from lego.apps.action_handlers.registry import register_handler
from lego.apps.feeds.activity import Activity
from lego.apps.feeds.feed_manager import feed_manager
from lego.apps.feeds.models import NotificationFeed, PersonalFeed, UserFeed
from lego.apps.feeds.verbs import TrophyVerb


class AchievementHandler(Handler):
    """
    Achievements only get an onsite feed notification (no email/push) - the
    identifier and level are passed along so the frontend can resolve the
    trophy's name and rarity title itself.
    """

    model = Achievement
    manager = feed_manager

    @staticmethod
    def get_activity(achievement):
        return Activity(
            actor=achievement.user,
            verb=TrophyVerb,
            object=achievement,
            time=achievement.created_at,
            extra_context={
                "identifier": achievement.identifier,
                "level": achievement.level,
            },
        )

    def notify(self, instance, **kwargs):
        activity = self.get_activity(instance)
        user = instance.user

        # Bell notification and own profile feed for the achiever themself.
        self.manager.add_activity(activity, [user.pk], [NotificationFeed, UserFeed])

        # Followers' timeline.
        followers = user.followers.exclude(follower_id=user.pk).values_list(
            "follower_id", flat=True
        )
        self.manager.add_activity(activity, followers, [PersonalFeed])

    handle_create = notify
    handle_update = notify


register_handler(AchievementHandler)
