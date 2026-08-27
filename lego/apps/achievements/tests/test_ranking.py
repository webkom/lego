from datetime import timedelta

from django.utils import timezone

from lego.apps.achievements.constants import (
    EVENT_IDENTIFIER,
    QUOTE_IDENTIFIER,
    RankType,
)
from lego.apps.achievements.models import Achievement, RankSnapshot
from lego.apps.achievements.ranking import snapshot_rank_type
from lego.apps.achievements.tasks import snapshot_leaderboard_ranks
from lego.apps.events.models import Event, Registration
from lego.apps.events.tests.utils import get_dummy_users
from lego.utils.test_utils import BaseTestCase


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


class SnapshotRankTypeTestCase(BaseTestCase):
    fixtures = ["test_abakus_groups.yaml"]

    def setUp(self):
        self.users = get_dummy_users(4)

    def test_snapshot_only_ranks_users_with_achievements(self):
        _give_achievement(self.users[1], QUOTE_IDENTIFIER, 0)  # score 2
        _give_achievement(self.users[2], EVENT_IDENTIFIER, 3)  # score 4.3
        _give_achievement(self.users[3], EVENT_IDENTIFIER, 5)  # score 7.5

        created = snapshot_rank_type(RankType.ACHIEVEMENT_SCORE)

        self.assertEqual(created, 3)
        rows = RankSnapshot.objects.filter(type=RankType.ACHIEVEMENT_SCORE)
        ranks = {row.user_id: row.rank for row in rows}
        self.assertEqual(ranks[self.users[3].id], 1)
        self.assertEqual(ranks[self.users[2].id], 2)
        self.assertEqual(ranks[self.users[1].id], 3)
        self.assertNotIn(self.users[0].id, ranks)

        values = {row.user_id: row.value for row in rows}
        self.assertAlmostEqual(values[self.users[3].id], 7.5)
        self.assertAlmostEqual(values[self.users[2].id], 4.3)
        self.assertAlmostEqual(values[self.users[1].id], 2.0)

        for row in rows:
            self.assertEqual(row.date, timezone.now().date())

    def test_snapshot_ranks_all_users_by_event_count_including_zero(self):
        _register_for_n_events(self.users[0], 1)
        _register_for_n_events(self.users[1], 5)
        _register_for_n_events(self.users[2], 3)
        # users[3] has no registrations at all

        created = snapshot_rank_type(RankType.EVENT_COUNT)

        rows = {
            row.user_id: (row.rank, row.value)
            for row in RankSnapshot.objects.filter(type=RankType.EVENT_COUNT)
        }
        self.assertEqual(created, len(self.users))
        self.assertEqual(rows[self.users[1].id], (1, 5))
        self.assertEqual(rows[self.users[2].id], (2, 3))
        self.assertEqual(rows[self.users[0].id], (3, 1))
        self.assertEqual(rows[self.users[3].id], (4, 0))

    def test_ties_share_rank_and_next_distinct_value_skips_ahead(self):
        _give_achievement(self.users[0], QUOTE_IDENTIFIER, 0)  # score 2 (tie)
        _give_achievement(self.users[1], QUOTE_IDENTIFIER, 0)  # score 2 (tie)
        _give_achievement(self.users[2], EVENT_IDENTIFIER, 3)  # score 4.3 (highest)

        snapshot_rank_type(RankType.ACHIEVEMENT_SCORE)

        ranks = {
            row.user_id: row.rank
            for row in RankSnapshot.objects.filter(type=RankType.ACHIEVEMENT_SCORE)
        }
        self.assertEqual(ranks[self.users[2].id], 1)
        self.assertEqual(ranks[self.users[0].id], 2)
        self.assertEqual(ranks[self.users[1].id], 2)

    def test_snapshot_deduplicates_users_with_multiple_achievements(self):
        _give_achievement(self.users[0], QUOTE_IDENTIFIER, 0)
        _give_achievement(self.users[0], EVENT_IDENTIFIER, 3)

        created = snapshot_rank_type(RankType.ACHIEVEMENT_SCORE)

        self.assertEqual(created, 1)
        rows = RankSnapshot.objects.filter(
            type=RankType.ACHIEVEMENT_SCORE, user=self.users[0]
        )
        self.assertEqual(rows.count(), 1)

    def test_unknown_rank_type_raises(self):
        with self.assertRaises(ValueError):
            snapshot_rank_type("not_a_real_type")

    def test_second_snapshot_only_writes_changed_ranks(self):
        _register_for_n_events(self.users[0], 5)  # rank 1
        _register_for_n_events(self.users[1], 2)  # rank 2

        first_created = snapshot_rank_type(RankType.EVENT_COUNT)
        self.assertEqual(first_created, len(self.users))

        # users[1] overtakes users[0]; ranks flip for both, others are untouched.
        _register_for_n_events(self.users[1], 10)
        second_created = snapshot_rank_type(RankType.EVENT_COUNT)

        rows = {
            row.user_id: row.rank
            for row in RankSnapshot.objects.filter(type=RankType.EVENT_COUNT)
        }
        self.assertEqual(rows[self.users[1].id], 1)
        self.assertEqual(rows[self.users[0].id], 2)
        self.assertEqual(second_created, 2)


class SnapshotLeaderboardRanksTaskTestCase(BaseTestCase):
    fixtures = ["test_abakus_groups.yaml"]

    def setUp(self):
        self.users = get_dummy_users(3)

    def test_task_snapshots_both_rank_types(self):
        _give_achievement(self.users[0], QUOTE_IDENTIFIER, 0)
        _register_for_n_events(self.users[1], 2)

        snapshot_leaderboard_ranks.apply()

        self.assertTrue(
            RankSnapshot.objects.filter(
                type=RankType.ACHIEVEMENT_SCORE, user=self.users[0]
            ).exists()
        )
        self.assertTrue(
            RankSnapshot.objects.filter(
                type=RankType.EVENT_COUNT, user=self.users[1]
            ).exists()
        )
