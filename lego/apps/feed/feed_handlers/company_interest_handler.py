from lego.apps.feed.activities import Activity
from lego.apps.feed.feed_handlers.base_handler import BaseHandler
from lego.apps.feed.feed_manager import feed_manager
from lego.apps.feed.feeds.notification_feed import NotificationFeed
from lego.apps.feed.registry import register_handler
from lego.apps.feed.verbs import CompanyInterestVerb
from lego.apps.companies.models import CompanyInterest
from lego.apps.companies.notifications import CompanyInterestNotification
from lego.apps.users.models import AbakusGroup


class CompanyInterestHandler(BaseHandler):

    model = CompanyInterest
    manager = feed_manager

    def handle_create(self, company_interest):

        activity = Activity(
            actor=company_interest.company_name,
            verb=CompanyInterestVerb,
            object=company_interest,
            time=company_interest.created_at,
            extra_context={}
        )

        recipients = [membership.user for membership in AbakusGroup.objects.get(name="Bedkom").memberships()]

        self.manager.add_activity(activity, [recipient.pk for recipient in recipients], [NotificationFeed])

        for recipient in recipients:
            notification = CompanyInterestNotification(
                recipient, company_interest=company_interest
            )
            notification.notify()

    def handle_update(self, company_interest):
        pass

    def handle_delete(self, company_interest):
        pass

register_handler(CompanyInterestHandler)
