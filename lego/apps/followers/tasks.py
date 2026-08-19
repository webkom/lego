from datetime import timedelta

from django.utils import timezone

from structlog import get_logger

from lego import celery_app
from lego.apps.events.models import Pool
from lego.apps.followers.notifications import RegistrationReminderNotification
from lego.utils.tasks import AbakusTask

log = get_logger()


@celery_app.task(serializer="json", bind=True, base=AbakusTask)
def send_registration_reminder_mail(self, logger_context=None):
    self.setup_logger(logger_context)

    pools = (
        Pool.objects.filter(
            activation_date__gt=timezone.now(),
            activation_date__lte=timezone.now() + timedelta(minutes=60),
        )
        .order_by("activation_date")
        .prefetch_related("event", "event__followers", "event__followers__follower")
    )

    for pool in pools:
        pool_group_ids = set(pool.permission_groups.values_list("id", flat=True))
        for followsevent in pool.event.followers.all():
            if followsevent.notification_sent:
                continue

            user = followsevent.follower
            if pool_group_ids.isdisjoint(group.id for group in user.all_groups):
                continue
            if pool.event.registrations.filter(user=user).exists():
                continue

            RegistrationReminderNotification(user, event=pool.event).notify()
            followsevent.notification_sent = True
            followsevent.save()
