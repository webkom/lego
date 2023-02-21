from django.conf import settings
from django.utils import timezone

from lego.apps.action_handlers.handler import Handler
from lego.apps.action_handlers.registry import register_handler
from lego.apps.companies.models import CompanyInterest
from lego.apps.feeds.feed_manager import feed_manager
from lego.utils.tasks import send_email


class CompanyInterestHandler(Handler):

    model = CompanyInterest
    manager = feed_manager

    def handle_create(self, instance, **kwargs):

        # activity = Activity(
        #    actor=instance,
        #    verb=CompanyInterestVerb,
        #    object=instance,
        #    time=instance.created_at,
        #    extra_context={},
        # )

        # recipients = [
        #    member.user
        #    for member in AbakusGroup.objects.get(name="Bedkom").memberships.all()
        # ]

        # self.manager.add_activity(
        #    activity, [recipient.pk for recipient in recipients], [NotificationFeed]
        # )

        # for recipient in recipients:
        #    notification = CompanyInterestNotification(
        #        recipient, company_interest=instance
        #    )
        #    notification.notify()

        mail_context = instance.generate_mail_context()
        recipients = [f"bedriftskontakt@{settings.GSUITE_DOMAIN}"]

        current_date = timezone.now()
        booking_period_from, booking_period_to = settings.BEDKOM_BOOKING_PERIOD

        if (
            booking_period_from
            <= (current_date.month, current_date.day)
            <= booking_period_to
        ):
            # If a company sends in an interest form within bedkoms booking period, an automatic
            # reply is sent to them (and bedkom)
            recipients.append(mail_context["mail"])
            if mail_context["readme"]:
                # recipients.append(f"lederreadme@{settings.GSUITE_DOMAIN}")
                recipients.append("redaktor@abakus.no")
            send_email.delay(
                to_email=recipients,
                context=mail_context,
                subject="Takk for din interesse!",
                plain_template="companies/email/response_mail_company.txt",
                html_template="companies/email/response_mail_company.html",
            )
        else:
            # If a company sends in an interest form outside of bedkoms booking
            # period, the answers from the form is forwarded to bedkom so they can reply manually
            send_email.delay(
                to_email=recipients,
                context=mail_context,
                subject="En ny bedrift har meldt sin interesse",
                plain_template="companies/email/response_mail_bedkom.txt",
                html_template="companies/email/response_mail_bedkom.html",
            )


register_handler(CompanyInterestHandler)
