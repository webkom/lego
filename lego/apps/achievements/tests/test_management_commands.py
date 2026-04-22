from io import StringIO
from unittest.mock import patch

from django.core.management import call_command
from django.core.management.base import CommandError

from lego.apps.achievements.constants import (
    CHRISTMAS_CALENDAR_IDENTIFIER,
    EASTER_2025_IDENTIFIER,
    EASTER_2026_IDENTIFIER,
)
from lego.apps.achievements.models import Achievement
from lego.apps.users.models import User
from lego.utils.test_utils import BaseTestCase


class GrantTrophyCommandTestCase(BaseTestCase):
    fixtures = ["test_users.yaml"]

    def test_grant_trophy_creates_manual_achievement(self):
        user = User.objects.get(username="test1")

        with patch("builtins.input", return_value="y"):
            call_command("grant_trophy", "easter_2026_winner", "test1")

        self.assertTrue(
            Achievement.objects.filter(
                user=user,
                identifier=EASTER_2026_IDENTIFIER,
                level=2,
            ).exists()
        )

    def test_grant_trophy_updates_existing_manual_achievement(self):
        user = User.objects.get(username="test1")
        Achievement.objects.create(
            user=user, identifier=EASTER_2026_IDENTIFIER, level=0
        )

        with patch("builtins.input", return_value="y"):
            call_command("grant_trophy", "easter_2026_winner", "test1")

        self.assertEqual(
            Achievement.objects.filter(
                user=user,
                identifier=EASTER_2026_IDENTIFIER,
            ).count(),
            1,
        )
        self.assertTrue(
            Achievement.objects.filter(
                user=user,
                identifier=EASTER_2026_IDENTIFIER,
                level=2,
            ).exists()
        )

    def test_grant_trophy_keeps_easter_trophies_from_other_years(self):
        user = User.objects.get(username="test1")
        Achievement.objects.create(
            user=user, identifier=EASTER_2025_IDENTIFIER, level=1
        )

        with patch("builtins.input", return_value="y"):
            call_command("grant_trophy", "easter_2026_winner", "test1")

        self.assertTrue(
            Achievement.objects.filter(
                user=user,
                identifier=EASTER_2025_IDENTIFIER,
                level=1,
            ).exists()
        )
        self.assertTrue(
            Achievement.objects.filter(
                user=user,
                identifier=EASTER_2026_IDENTIFIER,
                level=2,
            ).exists()
        )

    def test_grant_trophy_accepts_level_zero_trophies(self):
        user = User.objects.get(username="test1")

        with patch("builtins.input", return_value="y"):
            call_command("grant_trophy", "christmas_2025", "test1")

        self.assertTrue(
            Achievement.objects.filter(
                user=user,
                identifier=CHRISTMAS_CALENDAR_IDENTIFIER,
                level=0,
            ).exists()
        )

    def test_grant_trophy_grants_to_multiple_users(self):
        with patch("builtins.input", return_value="y"):
            call_command("grant_trophy", "christmas_2025", "test1", "test2")

        self.assertEqual(
            Achievement.objects.filter(
                identifier=CHRISTMAS_CALENDAR_IDENTIFIER,
                level=0,
                user__username__in=["test1", "test2"],
            ).count(),
            2,
        )

    def test_grant_trophy_lists_available_manual_trophies(self):
        stdout = StringIO()

        call_command("grant_trophy", "--list", stdout=stdout)

        output = stdout.getvalue()
        self.assertIn("Available manual trophies:", output)
        self.assertIn("easter_2026_winner", output)
        self.assertIn("christmas_2025", output)

    def test_grant_trophy_errors_for_unknown_user(self):
        with self.assertRaises(CommandError):
            call_command("grant_trophy", "christmas_2025", "missing-user")

    def test_grant_trophy_aborts_when_confirmation_is_rejected(self):
        stdout = StringIO()

        with patch("builtins.input", return_value="n"):
            call_command("grant_trophy", "christmas_2025", "test1", stdout=stdout)

        self.assertFalse(
            Achievement.objects.filter(
                identifier=CHRISTMAS_CALENDAR_IDENTIFIER,
                user__username="test1",
            ).exists()
        )
        self.assertIn("Aborted.", stdout.getvalue())

    def test_grant_trophy_prompt_shows_full_name(self):
        stdout = StringIO()

        with patch("builtins.input", return_value="n"):
            call_command("grant_trophy", "christmas_2025", "test1", stdout=stdout)

        output = stdout.getvalue()
        self.assertIn('Grant trophy "christmas_2025" to:', output)
        self.assertIn("- test1 (test user1)", output)

    def test_grant_trophy_yes_skips_confirmation_prompt(self):
        with patch("builtins.input", side_effect=AssertionError("prompted")):
            call_command("grant_trophy", "--yes", "christmas_2025", "test1")

        self.assertTrue(
            Achievement.objects.filter(
                identifier=CHRISTMAS_CALENDAR_IDENTIFIER,
                level=0,
                user__username="test1",
            ).exists()
        )

    def test_grant_trophy_dry_run_does_not_write(self):
        stdout = StringIO()

        call_command(
            "grant_trophy",
            "--dry-run",
            "christmas_2025",
            "test1",
            stdout=stdout,
        )

        self.assertFalse(
            Achievement.objects.filter(
                identifier=CHRISTMAS_CALENDAR_IDENTIFIER,
                level=0,
                user__username="test1",
            ).exists()
        )
        self.assertIn(
            'Would create trophy "christmas_2025" for "test1".',
            stdout.getvalue(),
        )

    def test_grant_trophy_restores_soft_deleted_achievement(self):
        user = User.objects.get(username="test1")
        achievement = Achievement.objects.create(
            user=user,
            identifier=EASTER_2026_IDENTIFIER,
            level=0,
        )
        achievement.delete()

        with patch("builtins.input", return_value="y"):
            call_command("grant_trophy", "easter_2026_winner", "test1")

        achievement.refresh_from_db()
        self.assertFalse(achievement.deleted)
        self.assertEqual(achievement.level, 2)
        self.assertEqual(
            Achievement.all_objects.filter(
                user=user,
                identifier=EASTER_2026_IDENTIFIER,
            ).count(),
            1,
        )
