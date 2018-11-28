from lego.apps.users.models import AbakusGroup
from lego.utils.tasks import send_email


def send_message(title, message, user, anonymous):
    """
    Send a message to HS when users posts to the contact form.
    Don't catch AbakusGroup.DoesNotExist, this notifies us when the group doesn't exist.
    """
    anonymous = anonymous if user.is_authenticated else True
    abakus_group = AbakusGroup.objects.get(name="Hovedstyret")

    from_name = "Anonymous" if anonymous else user.full_name
    from_email = "Unknown" if anonymous else user.email_address

    send_email.delay(
        to_email=abakus_group.contact_email,
        context={
            "title": title,
            "message": message,
            "from_name": from_name,
            "from_email": from_email,
        },
        subject="Ny henvendelse fra kontaktskjemaet",
        plain_template="contact/email/contact_form.txt",
        html_template="contact/email/contact_form.html",
        from_email=None,
    )
