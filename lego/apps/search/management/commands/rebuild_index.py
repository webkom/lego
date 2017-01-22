import logging

from lego.apps.search import backend
from lego.apps.search.registry import index_registry
from lego.utils.management_command import BaseCommand

log = logging.getLogger(__name__)


class Command(BaseCommand):

    help = 'Rebuild all search indexes.'

    def run(self, *args, **options):
        log.info('Rebuilding indexes')
        search_backend = backend.current_backend
        log.info(f'Using the {search_backend.name} backend...')
        log.info('Clearing indexes')
        search_backend.clear()
        log.info('Cleared all indexes')
        for content_type, index in index_registry.items():
            log.info(f'Rebuilding the {content_type} index')
            index.update()
        log.info('Done!')
