from django.conf import settings
from django.db import models, transaction
from django.db.models import Sum
from django.utils import timezone
from rest_framework.exceptions import ParseError

from lego.apps.content.models import Content
from lego.apps.polls.permissions import PollPermissionHandler
from lego.apps.users.models import User
from lego.utils.models import BasisModel


def get_time_delta():
    return timezone.now() + timezone.timedelta(weeks=52)


class Poll(Content, BasisModel):

    description = models.TextField(blank=True)

    valid_until = models.DateTimeField(default=get_time_delta)

    answered_users = models.ManyToManyField(User, related_name="answered_polls")

    def __str__(self):
        return self.title

    @property
    def total_votes(self):
        return Option.objects.filter(poll=self).aggregate(total_votes=Sum("votes"))[
            "total_votes"
        ]

    def get_absolute_url(self):
        return f"{settings.FRONTEND_URL}/polls/{self.id}/"

    @transaction.atomic
    def vote(self, user, option_id):
        option = self.options.get(pk=option_id)
        if not option:
            raise ParseError(detail="Option not found.")
        option.votes += 1
        option.save()
        self.answered_users.add(user)
        self.save()

    class Meta:
        permission_handler = PollPermissionHandler()
        get_latest_by = "created_at"


class Option(BasisModel):

    name = models.CharField(max_length=30)
    votes = models.IntegerField(default=0)
    poll = models.ForeignKey(Poll, on_delete=models.CASCADE, related_name="options")

    def __str__(self):
        return self.name

    class Meta:
        ordering = ["-votes", "pk"]
