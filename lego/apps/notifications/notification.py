from lego.utils.tasks import send_email

from .models import NotificationSetting


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
            'email': self.generate_mail
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

    def generate_mail(self):
        """
        Create and sent the email message.
        """
        raise NotImplemented
