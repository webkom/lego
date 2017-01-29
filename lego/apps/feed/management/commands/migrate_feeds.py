import logging

from cassandra.cqlengine.management import create_keyspace_simple, drop_keyspace, sync_table
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
        self.setup()

    def get_cassandra_models(self):
        return [
            UserFeed.get_timeline_storage().model,
            NotificationFeed.get_timeline_storage().model
        ]

    def setup(self):
        log.info('Creating Cassandra keyspaces and syncing tables...')

        create_keyspace_simple(
            settings.STREAM_DEFAULT_KEYSPACE,
            settings.STREAM_CASSANDRA_CONSISTENCY_LEVEL
        )

        # Create a table for all feeds
        for model in self.get_cassandra_models():
            sync_table(model)

        log.info('Done!')

    def teardown(self):
        log.info('Dropping Cassandra keyspaces and dropping tables...')

        drop_keyspace(
            settings.STREAM_DEFAULT_KEYSPACE
        )

        log.info('Done!')
