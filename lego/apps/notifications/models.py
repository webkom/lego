from django.contrib.postgres.fields import ArrayField
from django.db import models
from django.utils import timezone

from lego.apps.action_handlers.events import handle_event
from lego.utils.models import BasisModel

from .constants import CHANNEL_CHOICES, CHANNELS, NOTIFICATION_CHOICES, NOTIFICATION_TYPES


class NotificationSetting(models.Model):
    """
    All notifications is enabled by default. We need to create an instance of this model
    to adjust this.
    """

    user = models.ForeignKey('users.User', on_delete=models.CASCADE)
    notification_type = models.CharField(max_length=64, choices=NOTIFICATION_CHOICES)
    enabled = models.BooleanField(default=True)
    channels = ArrayField(
        models.CharField(max_length=64, choices=CHANNEL_CHOICES), default=CHANNELS, null=True
    )

    class Meta:
        unique_together = (('user', 'notification_type'), )

    @classmethod
    def active_channels(cls, user, notification_type):
        """
        Return a list of active notification channels for a given notification type.
        """
        if notification_type not in NOTIFICATION_TYPES:
            raise ValueError('You asked for an invalid notification_type')

        try:
            setting = cls.objects.get(user=user, notification_type=notification_type)
        except cls.DoesNotExist:
            # No setting equals all channels
            return CHANNELS

        if not setting.enabled:
            # Everything is disabled when the enabled flag is False
            return []

        # When enabled is True return all valid channels in the channels field.
        return list(set(setting.channels or []) & set(CHANNELS))

    @classmethod
    def lookup_setting(cls, user, notification_type):
        return cls.objects.get_or_create(
            user=user, notification_type=notification_type, defaults={
                'enabled': True,
                'channels': CHANNELS
            }
        )


class Announcement(BasisModel):
    """
    Send important messages to selected recipients.
    A notification is created when a message is saved.
    This works in the same way as restricted mail.
    The lookup functions on the relations is called announcement_lookup.
    """

    message = models.TextField()
    sent = models.DateTimeField(null=True, default=None)

    MANY_TO_MANY_RELATIONS = ['users', 'groups', 'events', 'meetings']

    users = models.ManyToManyField('users.User', blank=True)
    groups = models.ManyToManyField('users.AbakusGroup', blank=True)
    events = models.ManyToManyField('events.Event', blank=True)
    meetings = models.ManyToManyField('meetings.Meeting', blank=True)

    def lookup_recipients(self):
        """
        Lookup users that should receive this message.
        """
        all_users = []

        for relation_name in self.MANY_TO_MANY_RELATIONS:
            relation = getattr(self, relation_name)
            for instance in relation.all():
                announcement_lookup = getattr(instance, 'announcement_lookup', None)
                if announcement_lookup:
                    users = announcement_lookup()
                    all_users += list(users)

        return list(set(all_users))

    def send(self):
        if self.sent:
            # Message is sent already, nothing to do!
            return

        handle_event(self, 'send')
        self.sent = timezone.now()
        self.save()
