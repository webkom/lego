from django.urls import reverse

from lego.apps.achievements.constants import EVENT_IDENTIFIER, QUOTE_IDENTIFIER
from lego.apps.achievements.models import Achievement
from lego.apps.achievements.utils.calculation_utils import ACHIEVEMENT_RARITIES
from lego.apps.events.tests.utils import get_dummy_users
from lego.utils.test_utils import BaseAPITestCase


def _rarity_url():
    return reverse("api:v1:achievement-rarity")


def _give_achievement(user, identifier, level):
    Achievement.objects.create(user=user, identifier=identifier, level=level)


def _by_identifier_and_level(rows):
    return {(row["identifier"], row["level"]): row["percentage"] for row in rows}


class AchievementRarityTestCase(BaseAPITestCase):
    fixtures = ["test_abakus_groups.yaml"]

    def setUp(self):
        self.users = get_dummy_users(4)
        self.client.force_authenticate(self.users[0])

    def test_includes_every_defined_level_even_with_no_achievers(self):
        res = self.client.get(_rarity_url())

        self.assertEqual(res.status_code, 200)
        by_row = _by_identifier_and_level(res.data)
        for identifier, rarity_list in ACHIEVEMENT_RARITIES.items():
            for level in range(len(rarity_list)):
                self.assertEqual(by_row[(identifier, level)], 0.0)

    def test_percentage_is_cumulative_by_level(self):
        # QUOTE_IDENTIFIER only has a single defined level (0).
        _give_achievement(self.users[0], QUOTE_IDENTIFIER, 0)
        _give_achievement(self.users[1], QUOTE_IDENTIFIER, 0)
        # A single user promoted straight to level 2 of EVENT_IDENTIFIER - only
        # one row is ever stored per (user, identifier), see promotion.py.
        _give_achievement(self.users[2], EVENT_IDENTIFIER, 2)
        # users[3] has no achievements.

        res = self.client.get(_rarity_url())

        by_row = _by_identifier_and_level(res.data)
        self.assertEqual(by_row[(QUOTE_IDENTIFIER, 0)], 50.0)
        # The level-2 holder counts towards "at least level 0/1/2".
        self.assertEqual(by_row[(EVENT_IDENTIFIER, 0)], 25.0)
        self.assertEqual(by_row[(EVENT_IDENTIFIER, 1)], 25.0)
        self.assertEqual(by_row[(EVENT_IDENTIFIER, 2)], 25.0)
        # ...but nobody has reached level 3 yet.
        self.assertEqual(by_row[(EVENT_IDENTIFIER, 3)], 0.0)

    def test_matches_achievement_percentage_property(self):
        _give_achievement(self.users[0], EVENT_IDENTIFIER, 0)
        _give_achievement(self.users[1], EVENT_IDENTIFIER, 3)

        res = self.client.get(_rarity_url())

        by_row = _by_identifier_and_level(res.data)
        achievement = Achievement.objects.get(
            user=self.users[1], identifier=EVENT_IDENTIFIER
        )
        self.assertAlmostEqual(
            by_row[(EVENT_IDENTIFIER, achievement.level)],
            round(achievement.percentage, 2),
        )
