import logging

from lego.apps.search.backends.elasticsearch import backend as elasticsearch_backend
from lego.apps.search.registry import index_registry
from lego.utils.management_command import BaseCommand

log = logging.getLogger(__name__)


class Command(BaseCommand):

    help = 'Rebuild all indexes in Elasticsearch.'

    def run(self, *args, **options):
        log.info('Rebuilding indexes')
        elasticsearch_backend.clear()
        log.info('Cleared all indexes')
        for index in index_registry.values():
            log.info('Rebuilding index {index}'.format(index=index))
            index.update()
        log.info('Done!')
