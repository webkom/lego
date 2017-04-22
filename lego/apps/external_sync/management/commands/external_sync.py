import logging

from lego.apps.external_sync.sync import Sync
from lego.utils.management_command import BaseCommand

log = logging.getLogger(__name__)


class Command(BaseCommand):

    help = 'Sync users and groups to external systems.'

    def run(self, *args, **options):
        log.info('Syncing users and groups to external systems...')
        sync = Sync()
        sync.sync()
        log.info('Done!')
