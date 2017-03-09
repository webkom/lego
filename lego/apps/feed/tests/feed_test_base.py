from django.test import TestCase

from lego.apps.feed.management.commands.migrate_feeds import Command as MigrateCommand


class FeedTestBase(TestCase):
    @classmethod
    def setUpClass(cls):
        super(FeedTestBase, cls).setUpClass()
        try:
            MigrateCommand().teardown()
        except:
            pass

    def _pre_setup(self):
        super(FeedTestBase, self)._pre_setup()
        MigrateCommand().setup()

    def _post_teardown(self):
        super(FeedTestBase, self)._post_teardown()
        MigrateCommand().teardown()

    '''
    Helper functions for aggregated feeds
    '''
    def activity_count(self, feed):
        count = 0
        for aggregated in feed[:]:
            count += len(aggregated)
        return count

    def all_activities(self, feed):
        activities = set()
        for aggregated in feed[:]:
            activities = activities.union(aggregated.activities)
        return list(activities)
