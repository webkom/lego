from django.db import models, transaction
from django.utils import timezone

from lego.apps.users.models import User
from lego.utils.models import BasisModel


class UserCommandManager(models.Manager):
    @transaction.atomic
    def record_usage(self, user: User, command_id: str):
        commands = list(self.filter(user=user).order_by("position"))
        positions = {c.command_id: c for c in commands}

        if command_id in positions:
            cmd = positions[command_id]
            if cmd.position > 0:
                prev = next(
                    (c for c in commands if c.position == cmd.position - 1), None
                )
                if prev:
                    prev.position, cmd.position = cmd.position, prev.position
                    prev.save(update_fields=["position"])
                cmd.position -= 1
            cmd.last_used = timezone.now()
            cmd.save(update_fields=["position", "last_used"])
            return cmd

        if len(commands) < 5:
            new_pos = len(commands)
            return self.create(user=user, command_id=command_id, position=new_pos)

        last = commands[-1]
        last.command_id = command_id
        last.last_used = timezone.now()
        last.save(update_fields=["command_id", "last_used"])
        return last


class UserCommand(BasisModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="commands")
    command_id = models.CharField(max_length=100)
    position = models.PositiveIntegerField(default=0)
    last_used = models.DateTimeField(auto_now=True)

    objects = UserCommandManager()

    class Meta:
        unique_together = ("user", "command_id")
        ordering = ["position"]

    def __str__(self):
        return f"{self.user} – {self.command_id} (pos={self.position})"
