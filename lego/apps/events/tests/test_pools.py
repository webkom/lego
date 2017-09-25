from datetime import timedelta

from django.test import TestCase
from django.utils import timezone

from lego.apps.events.models import Event, Pool
from lego.apps.users.models import AbakusGroup


class PoolMethodTest(TestCase):
    fixtures = ['initial_files.yaml', 'test_abakus_groups.yaml', 'test_users.yaml',
                'test_companies.yaml', 'test_events.yaml']

    def setUp(self):
        event = Event.objects.get(title='POOLS_WITH_REGISTRATIONS')
        self.pool = event.pools.first()

    def test_str(self):
        self.assertEqual(str(self.pool), self.pool.name)

    def test_delete_pool_with_registrations(self):
        with self.assertRaises(ValueError):
            self.pool.delete()

    def test_delete_pool_without_registrations(self):
        event = Event.objects.get(title='POOLS_NO_REGISTRATIONS')
        pool = event.pools.first()
        number_of_pools = len(event.pools.all())
        pool.delete()
        self.assertEqual(len(event.pools.all()), number_of_pools - 1)


class PoolCapacityTestCase(TestCase):
    fixtures = ['initial_files.yaml', 'test_abakus_groups.yaml', 'test_users.yaml',
                'test_companies.yaml', 'test_events.yaml']

    def create_pools(self, event, capacities_to_add, permission_groups):
        for capacity in capacities_to_add:
            pool = Pool.objects.create(
                name='Abakus', capacity=capacity, event=event,
                activation_date=(timezone.now() - timedelta(hours=24)))
            pool.permission_groups = permission_groups

    def test_capacity_with_single_pool(self):
        event = Event.objects.get(title='NO_POOLS_ABAKUS')
        capacities_to_add = [10]
        self.create_pools(event, capacities_to_add, [AbakusGroup.objects.get(name='Abakus')])
        self.assertEqual(sum(capacities_to_add), event.active_capacity)

    def test_capacity_with_multiple_pools(self):
        event = Event.objects.get(title='NO_POOLS_ABAKUS')
        capacities_to_add = [10, 20]
        self.create_pools(event, capacities_to_add, [AbakusGroup.objects.get(name='Abakus')])
        self.assertEqual(sum(capacities_to_add), event.active_capacity)
