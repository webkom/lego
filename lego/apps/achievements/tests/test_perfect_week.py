from datetime import timedelta

from django.utils import timezone

from lego.apps.achievements.constants import PERFECT_WEEK_IDENTIFIER
from lego.apps.achievements.models import Achievement
from lego.apps.achievements.promotion import check_perfect_week_related_single_user
from lego.apps.achievements.verification import check_perfect_week
from lego.apps.events.constants import (
    PAYMENT_SUCCESS,
    PRESENCE_CHOICES,
    SUCCESS_REGISTER,
)
from lego.apps.events.models import Event, Pool, Registration
from lego.apps.events.tests.utils import get_dummy_users
from lego.apps.users.models import AbakusGroup, User
from lego.utils.test_utils import BaseTestCase

# A Monday a few weeks in the past - every event built on top of this is
# guaranteed to already have "ended" by the time a test runs.
_TODAY = timezone.localtime(timezone.now()).date()
BASE_MONDAY = timezone.make_aware(
    timezone.datetime.combine(
        _TODAY - timedelta(days=_TODAY.weekday(), weeks=10),
        timezone.datetime.min.time(),
    )
) + timedelta(hours=10)


def _create_event(start_time, group, is_priced=False):
    event = Event.objects.create(
        title=f"event-{start_time.isoformat()}",
        start_time=start_time,
        end_time=start_time + timedelta(hours=2),
        is_priced=is_priced,
    )
    pool = Pool.objects.create(
        name="Pool",
        capacity=50,
        event=event,
        activation_date=start_time - timedelta(days=7),
    )
    pool.permission_groups.set([group])
    return event


def _extra_users(n, group):
    # get_dummy_users always starts at username "0", so it collides with the
    # test's own self.user - build extras with distinct usernames instead.
    users = []
    for i in range(n):
        user = User.objects.create(
            username=f"other{i}", first_name=f"other{i}", email=f"other{i}@aba.wtf"
        )
        group.add_user(user)
        users.append(user)
    return users


def _register(user, event, presence=PRESENCE_CHOICES.UNKNOWN, payment_status=""):
    return Registration.objects.create(
        event=event,
        user=user,
        pool=event.pools.first(),
        status=SUCCESS_REGISTER,
        presence=presence,
        payment_status=payment_status,
    )


class CheckPerfectWeekTestCase(BaseTestCase):
    fixtures = ["test_abakus_groups.yaml"]

    def setUp(self):
        self.user = get_dummy_users(1)[0]
        self.group = AbakusGroup.objects.get(name="Users")

    def _fill_week(self, monday, count, attend=True, presence=PRESENCE_CHOICES.PRESENT):
        events = [
            _create_event(monday + timedelta(days=i), self.group) for i in range(count)
        ]
        if attend:
            for event in events:
                _register(self.user, event, presence=presence)
        return events

    def test_no_eligible_events_does_not_qualify(self):
        self.assertFalse(check_perfect_week(self.user, weeks=1))

    def test_qualifies_with_min_events_all_attended(self):
        self._fill_week(BASE_MONDAY, 3)
        self.assertTrue(check_perfect_week(self.user, weeks=1))

    def test_fails_below_min_events(self):
        self._fill_week(BASE_MONDAY, 2)
        self.assertFalse(check_perfect_week(self.user, weeks=1))

    def test_fails_if_one_event_missed(self):
        events = self._fill_week(BASE_MONDAY, 3, attend=False)
        for event in events[:2]:
            _register(self.user, event, presence=PRESENCE_CHOICES.PRESENT)
        # events[2] is left unregistered
        self.assertFalse(check_perfect_week(self.user, weeks=1))

    def test_ignores_events_outside_users_groups(self):
        other_group = AbakusGroup.objects.create(name="SomeOtherGroup")
        for i in range(3):
            _create_event(BASE_MONDAY + timedelta(days=i), other_group)
        self.assertFalse(check_perfect_week(self.user, weeks=1))

    def test_untracked_event_falls_back_to_registration_only(self):
        # No one's presence was ever marked, so the event never "took
        # attendance" - the looser registered-with-a-pool standard applies.
        self._fill_week(BASE_MONDAY, 3, presence=PRESENCE_CHOICES.UNKNOWN)
        self.assertTrue(check_perfect_week(self.user, weeks=1))

    def test_tracked_event_requires_present_or_late(self):
        events = self._fill_week(BASE_MONDAY, 3, attend=False)
        # Mark presence for enough other users to cross the "tracked" threshold,
        # but leave our user's own presence as NOT_PRESENT.
        others = _extra_users(3, self.group)
        for event in events:
            for other in others:
                _register(other, event, presence=PRESENCE_CHOICES.PRESENT)
            _register(self.user, event, presence=PRESENCE_CHOICES.NOT_PRESENT)

        self.assertFalse(check_perfect_week(self.user, weeks=1))

    def test_priced_event_requires_payment(self):
        free_events = [
            _create_event(BASE_MONDAY + timedelta(days=i), self.group) for i in range(2)
        ]
        priced_event = _create_event(
            BASE_MONDAY + timedelta(days=2), self.group, is_priced=True
        )
        for event in free_events:
            _register(self.user, event, presence=PRESENCE_CHOICES.PRESENT)
        _register(self.user, priced_event, presence=PRESENCE_CHOICES.PRESENT)

        self.assertFalse(check_perfect_week(self.user, weeks=1))

        Registration.objects.filter(event=priced_event, user=self.user).update(
            payment_status=PAYMENT_SUCCESS
        )
        self.assertTrue(check_perfect_week(self.user, weeks=1))

    def test_two_week_window_requires_both_weeks_independently(self):
        self._fill_week(BASE_MONDAY, 3)
        self._fill_week(BASE_MONDAY + timedelta(weeks=1), 2)  # second week falls short

        self.assertTrue(check_perfect_week(self.user, weeks=1))
        self.assertFalse(check_perfect_week(self.user, weeks=2))

    def test_two_week_window_qualifies(self):
        self._fill_week(BASE_MONDAY, 3)
        self._fill_week(BASE_MONDAY + timedelta(weeks=1), 3)

        self.assertTrue(check_perfect_week(self.user, weeks=2))

    def test_promotion_grants_level_1_when_both_weeks_qualify(self):
        # check_leveled_promotions keeps a single row per (user, identifier)
        # and bumps its level in place, so satisfying weeks=2 straight away
        # should leave one row sitting at level 1, not separate rows per level.
        self._fill_week(BASE_MONDAY, 3)
        self._fill_week(BASE_MONDAY + timedelta(weeks=1), 3)

        check_perfect_week_related_single_user(self.user)

        achievement = Achievement.objects.get(
            user=self.user, identifier=PERFECT_WEEK_IDENTIFIER
        )
        self.assertEqual(achievement.level, 1)

    def test_promotion_grants_only_level_0_when_second_week_falls_short(self):
        self._fill_week(BASE_MONDAY, 3)
        self._fill_week(BASE_MONDAY + timedelta(weeks=1), 2)

        check_perfect_week_related_single_user(self.user)

        achievement = Achievement.objects.get(
            user=self.user, identifier=PERFECT_WEEK_IDENTIFIER
        )
        self.assertEqual(achievement.level, 0)
