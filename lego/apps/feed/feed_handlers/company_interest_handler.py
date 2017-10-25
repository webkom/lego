from django.conf import settings

from lego.apps.companies.models import CompanyInterest
from lego.apps.companies.notifications import CompanyInterestNotification
from lego.apps.feed.activities import Activity
from lego.apps.feed.feed_handlers.base_handler import BaseHandler
from lego.apps.feed.feed_manager import feed_manager
from lego.apps.feed.feeds.notification_feed import NotificationFeed
from lego.apps.feed.registry import register_handler
from lego.apps.feed.verbs import CompanyInterestVerb
from lego.apps.users.models import AbakusGroup
from lego.utils.tasks import send_email


class CompanyInterestHandler(BaseHandler):

    model = CompanyInterest
    manager = feed_manager

    def handle_interest(self, company_interest):

        activity = Activity(
            actor=company_interest,
            verb=CompanyInterestVerb,
            object=company_interest,
            time=company_interest.created_at,
            extra_context={}
        )

        recipients = [
            member.user for member in AbakusGroup.objects.get(name="Bedkom").memberships.all()
        ]

        self.manager.add_activity(
            activity, [recipient.pk for recipient in recipients], [NotificationFeed]
        )

        for recipient in recipients:
            notification = CompanyInterestNotification(
                recipient, company_interest=company_interest
            )
            notification.notify()

        send_email.delay(
                to_email=f'bedriftskontakt@{settings.GSUITE_DOMAIN}',
                context=company_interest.generate_mail_context(),
                subject='En ny bedrift har meldt sin interesse',
                plain_template='companies/email/company_interest.txt',
                html_template='companies/email/company_interest.html',
            )

    def handle_create(self, company_interest):
        pass

    def handle_update(self, company_interest):
        pass

    def handle_delete(self, company_interest):
        pass


register_handler(CompanyInterestHandler)
