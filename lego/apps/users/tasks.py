from smtplib import SMTPException

from django.conf import settings
from django.core.mail import send_mail
from django.template import loader
from structlog import get_logger

from lego import celery_app
from lego.apps.users.models import User

log = get_logger()


@celery_app.task(bind=True, default_retry_delay=(60 * 5))
def async_send_registration_confirmation(self, username, user_email):
    """Send confirmation email to the user that registered."""

    # Generate a token for the registration confirmation
    token = User.generate_registration_token(username)
    message = loader.get_template("email/user_registration_email.html")

    context = {
        "username": username,
        "token": token,
        "settings": settings
    }

    try:
        send_mail('Velkommen til Abakus.no', message.render(context), None, [user_email])
    except SMTPException as e:
        log.error(
            'email_invitations_send_email_error',
            exception=e,
            username=username,
            user_email=user_email,
            token=token
        )
        raise self.retry(exc=e, max_retries=3)
