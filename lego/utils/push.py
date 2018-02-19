from django.template.loader import render_to_string
from push_notifications.models import APNSDevice, GCMDevice
from structlog import get_logger

from lego.utils.content_types import instance_to_string

log = get_logger()


class PushMessage:
    def __init__(self, user, template, context, instance=None):
        self.user = user
        self.template = template
        self.context = context
        self.instance = instance

    def _get_unread_count(self):
        return 0

    def send(self):
        """
        Send push messages to devices owned by the user. Apple supports a badge argument, this is
        set to the unread notifications count.
        """

        message = render_to_string(self.template, self.context).strip()
        extra = dict()
        if self.instance:
            extra['target'] = instance_to_string(self.instance)

        gcm_devices = GCMDevice.objects.filter(user=self.user, active=True)
        apns_devices = APNSDevice.objects.filter(user=self.user, active=True)

        log.info(
            'send_push', message=message, gcm_devices=gcm_devices.count(),
            apns_devices=apns_devices.count()
        )

        gcm_devices.send_message(message, extra=extra)
        apns_devices.send_message(message, badge=self._get_unread_count(), extra=extra)
