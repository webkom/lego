from django.db import transaction
from django.utils import timezone
from structlog import get_logger

from lego import celery_app
from lego.apps.events.constants import PRESENT
from lego.apps.stats.utils import track
from lego.apps.surveys.models import Survey
from lego.apps.surveys.notifications import SurveyNotification
from lego.utils.tasks import AbakusTask

log = get_logger()


@celery_app.task(serializer='json', bind=True, base=AbakusTask)
def send_survey_mail(self, logger_context=None):
    self.setup_logger(logger_context)

    surveys = Survey.objects.filter(active_from__lte=timezone.now(), sent=False)
    print('surveys in send_mail', surveys.all())
    for survey in surveys.all():
        with transaction.atomic():
            print('survey id', survey.id, survey.sent)
            for registration in survey.event.registrations.filter(presence=PRESENT):
                notification = SurveyNotification(registration.user, survey=survey)
                notification.notify()
                track(registration.user, 'survey.create', properties={'survey_id': survey.id})
            survey.sent = True
            survey.save()
            print('survey after saving', survey.sent)
