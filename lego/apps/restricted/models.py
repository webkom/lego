from django.contrib.postgres.fields import ArrayField
from django.core import signing
from django.db import models
from django.utils import timezone
from django.utils.crypto import get_random_string
from structlog import get_logger

from lego.apps.notifications.constants import EMAIL, WEEKLY_MAIL
from lego.apps.notifications.models import NotificationSetting
from lego.utils.models import BasisModel

log = get_logger()


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
    hide_sender = models.BooleanField(default=False)
    token = models.CharField(max_length=128, db_index=True, unique=True)
    used = models.DateTimeField(null=True)
    weekly = models.BooleanField(default=False)

    users = models.ManyToManyField('users.User', blank=True)
    groups = models.ManyToManyField('users.AbakusGroup', blank=True)
    events = models.ManyToManyField('events.Event', blank=True)
    meetings = models.ManyToManyField('meetings.Meeting', blank=True)
    raw_addresses = ArrayField(models.EmailField(), null=True)

    @classmethod
    def get_restricted_mail(cls, from_address, token):
        try:
            return cls.objects\
                .prefetch_related(*cls.MANY_TO_MANY_RELATIONS)\
                .get(used=None, from_address=from_address.lower(), token=token)
        except cls.DoesNotExist:
            return None
        except cls.MultipleObjectsReturned:
            log.exception('multiple_restricted_mails_returned')
            return None

    def lookup_recipients(self):
        """
        Loop over all many-to-many relations and lookup recipients.
        """
        all_users = []
        all_raw_addresses = self.raw_addresses or []

        for relation_name in self.MANY_TO_MANY_RELATIONS:
            relation = getattr(self, relation_name)
            for instance in relation.all():
                restricted_lookup = getattr(instance, 'restricted_lookup', None)
                if restricted_lookup:
                    users, raw_addresses = restricted_lookup()
                    all_users += list(users)
                    all_raw_addresses += list(raw_addresses)

        recipients = set(all_raw_addresses)

        for user in all_users:
            if self.weekly:
                if EMAIL not in NotificationSetting.active_channels(user, WEEKLY_MAIL):
                    continue
            recipients.add(user.email_address)

        return list(recipients)

    def mark_used(self, timestamp=None):
        """
        Mark the restricted mail as used with a timestamp.
        """
        timestamp = timestamp or timezone.now()
        self.used = timestamp
        self.save()

    def token_query_param(self):
        """
        Return a token that can be used to access the token file.
        """
        return signing.TimestampSigner().sign(self.id)

    def token_verify_query_param(self, token):
        """
        Verify token access based on the token query param.
        """
        try:
            # Valid in 10 min
            valid_in = 60 * 10
            data = signing.TimestampSigner().unsign(token, max_age=valid_in)
            return data == str(self.id)
        except signing.BadSignature:
            pass
        return False

    @staticmethod
    def create_token():
        token = get_random_string(128)
        return token
