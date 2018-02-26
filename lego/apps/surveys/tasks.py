from django.db import IntegrityError, transaction
from django.utils import timezone
from structlog import get_logger

from lego import celery_app
from lego.apps.events.constants import PRESENT
from lego.apps.stats.utils import track
from lego.apps.surveys.models import Survey
from lego.apps.surveys.notifications import SurveyNotification
from lego.utils.tasks import AbakusTask

log = get_logger()


@celery_app.task(serializer='json',  base=AbakusTask)
def survey_mail(self, logger_context=None):
    self.setup_logger(logger_context)

    surveys = Survey.objects.filter(active_from__lte=timezone.now(), sent=False)
    for survey in surveys.all():
        with transaction.atomic():
            for registration in survey.event.registrations.filter(presence=PRESENT):
                notification = SurveyNotification(registration, survey=survey)
                notification.notify()
                track(survey, 'survey.create', properties={'survey_id': self.id})
            survey.sent = True
            survey.save()
