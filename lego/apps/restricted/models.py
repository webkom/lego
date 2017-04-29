from django.db import models

from lego.utils.models import BasisModel


class RestrictedMail(BasisModel):
    """
    This class represents a restricted mail. Each mail can only be used once and may contain a set
    of users, groups, events and meetings. It is possible to add more entities at a later point.

    The creator must provide the from mail and attach the generated token to the mail for
    security reasons.

    All models in the ManyToManyFields must contain a restricted_lookup function that returns a
    tuple ([users], [raw_addresses])
    """

    MANY_TO_MANY_RELATIONS = ['users', 'groups', 'events', 'meetings']

    from_address = models.EmailField(db_index=True)
    token = models.CharField(max_length=128, db_index=True)
    used = models.DateTimeField(null=True)

    users = models.ManyToManyField('users.User', null=True)
    groups = models.ManyToManyField('users.AbakusGroup', null=True)
    events = models.ManyToManyField('events.Event', null=True)
    meetings = models.ManyToManyField('meetings.Meeting', null=True)

    @classmethod
    def get_restricted_mail(cls, from_address, token):
        return cls.objects\
            .prefetch_related(*cls.MANY_TO_MANY_RELATIONS)\
            .get(used=None, from_address=from_address, token=token)

    def lookup_recipients(self):
        pass
