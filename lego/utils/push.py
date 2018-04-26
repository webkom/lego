from django.template.loader import render_to_string
from push_notifications.models import APNSDevice, GCMDevice
from structlog import get_logger

from lego.apps.feeds.models import NotificationFeed

log = get_logger()


class PushMessage:
    def __init__(self, user, template, context, target=None):
        self.user = user
        self.template = template
        self.context = context
        self.target = target

    def _get_unread_count(self):
        feed = NotificationFeed
        data = feed.get_notification_data(self.user.pk)
        return data.get('unread_count', 0)

    def send(self):
        """
        Send push messages to devices owned by the user. Apple supports a badge argument, this is
        set to the unread notifications count.
        """

        message = render_to_string(self.template, self.context).strip()
        extra = dict()
        if self.target:
            extra['target'] = self.target

        gcm_devices = GCMDevice.objects.filter(user=self.user, active=True)
        apns_devices = APNSDevice.objects.filter(user=self.user, active=True)

        log.info(
            'send_push', message=message, gcm_devices=gcm_devices.count(),
            apns_devices=apns_devices.count()
        )

        gcm_devices.send_message(message, extra=extra)
        apns_devices.send_message(message, badge=self._get_unread_count(), extra=extra)
