from django.contrib.postgres.fields import ArrayField
from django.db import models

from .constants import CHANNEL_CHOICES, CHANNELS, NOTIFICATION_CHOICES, NOTIFICATION_TYPES


class NotificationSetting(models.Model):
    """
    All notifications is enabled by default. We need to create an instance of this model
    to adjust this.
    """

    user = models.ForeignKey('users.User')
    notification_type = models.CharField(max_length=64, choices=NOTIFICATION_CHOICES)
    enabled = models.BooleanField(default=True)
    channels = ArrayField(
        models.CharField(max_length=64, choices=CHANNEL_CHOICES),
        default=CHANNELS,
        null=True
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
