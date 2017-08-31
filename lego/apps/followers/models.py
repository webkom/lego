from django.db import models

from lego.apps.followers.permissions import FollowersPermissionHandler
from lego.utils.models import TimeStampModel


class Follower(TimeStampModel):
    follower = models.ForeignKey('users.User')

    class Meta:
        abstract = True


class FollowUser(Follower):
    target = models.ForeignKey('users.User', related_name='followers')

    class Meta:
        unique_together = ('follower', 'target')
        permission_handler = FollowersPermissionHandler()


class FollowEvent(Follower):
    target = models.ForeignKey('events.Event', related_name='followers')

    class Meta:
        unique_together = ('follower', 'target')
        permission_handler = FollowersPermissionHandler()


class FollowCompany(Follower):
    target = models.ForeignKey('companies.Company', related_name='followers')

    class Meta:
        unique_together = ('follower', 'target')
        permission_handler = FollowersPermissionHandler()
