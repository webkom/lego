from datetime import timedelta
from math import ceil

from django.conf import settings
from django.db.models import Q
from django.utils import timezone

from structlog import get_logger

from lego import celery_app
from lego.apps.users.models import User
from lego.apps.users.notifications import DeletedUserNotification, InactiveNotification
from lego.utils.tasks import AbakusTask, send_email

log = get_logger()

MAX_INACTIVE_DAYS = 365
MIN_INACTIVE_DAYS = MAX_INACTIVE_DAYS - 2 * 30
MEDIAN_INACTIVE_DAYS = MAX_INACTIVE_DAYS - ceil(
    (MAX_INACTIVE_DAYS - MIN_INACTIVE_DAYS) / 2
)


@celery_app.task(serializer="json", bind=True, base=AbakusTask)
def send_inactive_reminder_mail(self, logger_context=None):

    self.setup_logger(logger_context)

    users_to_delete = User.objects.filter(
        Q(last_login__lte=timezone.now() - timedelta(days=MAX_INACTIVE_DAYS))
        & Q(inactive_notified_counter__gte=4)
    )

    list_usernames_to_delete = list(map(lambda u: u.username, users_to_delete))
    num_users_to_delete = len(users_to_delete)
    if len(list_usernames_to_delete) != num_users_to_delete:
        log.error(
            "Length of list of usernames to be deleted is not equal to number of users to be deleted",
            list_usernames_to_delete=list_usernames_to_delete,
            users_to_delete=users_to_delete,
        )

    for user in users_to_delete:
        notification = DeletedUserNotification(
            user, max_inactive_days=MAX_INACTIVE_DAYS
        )
        notification.notify()
        user.delete(force=True)

    send_email.delay(
        to_email=f"daemon@{settings.GSUITE_DOMAIN}",
        context={
            "userlist": list_usernames_to_delete,
        },
        subject=f"{num_users_to_delete} brukere har blitt slettet.",
        plain_template="users/email/list_of_deleted_users.txt",
        html_template="users/email/list_of_deleted_users.html",
    )

    def send_inactive_notification(user):
        notification = InactiveNotification(user, max_inactive_days=MAX_INACTIVE_DAYS)
        notification.notify()
        user.inactive_notified_counter += 1
        user.save()

    users_to_notifiy_weekly = User.objects.filter(
        last_login__lte=timezone.now() - timedelta(days=MEDIAN_INACTIVE_DAYS)
    )

    for user in users_to_notifiy_weekly:
        send_inactive_notification(user)

    users_to_notifiy_montly = User.objects.filter(
        Q(last_login__lte=timezone.now() - timedelta(days=MIN_INACTIVE_DAYS))
        & Q(inactive_notified_counter=0)
    )

    for user in users_to_notifiy_montly:
        send_inactive_notification(user)
