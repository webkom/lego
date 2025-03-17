import itertools
from datetime import datetime, timedelta

from django.db.models import Q, Sum
from django.db.models.functions import ExtractYear
from django.db.models.manager import BaseManager
from django.utils import timezone

from lego.apps.events.constants import (
    PAYMENT_MANUAL,
    PAYMENT_SUCCESS,
    PRESENCE_CHOICES,
    SUCCESS_REGISTER,
)
from lego.apps.events.models import Registration
from lego.apps.polls.models import Poll
from lego.apps.quotes.models import Quote
from lego.apps.users.models import Penalty, User


def _passed_user_registrations(user: User) -> BaseManager[Registration]:
    return Registration.objects.filter(
        user=user,
        status=SUCCESS_REGISTER,
        event__end_time__lte=timezone.now(),
        pool__isnull=False,
    )


def check_event_generic(user: User, count: int) -> bool:
    return _passed_user_registrations(user).count() >= count


def check_verified_quote(user: User):
    return Quote.objects.filter(approved=True, created_by=user).exists()


def check_complete_profile(user: User):
    return user.github_username and user.linkedin_id and bool(user.picture)


def check_poll_responses(user: User, count: int):
    return (
        Poll.objects.filter(
            answered_users__in=[user],
        ).count()
        >= count
    )


def _generate_penalty_intervals(
    user: User, start_time: datetime, end_time: datetime
) -> list[tuple[datetime, datetime]]:
    intervals: list[tuple[datetime, datetime]] = []

    if penalties := Penalty.objects.filter(user=user).order_by("created_at"):
        intervals.append((start_time, penalties.first().created_at))
        intervals.extend(
            [
                (first.created_at, second.created_at)
                for first, second in itertools.pairwise(penalties)
            ]
        )
        intervals.append((penalties.last().created_at, end_time))
    else:
        intervals.append((start_time, end_time))

    return intervals


def check_longest_period_without_penalties(user: User, years: int) -> bool:
    if not user.has_grade_group:
        return False
    if not (
        registrations := _passed_user_registrations(user).order_by("event__end_time")
    ).exists():
        return False

    days = 365 * years
    max_registration_interval = timedelta(days=365)  # Once a year
    start_time = registrations.first().event.end_time
    end_time = registrations.last().event.end_time
    intervals = _generate_penalty_intervals(user, start_time, end_time)

    for start_time, end_time in intervals:
        if (end_time - start_time).days < days:
            continue

        current_start = current_end = start_time

        while (cutoff_time := current_end + max_registration_interval) < end_time:
            if (cutoff_time - current_start).days >= days:
                return True

            last_registration_in_interval = (
                _passed_user_registrations(user)
                .filter(
                    event__end_time__gt=current_end, event__end_time__lte=cutoff_time
                )
                .last()
            )

            if last_registration_in_interval is not None:
                current_end = last_registration_in_interval.event.end_time
                continue

            next_event = (
                _passed_user_registrations(user)
                .filter(event__end_time__gt=cutoff_time)
                .first()
            )

            if next_event is None:
                break

            current_start = current_end = next_event.event.end_time

        if (end_time - current_start).days >= days:
            return True

    return False


def check_total_genfors_events(user: User, count: int) -> bool:
    queryset = (
        Registration.objects.filter(
            user=user,
            event__title__icontains="generalfor",
            event__end_time__lt=timezone.now(),
        )
        .annotate(year=ExtractYear("event__end_time"))
        .filter(
            Q(year__lt=2025)
            | Q(presence__in=[PRESENCE_CHOICES.PRESENT, PRESENCE_CHOICES.LATE])
        )
    )
    return count <= queryset.count()


def check_total_galas(user: User, count: int) -> bool:
    # Will need to be updated if there are more gala-like events
    gala_substrings = (
        "bankett",  # Max 3 (itDAGENE)
        "halvingfest",  # Max 1
        "immatrikuleringsball",  # Max 5
        "jubileum",  # Max 4 (Abakus, Abakusrevyen, LaBamba, readme)
        "julebord",  # Max 5
        "utmatrikuleringsfest",  # Max 1
        "vaargalla",  # Max 5
    )

    query = Q()
    for substring in gala_substrings:
        query |= Q(event__title__icontains=substring)

    queryset = _passed_user_registrations(user).filter(query)

    if count == 1:
        return queryset.exists()
    return queryset.count() >= count


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
