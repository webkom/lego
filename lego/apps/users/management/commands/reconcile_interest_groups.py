from typing import Any

from django.core.management.base import BaseCommand, CommandParser

from lego.apps.users import constants
from lego.apps.users.models import AbakusGroup


class Command(BaseCommand):
    help = "Promote a co-leader or deactivate active interest groups without a leader."

    def add_arguments(self, parser: CommandParser) -> None:
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Show what would change without writing to the database.",
        )

    def handle(self, *args: Any, **options: Any) -> None:
        dry_run = options["dry_run"]
        prefix = "Would " if dry_run else ""

        groups = AbakusGroup.objects.filter(
            type=constants.GROUP_INTEREST, active=True
        ).order_by("name")
        for group in groups:
            action = group.reconcile_leadership(dry_run=dry_run)
            if action:
                self.stdout.write(
                    self.style.SUCCESS(f'{prefix}{action} in "{group.name}".')
                )
