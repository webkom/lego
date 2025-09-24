from django.db import models

from lego.apps.users.models import User
from lego.utils.models import BasisModel


class UserCommand(BasisModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="commands")
    command_id = models.CharField(max_length=100)
    pinned_position = models.PositiveIntegerField(null=True, blank=True)
    usage_count = models.PositiveIntegerField(default=0)
    last_used = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ("user", "command_id")
        ordering = ["pinned_position", "-usage_count"]

    def __str__(self):
        return f"{self.user} – {self.command_id} (pinned={self.pinned}, usage={self.usage_count})"

    def record_usage(self, count: int = 1):
        self.usage_count = models.F("usage_count") + count
        self.save(update_fields=["usage_count", "last_used"])

    def toggle_pin(self):
        self.pinned = not self.pinned
        self.save(update_fields=["pinned"])
