from lego.apps.achievements.constants import ACHIEVEMENT_FULLNAME_LOOKUP
from lego.apps.notifications.constants import ACHIEVEMENT_EARNED
from lego.apps.notifications.notification import Notification


class AchievementNotification(Notification):
    name = ACHIEVEMENT_EARNED

    def generate_push(self):
        achievement = self.kwargs["achievement"]

        return self._delay_push(
            template="achievements/push/new_achievement.txt",
            context={
                "achievement_title": ACHIEVEMENT_FULLNAME_LOOKUP[
                    achievement.identifier
                ][int(achievement.level)],
                "achievement_level": achievement.level+1,
            },
            instance=achievement,
        )
