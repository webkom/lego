import logging

from cassandra.cqlengine.management import create_keyspace_simple, sync_table
from stream_framework import settings

from lego.apps.feed.feeds.notification.feed import NotificationFeed
from lego.apps.feed.feeds.user.feed import UserFeed
from lego.utils.management_command import BaseCommand

log = logging.getLogger(__name__)


class Command(BaseCommand):

    help = 'Create Cassandra keyspace and sync tables'

    def run(self, *args, **options):
        """
        Migrate the cassandra database after the postgres migration.
        This function creates the tablespace and tables.
        """
        log.info('Creating Cassandra keyspaces and syncing tables...')

        create_keyspace_simple(
            settings.STREAM_DEFAULT_KEYSPACE,
            settings.STREAM_CASSANDRA_CONSISTENCY_LEVEL
        )

        # Create a table for all feeds
        sync_table(UserFeed.get_timeline_storage().model)
        sync_table(NotificationFeed.get_timeline_storage().model)

        log.info('Done!')
