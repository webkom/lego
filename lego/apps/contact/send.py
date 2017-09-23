from lego.apps.users.models import AbakusGroup
from lego.utils.tasks import send_email


def send_message(title, message, user, anonymous):
    """
    Send a message to HS when users posts to the contact form.
    Don't catch AbakusGroup.DoesNotExist, this notifies us when the group doesn't exist.
    """
    anonymous = anonymous if user.is_authenticated else True
    abakus_group = AbakusGroup.objects.get(name='Hovedstyret')
    users = [membership.user for membership in abakus_group.memberships.select_related('user')]
    emails = [user.email_address for user in users]

    from_name = 'Anonymous' if anonymous else user.full_name
    from_email = 'Unknown' if anonymous else user.email_address

    send_email.delay(
        to_email=emails,
        context={
            'title': title,
            'message': message,
            'from_name': from_name,
            'from_email': from_email
        },
        subject='Ny henvendelse fra kontaktskjemaet',
        plain_template='contact/email/contact_form.html',
        html_template='contact/email/contact_form.txt',
        from_email=None
    )
