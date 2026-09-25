"""
Real multi-threaded, multi-connection tests for Registration.add_to_pool's
select_for_update() gate -- needs BaseAPITransactionTestCase since a plain
TestCase's single wrapping transaction wouldn't exercise real locking.
"""

from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import timedelta

from django.db import connections
from django.utils import timezone

from lego.apps.events import constants
from lego.apps.events.models import Event, Pool, Registration
from lego.apps.events.tests.utils import get_dummy_users
from lego.apps.users.models import AbakusGroup
from lego.utils.test_utils import BaseAPITransactionTestCase


def _register(event_id: int, user_id: int) -> None:
    """Runs in its own thread/connection: the full register() path."""
    try:
        event = Event.objects.get(pk=event_id)
        registration = Registration.objects.get_or_create(event=event, user_id=user_id)[
            0
        ]
        event.register(registration)
    finally:
        connections.close_all()


def _unregister(event_id: int, user_id: int) -> None:
    """Runs in its own thread/connection: the full unregister() path."""
    try:
        event = Event.objects.get(pk=event_id)
        registration = Registration.objects.get(event=event, user_id=user_id)
        event.unregister(registration)
    finally:
        connections.close_all()


def _run_burst(event_id: int, users: list) -> None:
    """Adds each user to Abakus, then fires a concurrent registration burst."""
    abakus = AbakusGroup.objects.get(name="Abakus")
    for user in users:
        abakus.add_user(user)
    connections.close_all()

    with ThreadPoolExecutor(max_workers=40) as ex:
        futures = [ex.submit(_register, event_id, u.id) for u in users]
        for f in as_completed(futures):
            f.result()  # re-raise any worker exception


class ConcurrentRegistrationBurstTestCase(BaseAPITransactionTestCase):
    """Big-load tests: many more registration attempts than capacity,
    fired at the same pool at once."""

    fixtures = [
        "test_abakus_groups.yaml",
        "test_users.yaml",
        "test_events.yaml",
        "test_companies.yaml",
    ]

    def test_large_single_pool_burst_never_oversells(self):
        """300 concurrent registrants racing a single pool with capacity 50
        -- exactly 50 must end up admitted, the rest waiting, and the pool
        must never be observed over capacity."""
        event = Event.objects.get(title="POOLS_NO_REGISTRATIONS")
        event.start_time = timezone.now() + timedelta(days=1)
        event.merge_time = None
        event.save()

        pool = event.pools.get(name="Abakusmember")
        pool.activation_date = timezone.now() - timedelta(days=1)
        pool.capacity = 50
        pool.save()
        # The fixture's other pool ("Webkom") is left in place -- none of these users
        # belong to that group, so get_possible_pools() never routes them there.

        users = get_dummy_users(300)
        _run_burst(event.id, users)

        pool.refresh_from_db()
        self.assertLessEqual(pool.registrations.count(), pool.capacity)
        self.assertEqual(pool.registrations.count(), 50)
        self.assertEqual(event.waiting_registrations.count(), 250)
        self.assertEqual(
            Registration.objects.filter(
                event=event, status=constants.SUCCESS_REGISTER
            ).count(),
            300,
        )

    def test_large_merged_event_burst_never_oversells(self):
        """Same burst, but against an already-merged event with two pools
        (total capacity 30) -- exercises the separate merged-path gate
        (Event.get_is_full under an event-level lock) rather than
        add_to_pool's per-pool gate."""
        event = Event.objects.get(title="POOLS_NO_REGISTRATIONS")
        event.start_time = timezone.now() + timedelta(days=1)
        event.merge_time = timezone.now() - timedelta(hours=1)
        event.save()

        pool_one = event.pools.get(name="Abakusmember")
        pool_one.activation_date = timezone.now() - timedelta(days=1)
        pool_one.capacity = 15
        pool_one.save()

        pool_two = event.pools.get(name="Webkom")
        pool_two.activation_date = timezone.now() - timedelta(days=1)
        pool_two.capacity = 15
        pool_two.save()

        users = get_dummy_users(200)
        _run_burst(event.id, users)

        total_admitted = pool_one.registrations.count() + pool_two.registrations.count()
        self.assertLessEqual(total_admitted, 30)
        self.assertEqual(total_admitted, 30)
        self.assertEqual(event.waiting_registrations.count(), 170)


