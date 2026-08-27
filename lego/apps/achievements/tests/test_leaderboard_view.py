from datetime import timedelta

from django.urls import reverse
from django.utils import timezone

from lego.apps.achievements.constants import (
    EVENT_IDENTIFIER,
    QUOTE_IDENTIFIER,
    RankType,
)
from lego.apps.achievements.models import Achievement, RankSnapshot
from lego.apps.achievements.ranking import snapshot_rank_type
from lego.apps.events.models import Event, Registration
from lego.apps.events.tests.utils import get_dummy_users
from lego.utils.test_utils import BaseAPITestCase


def _leaderboard_url():
    return reverse("api:v1:achievements-list")


def _give_achievement(user, identifier, level):
    Achievement.objects.create(user=user, identifier=identifier, level=level)


def _register_for_n_events(user, n):
    for i in range(n):
        event = Event.objects.create(
            title=f"event-{user.id}-{i}",
            start_time=timezone.now() - timedelta(days=10),
            end_time=timezone.now() - timedelta(days=9),
        )
        Registration.objects.create(event=event, user=user)


class LeaderBoardEventCountTestCase(BaseAPITestCase):
    fixtures = ["test_abakus_groups.yaml"]

    def setUp(self):
        self.users = get_dummy_users(3)
        self.client.force_authenticate(self.users[0])

    def _get(self, **params):
        return self.client.get(_leaderboard_url(), params)

    def test_event_count_type_excludes_users_with_no_registrations(self):
        _register_for_n_events(self.users[0], 3)
        _register_for_n_events(self.users[1], 1)
        # users[2] has no registrations at all

        res = self._get(type=RankType.EVENT_COUNT)

        self.assertEqual(res.status_code, 200)
        returned_ids = {row["id"] for row in res.data["results"]}
        self.assertIn(self.users[0].id, returned_ids)
        self.assertIn(self.users[1].id, returned_ids)
        self.assertNotIn(self.users[2].id, returned_ids)

    def test_event_count_type_computes_rank_from_registration_count(self):
        _register_for_n_events(self.users[0], 1)
        _register_for_n_events(self.users[1], 10)
        _register_for_n_events(self.users[2], 5)

        res = self._get(type=RankType.EVENT_COUNT)

        by_id = {row["id"]: row for row in res.data["results"]}
        self.assertEqual(by_id[self.users[1].id]["achievement_rank"], 1)
        self.assertEqual(by_id[self.users[2].id]["achievement_rank"], 2)
        self.assertEqual(by_id[self.users[0].id]["achievement_rank"], 3)

    def test_event_count_field_is_null_until_a_snapshot_has_been_taken(self):
        _register_for_n_events(self.users[0], 4)

        res = self._get(type=RankType.EVENT_COUNT)

        by_id = {row["id"]: row for row in res.data["results"]}
        self.assertIsNone(by_id[self.users[0].id]["event_count"])

    def test_event_count_field_reflects_the_latest_snapshot_value(self):
        _register_for_n_events(self.users[0], 4)
        snapshot_rank_type(RankType.EVENT_COUNT)

        res = self._get(type=RankType.EVENT_COUNT)

        by_id = {row["id"]: row for row in res.data["results"]}
        self.assertEqual(by_id[self.users[0].id]["event_count"], 4)

    def test_invalid_type_falls_back_to_achievement_score(self):
        _give_achievement(self.users[1], QUOTE_IDENTIFIER, 0)
        _register_for_n_events(self.users[2], 5)  # no achievements -> excluded

        res = self._get(type="not_a_real_rank_type")

        returned_ids = {row["id"] for row in res.data["results"]}
        self.assertIn(self.users[1].id, returned_ids)
        self.assertNotIn(self.users[2].id, returned_ids)

    def test_default_type_ranks_by_achievement_score(self):
        _give_achievement(self.users[0], QUOTE_IDENTIFIER, 0)  # score 2
        _give_achievement(self.users[1], EVENT_IDENTIFIER, 5)  # score 7.5

        res = self._get()

        by_id = {row["id"]: row for row in res.data["results"]}
        self.assertNotIn(self.users[2].id, by_id)
        self.assertEqual(by_id[self.users[1].id]["achievement_rank"], 1)
        self.assertEqual(by_id[self.users[0].id]["achievement_rank"], 2)


class LeaderBoardRankHistoryTestCase(BaseAPITestCase):
    fixtures = ["test_abakus_groups.yaml"]

    def setUp(self):
        self.users = get_dummy_users(1)
        self.user = self.users[0]
        self.client.force_authenticate(self.user)

    def _get(self, **params):
        return self.client.get(_leaderboard_url(), params)

    def test_rank_week_and_month_ago_use_the_most_recent_snapshot_within_range(self):
        _register_for_n_events(self.user, 1)
        today = timezone.now().date()

        RankSnapshot.objects.create(
            user=self.user,
            type=RankType.EVENT_COUNT,
            rank=5,
            value=1,
            date=today - timedelta(days=40),
        )
        RankSnapshot.objects.create(
            user=self.user,
            type=RankType.EVENT_COUNT,
            rank=3,
            value=1,
            date=today - timedelta(days=20),
        )
        RankSnapshot.objects.create(
            user=self.user,
            type=RankType.EVENT_COUNT,
            rank=1,
            value=1,
            date=today - timedelta(days=3),
        )

        res = self._get(type=RankType.EVENT_COUNT)

        row = next(r for r in res.data["results"] if r["id"] == self.user.id)
        # week_ago cutoff (today-7) only reaches back to the 20-days-old snapshot.
        self.assertEqual(row["rank_week_ago"], 3)
        # month_ago cutoff (today-30) only reaches back to the 40-days-old snapshot.
        self.assertEqual(row["rank_month_ago"], 5)

    def test_rank_week_and_month_ago_are_null_without_snapshots(self):
        _register_for_n_events(self.user, 1)

        res = self._get(type=RankType.EVENT_COUNT)

        row = next(r for r in res.data["results"] if r["id"] == self.user.id)
        self.assertIsNone(row["rank_week_ago"])
        self.assertIsNone(row["rank_month_ago"])
