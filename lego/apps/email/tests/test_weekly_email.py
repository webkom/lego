from datetime import timedelta
from unittest.mock import patch

from django.utils import timezone

from lego.apps.email.tasks import send_weekly_email
from lego.apps.events.models import Pool
from lego.apps.joblistings.models import Joblisting
from lego.apps.notifications.models import NotificationSetting
from lego.apps.users.models import AbakusGroup, User
from lego.utils.test_utils import BaseTestCase


@patch("lego.apps.restricted.message_processor.MessageProcessor.send_mass_mail_html")
class WeeklyEmailTestCase(BaseTestCase):
    fixtures = [
        "test_users.yaml",
        "test_articles.yaml",
        "test_events.yaml",
        "test_companies.yaml",
        "test_abakus_groups.yaml",
        "test_joblistings.yaml",
    ]

    def setUp(self):
        pool = Pool.objects.get(pk=1)
        pool.activation_date = timezone.now() + timedelta(days=1)
        pool.save()
        joblisting = Joblisting.objects.first()
        joblisting.created_at = timezone.now() - timedelta(days=1)
        joblisting.save()
        pr = AbakusGroup.objects.get(name="PR")
        pr.add_user(User.objects.get(pk=10))

    def assertEmailContains(self, send_mass_mail_mock, content):
        message = send_mass_mail_mock.call_args.args[0][0][1]
        self.assertIn(content, message)

    def assertEmailDoesNotContain(self, send_mail_mock, content):
        message = send_mail_mock.call_args.args[0][0][1]
        self.assertNotIn(content, message)

    def test_generate_weekly(self, send_mail_mock):
        send_weekly_email()
        weekly_text = "Klikk deg inn for å lese"
        self.assertEmailContains(send_mail_mock, weekly_text)

    def test_generate_events(self, send_mail_mock):
        event_title = "Arrangementer med påmelding neste uke"
        send_weekly_email()
        self.assertEmailContains(send_mail_mock, event_title)
        self.assertEmailContains(send_mail_mock, "Bedriftspresentasjon")

    def test_generate_joblistings(self, send_mail_mock):
        joblisting_title = "Nye jobbannonser"
        send_weekly_email()
        self.assertEmailContains(send_mail_mock, joblisting_title)
        self.assertEmailContains(send_mail_mock, "Gutta Consulting")
        self.assertTrue(send_mail_mock.called)


@patch("lego.apps.restricted.message_processor.MessageProcessor.send_mass_mail_html")
class WeeklyEmailTestCaseNoWeekly(WeeklyEmailTestCase):
    fixtures = [
        "test_users.yaml",
        "test_events.yaml",
        "test_companies.yaml",
        "test_abakus_groups.yaml",
        "test_joblistings.yaml",
    ]

    def setUp(self):
        pool = Pool.objects.get(pk=1)
        pool.activation_date = timezone.now() + timedelta(days=1)
        pool.save()
        joblisting = Joblisting.objects.first()
        joblisting.created_at = timezone.now() - timedelta(days=1)
        joblisting.save()
        pr = AbakusGroup.objects.get(name="PR")
        pr.add_user(User.objects.get(pk=10))

    def test_generate_weekly(self, send_mail_mock):
        send_weekly_email()
        weekly_text = "Klikk deg inn for å lese"
        self.assertEmailDoesNotContain(send_mail_mock, weekly_text)

    def test_generate_events(self, send_mail_mock):
        send_weekly_email()
        event_title = "Arrangementer med påmelding neste uke"
        self.assertEmailContains(send_mail_mock, event_title)
        self.assertEmailContains(send_mail_mock, "Bedriftspresentasjon")

    def test_generate_joblistings(self, send_mail_mock):
        send_weekly_email()
        joblisting_title = "Nye jobbannonser"
        self.assertEmailContains(send_mail_mock, joblisting_title)
        self.assertEmailContains(send_mail_mock, "Gutta Consulting")


@patch("lego.apps.restricted.message_processor.MessageProcessor.send_mass_mail_html")
class WeeklyEmailTestCaseNoEventsOrWeekly(WeeklyEmailTestCase):
    fixtures = [
        "test_users.yaml",
        "test_abakus_groups.yaml",
        "test_companies.yaml",
        "test_joblistings.yaml",
    ]

    def setUp(self):
        joblisting = Joblisting.objects.first()
        joblisting.created_at = timezone.now() - timedelta(days=1)
        joblisting.save()
        pr = AbakusGroup.objects.get(name="PR")
        pr.add_user(User.objects.get(pk=10))

    def test_generate_weekly(self, send_mail_mock):
        send_weekly_email()
        weekly_text = "Klikk deg inn for å lese"
        self.assertEmailDoesNotContain(send_mail_mock, weekly_text)

    def test_generate_events(self, send_mail_mock):
        send_weekly_email()
        event_title = "Arrangementer med påmelding neste uke"
        self.assertEmailDoesNotContain(send_mail_mock, event_title)
        self.assertEmailDoesNotContain(send_mail_mock, "Bedriftspresentasjon")

    def test_generate_joblistings(self, send_mail_mock):
        send_weekly_email()
        joblisting_title = "Nye jobbannonser"
        self.assertEmailContains(send_mail_mock, joblisting_title)
        self.assertEmailContains(send_mail_mock, "Gutta Consulting")


@patch("lego.apps.restricted.message_processor.MessageProcessor.send_mass_mail_html")
class WeeklyEmailTestCaseNothing(BaseTestCase):
    fixtures = [
        "test_users.yaml",
        "test_abakus_groups.yaml",
    ]

    def setUp(self):
        pr = AbakusGroup.objects.get(name="PR")
        pr.add_user(User.objects.get(pk=10))
        return

    def test_send_mail(self, send_mass_mail_mock):
        send_weekly_email()
        self.assertFalse(send_mass_mail_mock.called)


@patch("lego.apps.restricted.message_processor.MessageProcessor.send_mass_mail_html")
class WeeklyEmailTaskTest(BaseTestCase):
    fixtures = [
        "test_users.yaml",
        "test_articles.yaml",
        "test_events.yaml",
        "test_companies.yaml",
        "test_abakus_groups.yaml",
        "test_joblistings.yaml",
        "test_notification_settings.yaml",
    ]

    def setUp(self):
        pool = Pool.objects.get(pk=1)
        pool.activation_date = timezone.now() + timedelta(days=1)
        pool.save()
        joblisting = Joblisting.objects.first()
        joblisting.created_at = timezone.now() - timedelta(days=1)
        joblisting.save()
        pr = AbakusGroup.objects.get(name="PR")
        pr.add_user(User.objects.get(pk=10))

    def test_email_sent(self, send_mass_mail_mock):
        send_weekly_email()
        self.assertTrue(send_mass_mail_mock.called)

    def test_notification_settings(self, send_mass_mail_mock):
        for notification_setting in NotificationSetting.objects.all():
            notification_setting.enabled = False
            notification_setting.save()

        send_weekly_email()
        self.assertFalse(send_mass_mail_mock.called)
