from django.conf import settings

from lego.apps.action_handlers.handler import Handler
from lego.apps.action_handlers.registry import register_handler
from lego.apps.companies.models import CompanyInterest
from lego.apps.companies.notifications import CompanyInterestNotification
from lego.apps.feeds.activity import Activity
from lego.apps.feeds.feed_manager import feed_manager
from lego.apps.feeds.models import NotificationFeed
from lego.apps.feeds.verbs import CompanyInterestVerb
from lego.apps.users.models import AbakusGroup
from lego.utils.tasks import send_email


class CompanyInterestHandler(Handler):

    model = CompanyInterest
    manager = feed_manager

    def handle_create(self, instance, **kwargs):

        activity = Activity(
            actor=instance, verb=CompanyInterestVerb, object=instance, time=instance.created_at,
            extra_context={}
        )

        recipients = [
            member.user for member in AbakusGroup.objects.get(name="Bedkom").memberships.all()
        ]

        self.manager.add_activity(
            activity,
            [recipient.pk for recipient in recipients],
            [NotificationFeed]
        )

        for recipient in recipients:
            notification = CompanyInterestNotification(recipient, company_interest=instance)
            notification.notify()

        send_email.delay(
            to_email=f'bedriftskontakt@{settings.GSUITE_DOMAIN}',
            context=instance.generate_mail_context(),
            subject='En ny bedrift har meldt sin interesse',
            plain_template='companies/email/company_interest.txt',
            html_template='companies/email/company_interest.html',
        )


register_handler(CompanyInterestHandler)