class ConcurrentRegisterAndUnregisterTestCase(BaseAPITransactionTestCase):
    """People unregistering at the exact moment others register -- asserts
    the pool is never observed over capacity and every attempt lands somewhere."""

    fixtures = [
        "test_abakus_groups.yaml",
        "test_users.yaml",
        "test_events.yaml",
        "test_companies.yaml",
    ]

    def _setup_event(self, capacity: int) -> tuple[Event, Pool]:
        event = Event.objects.get(title="POOLS_NO_REGISTRATIONS")
        event.start_time = timezone.now() + timedelta(days=1)
        event.merge_time = None
        event.save()

        pool = event.pools.get(name="Abakusmember")
        pool.activation_date = timezone.now() - timedelta(days=1)
        pool.capacity = capacity
        pool.save()
        # The fixture's other pool ("Webkom") is left in place -- none of these users
        # belong to that group, so get_possible_pools() never routes them there.
        return event, pool

    def test_small_concurrent_register_and_unregister_race(self):
        """5 incumbents unregister at the same moment 15 new challengers
        race for the pool -- more challengers than freed slots, on purpose."""
        event, pool = self._setup_event(capacity=5)

        all_users = get_dummy_users(20)
        incumbents, challengers = all_users[:5], all_users[5:]
        abakus = AbakusGroup.objects.get(name="Abakus")
        for user in incumbents + challengers:
            abakus.add_user(user)

        for user in incumbents:
            registration = Registration.objects.get_or_create(event=event, user=user)[0]
            event.register(registration)
        pool.refresh_from_db()
        self.assertEqual(pool.registrations.count(), 5)
        connections.close_all()

        with ThreadPoolExecutor(max_workers=20) as ex:
            futures = [ex.submit(_unregister, event.id, u.id) for u in incumbents]
            futures += [ex.submit(_register, event.id, u.id) for u in challengers]
            for f in as_completed(futures):
                f.result()

        pool.refresh_from_db()
        self.assertLessEqual(pool.registrations.count(), pool.capacity)

        challenger_regs = Registration.objects.filter(event=event, user__in=challengers)
        admitted = challenger_regs.filter(pool__isnull=False).count()
        waiting = challenger_regs.filter(
            pool__isnull=True, status=constants.SUCCESS_REGISTER
        ).count()
        self.assertEqual(admitted + waiting, 15)

        for user in incumbents:
            reg = Registration.objects.get(event=event, user=user)
            self.assertIsNone(reg.pool)
            self.assertEqual(reg.status, constants.SUCCESS_UNREGISTER)

    def test_large_concurrent_register_and_unregister_race(self):
        """Bigger version: pool starts full at capacity 100; 40 incumbents
        unregister while 150 challengers race concurrently for the same
        pool row. Same invariant, higher contention."""
        event, pool = self._setup_event(capacity=100)

        all_users = get_dummy_users(250)
        incumbents, challengers = all_users[:100], all_users[100:]
        abakus = AbakusGroup.objects.get(name="Abakus")
        for user in incumbents + challengers:
            abakus.add_user(user)

        for user in incumbents:
            registration = Registration.objects.get_or_create(event=event, user=user)[0]
            event.register(registration)
        pool.refresh_from_db()
        self.assertEqual(pool.registrations.count(), 100)
        connections.close_all()

        unregistering, staying = incumbents[:40], incumbents[40:]

        with ThreadPoolExecutor(max_workers=60) as ex:
            futures = [ex.submit(_unregister, event.id, u.id) for u in unregistering]
            futures += [ex.submit(_register, event.id, u.id) for u in challengers]
            for f in as_completed(futures):
                f.result()

        pool.refresh_from_db()
        self.assertLessEqual(pool.registrations.count(), pool.capacity)

        for user in staying:
            reg = Registration.objects.get(event=event, user=user)
            self.assertIsNotNone(reg.pool)

        challenger_regs = Registration.objects.filter(event=event, user__in=challengers)
        admitted = challenger_regs.filter(pool__isnull=False).count()
        waiting = challenger_regs.filter(
            pool__isnull=True, status=constants.SUCCESS_REGISTER
        ).count()
        self.assertEqual(admitted + waiting, 150)
