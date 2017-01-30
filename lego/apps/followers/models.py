from django.db import models

from lego.utils.models import PersistentModel, TimeStampModel


class Follower(PersistentModel, TimeStampModel):
    follower = models.ForeignKey('users.User')

    class Meta:
        abstract = True


class FollowUser(Follower):
    target = models.ForeignKey('users.User', related_name='followers')

    class Meta:
        unique_together = ('follower', 'target')


class FollowEvent(Follower):
    target = models.ForeignKey('events.Event', related_name='followers')

    class Meta:
        unique_together = ('follower', 'target')
