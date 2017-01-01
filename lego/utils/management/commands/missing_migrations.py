import logging
import sys

from django.apps import apps
from django.conf import settings
from django.db import connections
from django.db.migrations.autodetector import MigrationAutodetector
from django.db.migrations.executor import MigrationExecutor
from django.db.migrations.state import ProjectState
from django.db.utils import OperationalError

from lego.utils.management_command import BaseCommand

log = logging.getLogger(__name__)


class Command(BaseCommand):
    """
    Detect if any apps have missing migration files

    (not necessaily applied though)
    """
    help = 'Detect if any apps have missing migration files'

    def run(self, *args, **kwargs):

        changed = set()

        log.info('Checking DB migrations')
        for db in settings.DATABASES.keys():

            try:
                executor = MigrationExecutor(connections[db])
            except OperationalError:
                log.critical('Unable to check migrations, cannot connect to database')
                sys.exit(1)

            autodetector = MigrationAutodetector(
                executor.loader.project_state(),
                ProjectState.from_apps(apps),
            )

            changed.update(autodetector.changes(graph=executor.loader.graph).keys())

        if changed:
            log.critical(
                'Apps with model changes but no corresponding '
                f'migration file: {list(changed)}'
            )
            sys.exit(1)
        else:
            log.info('All migration files present')
