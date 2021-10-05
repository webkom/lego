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

    max_inactive_days = 183

    users_to_delete = User.objects.filter(
        Q(last_login__lte=timezone.now() - timedelta(days=max_inactive_days))
        and Q(inactive_notified_counter__gte=4)
    )

    for user in users_to_delete:
        user.delete(force=True)
        user.save()

    def send_inactive_notification(user):
        notification = InactiveNotification(user, max_inactive_days=max_inactive_days)
        notification.notify()
        user.inactive_notified_counter += 1
        user.save()

    users_to_notifiy_weekly = User.objects.filter(
        last_login__lte=timezone.now() - timedelta(days=156)
    )

    for user in users_to_notifiy_weekly:
        send_inactive_notification(user)

    users_to_notifiy_montly = User.objects.filter(
        Q(last_login__lte=timezone.now() - timedelta(days=126))
        and Q(inactive_notified_counter=0)
    )

    for user in users_to_notifiy_montly:
        send_inactive_notification(user)
