from unittest.mock import patch

from django.conf import settings

from lego.apps.surveys.models import Survey
from lego.apps.surveys.notifications import SurveyNotification
from lego.apps.users.models import User
from lego.utils.test_utils import BaseTestCase


@patch('lego.utils.email.django_send_mail')
class SurveyMailTestCase(BaseTestCase):
    fixtures = [
        'test_abakus_groups.yaml', 'test_users.yaml', 'test_companies.yaml', 'test_events.yaml',
        'test_surveys.yaml'
    ]

    def setUp(self):
        self.survey = Survey.objects.first()
        self.recipient = User.objects.first()
        self.notifier = SurveyNotification(user=self.recipient, survey=self.survey)

    def assertEmailContains(self, send_mail_mock, content):
        self.notifier.generate_mail()
        email_args = send_mail_mock.call_args[1]
        self.assertIn(content, email_args['message'])
        self.assertIn(content, email_args['html_message'])

    def test_generate_email_name(self, send_mail_mock):
        opening = 'Hei, ' + self.recipient.first_name + ' ' + self.recipient.last_name + '!'
        self.assertEmailContains(send_mail_mock, opening)

    def test_generate_email_event(self, send_mail_mock):
        event = 'Du har en ny undersøkelse å svare på for arrangement ' + self.survey.event.title \
                + '.'
        self.assertEmailContains(send_mail_mock, event)

    def test_generate_email_url(self, send_mail_mock):
        url = settings.FRONTEND_URL + '/surveys/' + str(self.survey.id) + '/answer'
        self.assertEmailContains(send_mail_mock, url)
