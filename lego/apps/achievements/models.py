from django.db import models

from lego.apps.users.models import User
from lego.utils.models import BasisModel

from .constants import ACHIEVEMENT_IDENTIFIERS


class Achievement(BasisModel):
    identifier = models.CharField(choices=ACHIEVEMENT_IDENTIFIERS, max_length=128)
    user = models.ForeignKey(
        User, related_name="achievements", on_delete=models.CASCADE
    )
    level = models.PositiveSmallIntegerField(default=0)

    @property
    def percentage(self):
        total_users = User.objects.count() or 1
        achievement_users = (
            Achievement.objects.filter(
                identifier=self.identifier, level__gte=self.level
            )
            .values("user")
            .distinct()
            .count()
        )
        return (achievement_users / total_users) * 100

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["user", "identifier"], name="unique_user_identifier"
            )
        ]
        indexes = [
            models.Index(fields=["user", "identifier", "level"]),
        ]
