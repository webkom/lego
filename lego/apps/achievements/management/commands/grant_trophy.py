from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from lego.apps.achievements.constants import MANUAL_ACHIEVEMENTS
from lego.apps.achievements.models import Achievement


class Command(BaseCommand):
    help = "Grant a manual trophy to one or more users."

    def add_arguments(self, parser):
        parser.add_argument(
            "trophy",
            nargs="?",
            choices=sorted(MANUAL_ACHIEVEMENTS),
            help=("Manual trophy key, for example 'easter_2026_winner'."),
        )
        parser.add_argument(
            "usernames",
            nargs="*",
            help="One or more usernames to grant the trophy to.",
        )
        parser.add_argument(
            "--list",
            action="store_true",
            help="List available manual trophies and exit.",
        )
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Show what would change without writing to the database.",
        )
        parser.add_argument(
            "--yes",
            action="store_true",
            help="Skip the confirmation prompt.",
        )

    def handle(self, *args, **options):
        if options["list"]:
            self._print_available_trophies()
            return

        trophy_key = options["trophy"]
        if not trophy_key:
            raise CommandError("Trophy key is required unless --list is used.")

        usernames = list(dict.fromkeys(options["usernames"]))
        if not usernames:
            raise CommandError("Provide at least one username.")

        trophy = MANUAL_ACHIEVEMENTS[trophy_key]
        identifier = trophy["identifier"]
        level = trophy["level"]
        dry_run = options["dry_run"]
        assume_yes = options["yes"]

        User = get_user_model()
        users_by_username = User.objects.in_bulk(usernames, field_name="username")
        missing_usernames = [
            username for username in usernames if username not in users_by_username
        ]
        if missing_usernames:
            missing = ", ".join(f'"{username}"' for username in missing_usernames)
            raise CommandError(f"Unknown username(s): {missing}.")

        users = [users_by_username[username] for username in usernames]
        if (
            not dry_run
            and not assume_yes
            and not self._confirm_grant(trophy_key, users)
        ):
            self.stdout.write("Aborted.")
            return

        results = []
        with transaction.atomic():
            for user in users:
                username = user.username
                achievements = list(
                    Achievement.all_objects.select_for_update().filter(
                        user=user,
                        identifier=identifier,
                    )
                )

                if len(achievements) > 1:
                    raise CommandError(
                        f'User "{username}" has multiple "{identifier}" achievements. '
                        "Clean that up before using this command."
                    )

                current_achievement = achievements[0] if achievements else None
                if current_achievement is None:
                    action = "create"
                    if not dry_run:
                        Achievement.objects.create(
                            user=user,
                            identifier=identifier,
                            level=level,
                        )
                else:
                    update_fields = []
                    if current_achievement.deleted:
                        current_achievement.deleted = False
                        update_fields.append("deleted")
                    if current_achievement.level != level:
                        current_achievement.level = level
                        update_fields.append("level")

                    if update_fields:
                        action = "update"
                    else:
                        action = "unchanged"

                    if update_fields and not dry_run:
                        current_achievement.save(update_fields=update_fields)

                results.append((username, action))

        prefix = "Would " if dry_run else ""
        for username, action in results:
            if action == "unchanged":
                self.stdout.write(
                    f'{prefix}leave trophy "{trophy_key}" unchanged for "{username}".'
                )
            else:
                self.stdout.write(
                    self.style.SUCCESS(
                        f'{prefix}{action} trophy "{trophy_key}" for "{username}".'
                    )
                )

    def _print_available_trophies(self):
        self.stdout.write("Available manual trophies:")
        for trophy_key in sorted(MANUAL_ACHIEVEMENTS):
            trophy = MANUAL_ACHIEVEMENTS[trophy_key]
            self.stdout.write(
                f"- {trophy_key}: "
                f'identifier="{trophy["identifier"]}", level={trophy["level"]}'
            )

    def _confirm_grant(self, trophy_key, users):
        self.stdout.write(f'Grant trophy "{trophy_key}" to:')
        for user in users:
            full_name = user.get_full_name() or "(no full name)"
            self.stdout.write(f"- {user.username} ({full_name})")

        response = input("Continue? [y/N]: ").strip().lower()
        return response in {"y", "yes"}
