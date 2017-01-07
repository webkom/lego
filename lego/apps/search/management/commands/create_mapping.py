import logging

from lego.apps.search.backends.elasticsearch import backend as elasticsearch_backend
from lego.utils.management_command import BaseCommand

log = logging.getLogger(__name__)


class Command(BaseCommand):

    help = 'Upload the index-template to Elasticsearch.'

    def run(self, *args, **options):
        log.info('Creating ES index template')
        elasticsearch_backend.create_template()
        log.info('Done!')
