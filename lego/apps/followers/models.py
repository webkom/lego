from django.db import models

from lego.utils.models import BasisModel


class Follower(BasisModel):
    follower = models.ForeignKey('users.User', related_name='following')


class FollowUser(Follower):
    followed_user = models.ForeignKey('users.User', related_name='followers')


class FollowEvent(Follower):
    followed_event = models.ForeignKey('events.Event', related_name='followers')


"""
class FollowCompany(Follower):
    followed_company = models.ForeignKey('companies.Company', related_name='followers')
"""
