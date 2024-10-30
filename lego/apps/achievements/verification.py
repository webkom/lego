from django.db.models import Count, Sum
from django.utils import timezone

from lego.apps.events.constants import PAYMENT_MANUAL, PAYMENT_SUCCESS, SUCCESS_REGISTER
from lego.apps.events.models import Registration
from lego.apps.polls.models import Poll
from lego.apps.quotes.models import Quote
from lego.apps.users.models import User


def check_event_generic(user: User, count: int):
    return (
        len(
            Registration.objects.filter(
                user=user, status=SUCCESS_REGISTER, event__end_time__lte=timezone.now()
            )
        )
        >= count
    )

def check_verified_quote(user: User):
    return Quote.objects.filter(approved=True, created_by=user).exists()


def check_poll_responses(user: User, count: int):
    return (
        Poll.objects.filter(
            answered_users__in=[user],
        ).count()
        >= count
    )


# There is a case where manual payment does not update the payment amount.
# I have not changed this code so only stripe payments will count.
def check_total_event_payment_over(user: User, price: int):
    total_paid = (
        Registration.objects.filter(
            user=user,
            event__is_priced=True,
            status=SUCCESS_REGISTER,
            payment_status__in=[PAYMENT_SUCCESS, PAYMENT_MANUAL],
            event__end_time__lte=timezone.now(),
        ).aggregate(total=Sum("payment_amount"))["total"]
        or 0
    )
    return total_paid > price
