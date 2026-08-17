import logging

from django.core import management

from lego.utils.management_command import BaseCommand

log = logging.getLogger(__name__)


class Command(BaseCommand):
    verbosity = 0
    help = "Initializes the Django environment"

    def run(self, *args, **options):
        self.stdout.write("Migrating...")
        management.call_command("migrate", verbosity=self.verbosity)
        self.stdout.write("Loading fixtures...")
        management.call_command(
            "load_fixtures", verbosity=self.verbosity, development=True
        )
        self.stdout.write("All done!")
