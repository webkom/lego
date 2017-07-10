from structlog import get_logger

from lego.utils.tasks import send_email, send_push

from .models import NotificationSetting

log = get_logger()


class Notification:
    """
    Lookup notifications settings and use this to notify the user on activated channels.
    """

    name = None

    def __init__(self, user, *args, **kwargs):
        self.user = user
        self.args = args,
        self.kwargs = kwargs

    def notify(self):
        """
        Lookup channels per user and notify on the selected channels.
        """
        if self.name is None:
            raise ValueError('Set a name on the notification class.')

        generators = {
            'email': self.generate_mail,
            'push': self.generate_push,
        }

        channels = NotificationSetting.active_channels(self.user, self.name)

        for channel in channels:
            generator = generators.get(channel)
            generator()

    def _delay_mail(self, *args, **kwargs):
        """
        Helper for the send_mail celery task.
        """
        return send_email.delay(*args, **kwargs)

    def _delay_push(self, template, context, instance=None):
        """
        Helper for push messages. Does the work in a celery task.
        """
        return send_push.delay(
            user=self.user, template=template, context=context, instance=instance
        )

    def generate_mail(self):
        """
        Create and sent the email message.
        """
        raise NotImplemented

    def generate_push(self):
        """
        Send a push message to the user.
        """
        log.warn('push_message_not_implemented')
