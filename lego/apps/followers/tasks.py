from lego.apps.followers.notifications import RegistrationReminderNotification

from django.utils import timezone
from datetime import timedelta

from structlog import get_logger

from lego import celery_app
from lego.apps.events.constants import PRESENT
from lego.apps.stats.utils import track
from lego.apps.events.models import Pool
from lego.utils.tasks import AbakusTask

log = get_logger()


@celery_app.task(serializer="json", bind=True, base=AbakusTask)
def send_survey_mail(self, logger_context=None):
    self.setup_logger(logger_context)

    pools = Pool.objects.filter(
        activation_date__gt=timezone.now() + timedelta(minutes=30), activation_date__lte=timezone.now() + timedelta(minutes=60)
    ).prefetch_related("event", "event__followers", "event__followers__follower")

    for pool in pools:
        for followsevent in pool.event.followers.all():
            user = followsevent.follower

            if pool.permission_groups.filter(id__in=[user.id for user in
                                                     user.all_groups]).exists():
                print(user, pool.event)
                print(pool.event.is_admitted(user))
                notification = RegistrationReminderNotification(
                    user, event=pool.event)
                notification.notify()
