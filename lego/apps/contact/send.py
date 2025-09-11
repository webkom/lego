from lego.apps.users.constants import LEADER
from lego.apps.users.models import AbakusGroup
from lego.utils.tasks import send_email


def send_message(title, message, user, recipient_group):
    """
    Send a message to HS when users posts to the contact form.
    Don't catch AbakusGroup.DoesNotExist, this notifies us when the group doesn't exist.
    """
    
    if not user or user.is_anonymous:
        raise ValueError("User must be authenticated")

    # Handle no recipient group as HS
    if not recipient_group:
        recipient_group = AbakusGroup.objects.get(name="Hovedstyret")

    recipient_emails = get_recipients(recipient_group)

    send_email.delay(
        to_email=recipient_emails,
        context={
            "title": title,
            "message": message,
            "from_name": user.full_name,
            "from_email": user.email_address,
            "recipient_group": recipient_group.__str__(),
        },
        subject=f"Ny henvendelse fra kontaktskjemaet til {recipient_group.__str__()}",
        plain_template="contact/email/contact_form.txt",
        html_template="contact/email/contact_form.html",
        from_email=None,
    )


def get_recipients(recipient_group):
    hs_group = AbakusGroup.objects.get(name="Hovedstyret")
    if recipient_group == hs_group:
        return [hs_group.contact_email]
    recipient_leaders = [
        membership.user
        for membership in recipient_group.memberships.filter(
            role=LEADER
        ).select_related("user")
    ]
    return [leader.email_address for leader in recipient_leaders]
