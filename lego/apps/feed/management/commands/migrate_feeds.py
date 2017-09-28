import logging
import os

from cassandra.cqlengine.management import create_keyspace_simple, sync_table
from cassandra.cqlengine.query import BatchQuery
from stream_framework import settings

from lego.apps.feed.feeds.company_feed import CompanyFeed
from lego.apps.feed.feeds.group_feed import GroupFeed
from lego.apps.feed.feeds.notification_feed import NotificationFeed
from lego.apps.feed.feeds.personal_feed import PersonalFeed
from lego.apps.feed.feeds.user_feed import UserFeed
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
            PersonalFeed.get_timeline_storage().model,
            NotificationFeed.get_timeline_storage().model,
            CompanyFeed.get_timeline_storage().model,
            GroupFeed.get_timeline_storage().model
        ]

    def setup(self):
        log.info('Creating Cassandra keyspaces and syncing tables...')

        os.environ['CQLENG_ALLOW_SCHEMA_MANAGEMENT'] = '1'

        create_keyspace_simple(
            settings.STREAM_DEFAULT_KEYSPACE,
            settings.STREAM_CASSANDRA_CONSISTENCY_LEVEL
        )

        # Create a table for all feeds
        for model in self.get_cassandra_models():
            sync_table(model)

        log.info('Done!')

    def truncate_models(self):
        log.info('Purging data from all tables...')

        for model in self.get_cassandra_models():
            b = BatchQuery()

            for instance in model.objects.all():
                instance.batch(b).delete()

            b.execute()

        log.info('Done!')
