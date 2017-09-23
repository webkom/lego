from django.conf import settings
from django.core.mail import send_mail as django_send_mail
from django.template.loader import render_to_string
from premailer import transform
from structlog import get_logger

log = get_logger()


def send_email(to_email, context, subject, plain_template, html_template, from_email=None,):
    """
    Render a plain and html message based on a context and send it using django.core.mail.
    """

    plain_body = render_to_string(plain_template, context)

    html_body = None
    if html_template:
        html_body = render_to_string(html_template, context)

    recipient_list = to_email if isinstance(to_email, list) else [to_email]

    log.info('send_mail', subject=subject, from_email=from_email, recipient_list=recipient_list)

    django_send_mail(
        subject=subject,
        message=plain_body,
        from_email=from_email,
        recipient_list=recipient_list,
        html_message=transform(html_body),
        fail_silently=False
    )


class EmailMessage:

    def __init__(
            self, subject, to_email, plain_template, html_template, context=None, from_email=None
    ):
        self.subject = subject
        self.to_email = to_email
        self.plain_template = plain_template
        self.html_template = html_template
        self.context = context or {}
        self.from_email = from_email or settings.DEFAULT_FROM_EMAIL

    def system_context(self):
        context = {
            'site': settings.SITE['domain'],
            'from': settings.SITE['owner'],
            'system_name': settings.SITE['name'],
            'frontend_url': settings.FRONTEND_URL

        }
        return context

    def custom_context(self, *args, **kwargs):
        """
        Override this method to generate custom context variables.
        """
        return self.context

    def build_context(self, **kwargs):
        context = {
            'title': self.subject
        }
        context.update(self.system_context())
        context.update(self.custom_context())
        context.update(kwargs)
        return context

    def send(self, **kwargs):
        context = self.build_context(**kwargs)
        return send_email(
            self.to_email,
            context,
            self.subject,
            self.plain_template,
            self.html_template,
            self.from_email
        )
