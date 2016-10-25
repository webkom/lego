from datetime import timedelta

from django.utils import timezone

from lego.utils.managers import PersistentModelManager
from lego.settings.lego import PENALTY_DURATION, PENALTY_IGNORE_SUMMER, PENALTY_IGNORE_WINTER


class AbakusGroupManager(PersistentModelManager):
    def get_by_natural_key(self, name):
        return self.get(name__iexact=name.lower())


class UserManager(PersistentModelManager):
    def get_by_natural_key(self, username):
        return self.get(username__iexact=username.lower())


class MembershipManager(PersistentModelManager):
    def get_by_natural_key(self, username, abakus_group_name):
        return self.get(user__username__iexact=username.lower(),
                        abakus_group__name__iexact=abakus_group_name.lower())


class UserPenaltyManager(PersistentModelManager):

    def valid(self):
        return super(UserPenaltyManager, self).get_queryset().\
            filter(created_at__gt=timezone.now() - self.penalty_offset(timezone.now(), False))

    def penalty_offset(self, start_date, forwards=True):

        remaining_days = PENALTY_DURATION.days
        offset_days = 0
        multiplier = 1 if forwards else -1

        while remaining_days > 0:

            date_to_check = start_date + (multiplier * timedelta(days=offset_days))

            if not self.ignore_date(date_to_check):
                remaining_days -= 1

            offset_days += 1

        return timedelta(days=offset_days)

    def ignore_date(self, date):
        summer_from, summer_to = PENALTY_IGNORE_SUMMER
        winter_from, winter_to = PENALTY_IGNORE_WINTER
        if summer_from \
                < (date.month, date.day) \
                < summer_to:
            return True
        elif winter_to \
                < (date.month, date.day) \
                < winter_from:
            return False
        return True
