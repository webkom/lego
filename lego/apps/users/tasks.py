from datetime import timedelta

from django.db.models import Q
from django.utils import timezone

from structlog import get_logger

from lego import celery_app
from lego.apps.users.models import User
from lego.apps.users.notifications import InactiveNotification
from lego.utils.tasks import AbakusTask

log = get_logger()


@celery_app.task(serializer="json", bind=True, base=AbakusTask)
def send_inactive_reminder_mail(self, logger_context=None):

    self.setup_logger(logger_context)

    # find all users that have been inactive for more than 5 months
    users = User.objects.filter(last_login__lte=timezone.now() - timedelta(days=156))

    for user in users:
        notification = InactiveNotification(user)
        notification.notify()
        user.inactive_notified_counter += 1
        user.save()

    # find all users that have been inactive for more than 4 months and have no notifications
    users = User.objects.filter(
        Q(last_login__lte=timezone.now() - timedelta(days=126))
        and Q(inactive_notified_counter__lt=1)
    )

    for user in users:
        notification = InactiveNotification(user)
        notification.notify()
        user.inactive_notified_counter += 1
        user.save()
