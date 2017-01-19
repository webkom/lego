import logging

from lego.apps.search import backend
from lego.utils.management_command import BaseCommand

log = logging.getLogger(__name__)


class Command(BaseCommand):

    help = 'Migrate the configured search backend.'

    def run(self, *args, **options):
        log.info('Migrating the search backend')
        search_backend = backend.current_backend
        log.info(f'Using the {search_backend.name} backend...')
        search_backend.migrate()
        log.info('Done!')
