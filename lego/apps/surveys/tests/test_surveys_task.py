from django.utils import timezone

from lego.apps.surveys.models import Survey
from lego.apps.surveys.tasks import send_survey_mail
from lego.utils.test_utils import BaseTestCase


class SurveyMailTestCase(BaseTestCase):
    fixtures = [
        'test_abakus_groups.yaml', 'test_users.yaml', 'test_companies.yaml', 'test_events.yaml',
        'test_surveys.yaml'
    ]

    def setUp(self):
        self.surveys = Survey.objects.all()

    def test_sent_true(self):
        active_surveys = self.surveys.filter(active_from__lte=timezone.now())
        self.assertEqual(len(active_surveys), 2)

        for survey in active_surveys:
            self.assertEqual(survey.sent, False)

        send_survey_mail()
        for survey in active_surveys:
            survey.refresh_from_db()
            self.assertEqual(survey.sent, True)
