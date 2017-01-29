from django.test import TestCase

from lego.apps.feed.management.commands.migrate_feeds import Command as MigrateCommand


class FeedTestBase(TestCase):
    def _pre_setup(self):
        super(FeedTestBase, self)._pre_setup()
        MigrateCommand().setup()

    def _post_teardown(self):
        super(FeedTestBase, self)._post_teardown()
        MigrateCommand().teardown()
