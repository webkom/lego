from datetime import timedelta

from django.utils import timezone

from lego.apps.events.exceptions import EventNotReady
from lego.apps.events.models import Event, Pool, Registration
from lego.apps.followers.models import FollowEvent
from lego.apps.users.models import AbakusGroup, User
from lego.utils.test_utils import BaseTestCase

from .utils import get_dummy_users


class RegistrationMethodTest(BaseTestCase):
    fixtures = [
        "test_abakus_groups.yaml",
        "test_users.yaml",
        "test_companies.yaml",
        "test_events.yaml",
    ]

    def setUp(self):
        Event.objects.all().update(start_time=timezone.now() + timedelta(hours=3))
        self.event = Event.objects.get(title="POOLS_AND_PRICED")
        self.users = get_dummy_users(2)
        AbakusGroup.objects.get(name="Abakus").add_user(self.users[0])
        self.registration = Registration.objects.get_or_create(
            event=self.event, user=self.users[0]
        )[0]

    def test_str(self):
        d = {"user": self.registration.user, "pool": self.registration.pool}

        self.assertEqual(str(self.registration), str(d))

    def test_member_cost(self):
        self.registration = self.event.register(self.registration)
        self.assertEqual(self.event.get_price(self.registration.user), 10000)

    def test_user_cost(self):
        registration = Registration.objects.get_or_create(
            event=self.event, user=self.users[1]
        )[0]
        self.event.register(registration)
        self.assertEqual(self.event.get_price(registration.user), 15000)


class RegistrationTestCase(BaseTestCase):
    fixtures = [
        "test_abakus_groups.yaml",
        "test_users.yaml",
        "test_companies.yaml",
        "test_events.yaml",
    ]

    def setUp(self):
        Event.objects.all().update(
            start_time=timezone.now() + timedelta(hours=3),
            merge_time=timezone.now() + timedelta(hours=12),
            heed_penalties=True,
        )

    def test_can_register_single_unlimited_pool(self):
        """Test registering user to event with a single unlimited pool"""
        user = get_dummy_users(1)[0]
        event = Event.objects.get(title="POOLS_NO_REGISTRATIONS")
        pool = event.pools.first()
        pool.capacity = 0
        pool.save()
        AbakusGroup.objects.get(name="Abakus").add_user(user)

        registration = Registration.objects.get_or_create(event=event, user=user)[0]
        event.register(registration)
        self.assertIsNotNone(registration.pool)
        self.assertEqual(pool.registrations.count(), 1)

    def test_can_register_single_pool(self):
        """Test registering user to event with only a single pool"""
        user = get_dummy_users(1)[0]
        event = Event.objects.get(title="POOLS_NO_REGISTRATIONS")
        pool = event.pools.first()
        AbakusGroup.objects.get(name="Abakus").add_user(user)

        registration = Registration.objects.get_or_create(event=event, user=user)[0]
        event.register(registration)
        self.assertEqual(pool.registrations.count(), event.number_of_registrations)

    def test_can_reregister_single_pool(self):
        """Test reregistering user to event with only a single pool"""
        user = get_dummy_users(1)[0]
        event = Event.objects.get(title="POOLS_NO_REGISTRATIONS")
        pool = event.pools.first()
        AbakusGroup.objects.get(name="Abakus").add_user(user)

        registration = Registration.objects.get_or_create(event=event, user=user)[0]
        event.register(registration)
        self.assertEqual(pool.registrations.count(), event.number_of_registrations)

    def test_can_register_to_single_open_pool(self):
        """Test registering user to event with only one pool with spots left"""
        users = get_dummy_users(10)
        abakus_users = users[:6]
        webkom_users = users[6:]
        event = Event.objects.get(title="POOLS_NO_REGISTRATIONS")
        pool_one = event.pools.get(name="Abakusmember")
        pool_two = event.pools.get(name="Webkom")

        for user in abakus_users:
            AbakusGroup.objects.get(name="Abakus").add_user(user)
        for user in webkom_users:
            AbakusGroup.objects.get(name="Webkom").add_user(user)

        for user in webkom_users:
            registration = Registration.objects.get_or_create(event=event, user=user)[0]
            event.register(registration)

        self.assertEqual(pool_one.registrations.count(), 2)
        self.assertEqual(pool_two.registrations.count(), 2)
        self.assertEqual(event.number_of_registrations, 4)

    def test_can_register_with_automatic_pool_selection(self):
        """Test that registrating user selects correct pool and that user follows the event"""
        user = get_dummy_users(1)[0]
        event = Event.objects.get(title="POOLS_NO_REGISTRATIONS")
        pool = event.pools.get(name="Abakusmember")
        pool_2 = event.pools.get(name="Webkom")
        AbakusGroup.objects.get(name="Abakus").add_user(user)

        registration = Registration.objects.get_or_create(event=event, user=user)[0]
        event.register(registration)
        self.assertEqual(pool.registrations.count(), 1)
        self.assertEqual(pool_2.registrations.count(), 0)

        event_follow_exists = FollowEvent.objects.filter(
            follower=user, target=event
        ).exists()
        self.assertEqual(event_follow_exists, True)

    def test_registrations_picks_correct_pool(self):
        """Test that multiple registrations selects correct pools"""
        users = get_dummy_users(15)
        abakus_users = users[:10]
        webkom_users = users[10:]

        event = Event.objects.get(title="POOLS_NO_REGISTRATIONS")
        pool = event.pools.get(name="Abakusmember")
        pool_2 = event.pools.get(name="Webkom")

        for user in abakus_users:
            AbakusGroup.objects.get(name="Abakus").add_user(user)
        for user in webkom_users:
            AbakusGroup.objects.get(name="Webkom").add_user(user)

        registration_webkom_1 = Registration.objects.get_or_create(
            event=event, user=webkom_users[0]
        )[0]
        event.register(registration_webkom_1)

        self.assertEqual(pool.registrations.count(), 0)
        self.assertEqual(pool_2.registrations.count(), 1)

        registration_webkom_2 = Registration.objects.get_or_create(
            event=event, user=webkom_users[1]
        )[0]
        registration_abakus = Registration.objects.get_or_create(
            event=event, user=abakus_users[0]
        )[0]
        event.register(registration_webkom_2)
        event.register(registration_abakus)
        self.assertEqual(pool.registrations.count(), 1)
        self.assertEqual(pool_2.registrations.count(), 2)

    def test_no_duplicate_registrations(self):
        """Test that a user are not able register multiple times"""
        users = get_dummy_users(2)
        user_1, user_2 = users[0], users[1]
        event = Event.objects.get(title="POOLS_NO_REGISTRATIONS")
        pool = event.pools.get(id=4)
        AbakusGroup.objects.get(name="Webkom").add_user(user_1)
        AbakusGroup.objects.get(name="Abakus").add_user(user_2)
        self.assertEqual(pool.registrations.count(), 0)

        registration_one = Registration.objects.get_or_create(event=event, user=user_1)[
            0
        ]
        event.register(registration_one)
        pool_two = Pool.objects.create(
            name="test",
            capacity=1,
            event=event,
            activation_date=(timezone.now() - timedelta(hours=24)),
        )
        with self.assertRaises(ValueError):
            event.register(registration_one)

        self.assertEqual(event.number_of_registrations, 1)
        self.assertEqual(pool.registrations.count(), 1)
        self.assertEqual(pool_two.registrations.count(), 0)

    def test_can_not_register_pre_activation(self):
        """Test that user can not register before pool is activated"""
        user = get_dummy_users(1)[0]
        event = Event.objects.get(title="NO_POOLS_WEBKOM")
        permission_groups = [AbakusGroup.objects.get(name="Webkom")]
        permission_groups[0].add_user(user)
        Pool.objects.create(
            name="Webkom",
            capacity=1,
            event=event,
            activation_date=(timezone.now() + timedelta(hours=24)),
        )
        with self.assertRaises(ValueError):
            registration = Registration.objects.get_or_create(event=event, user=user)[0]
            event.register(registration)
        self.assertEqual(event.number_of_registrations, 0)
        self.assertEqual(event.waiting_registrations.count(), 0)

    def test_waiting_list_if_full(self):
        """Test that user is put in waiting list if pools are full"""
        event = Event.objects.get(title="POOLS_NO_REGISTRATIONS")
        pool = event.pools.get(id=3)
        people_2_place_in_waiting_list = 3
        users = get_dummy_users(pool.capacity + people_2_place_in_waiting_list)

        for user in users:
            AbakusGroup.objects.get(name="Abakus").add_user(user)
            registration = Registration.objects.get_or_create(event=event, user=user)[0]
            event.register(registration)

        self.assertEqual(
            event.waiting_registrations.count(), people_2_place_in_waiting_list
        )
        self.assertEqual(pool.registrations.count(), pool.capacity)
        self.assertEqual(event.number_of_registrations, pool.registrations.count())

    def test_can_register_pre_merge(self):
        """Test that user can register before the pools are merged"""
        event = Event.objects.get(title="POOLS_NO_REGISTRATIONS")
        pool_one = event.pools.get(name="Abakusmember")
        pool_two = event.pools.get(name="Webkom")
        users = get_dummy_users(2)
        user_one, user_two = users[0], users[1]
        AbakusGroup.objects.get(name="Abakus").add_user(user_one)
        AbakusGroup.objects.get(name="Webkom").add_user(user_two)
        registration_one = Registration.objects.get_or_create(
            event=event, user=user_one
        )[0]
        event.register(registration_one)
        n_registrants = pool_one.registrations.count()
        self.assertEqual(pool_one.registrations.count(), event.number_of_registrations)

        registration_two = Registration.objects.get_or_create(
            event=event, user=user_two
        )[0]
        event.register(registration_two)
        n_registrants += pool_two.registrations.count()
        self.assertEqual(n_registrants, event.number_of_registrations)

    def test_can_register_post_merge(self):
        """Test that users can register after the pools are merged"""
        event = Event.objects.get(title="NO_POOLS_ABAKUS")
        event.merge_time = timezone.now() - timedelta(hours=12)
        permission_groups_one = [AbakusGroup.objects.get(name="Abakus")]
        permission_groups_two = [AbakusGroup.objects.get(name="Webkom")]
        pool_one = Pool.objects.create(
            name="Abakus",
            capacity=1,
            event=event,
            activation_date=(timezone.now() - timedelta(hours=24)),
        )
        pool_one.permission_groups.add(permission_groups_one[0])
        pool_two = Pool.objects.create(
            name="Webkom",
            capacity=2,
            event=event,
            activation_date=(timezone.now() - timedelta(hours=24)),
        )
        pool_two.permission_groups.add(permission_groups_two[0])

        users = get_dummy_users(3)

        for user in users:
            permission_groups_one[0].add_user(user)
            registration = Registration.objects.get_or_create(event=event, user=user)[0]
            event.register(registration)

        self.assertEqual(pool_one.registrations.count(), 3)
        self.assertEqual(pool_one.registrations.count(), event.number_of_registrations)

    def test_can_only_register_with_correct_permission_group(self):
        """Test that user only can register having correct permission group"""
        event = Event.objects.get(title="NO_POOLS_ABAKUS")
        event.merge_time = timezone.now() - timedelta(hours=12)
        permission_groups_one = [AbakusGroup.objects.get(name="Abakus")]
        permission_groups_two = [AbakusGroup.objects.get(name="Webkom")]
        pool = Pool.objects.create(
            name="Webkom",
            capacity=1,
            event=event,
            activation_date=(timezone.now() - timedelta(hours=24)),
        )
        pool.permission_groups.set(permission_groups_two)

        user = get_dummy_users(1)[0]
        permission_groups_one[0].add_user(user)

        with self.assertRaises(ValueError):
            registration = Registration.objects.get_or_create(event=event, user=user)[0]
            event.register(registration)

        self.assertEqual(pool.registrations.count(), 0)

    def test_placed_in_waiting_list_post_merge(self):
        """Test waiting list after pools are merged"""
        event = Event.objects.get(title="NO_POOLS_WEBKOM")
        permission_groups = [AbakusGroup.objects.get(name="Webkom")]
        pool = Pool.objects.create(
            name="Webkom",
            capacity=2,
            event=event,
            activation_date=(timezone.now() - timedelta(hours=24)),
        )
        pool.permission_groups.set(permission_groups)
        event.merge_time = timezone.now() - timedelta(hours=12)
        users = get_dummy_users(pool.capacity + 1)
        expected_users_in_waiting_list = 1

        for user in users:
            permission_groups[0].add_user(user)
            registration = Registration.objects.get_or_create(event=event, user=user)[0]
            event.register(registration)

        self.assertEqual(
            event.waiting_registrations.count(), expected_users_in_waiting_list
        )

    def test_bump(self):
        """Test that waiting registration is bumped on unregistration"""
        event = Event.objects.get(title="POOLS_NO_REGISTRATIONS")
        pool = event.pools.first()
        users = get_dummy_users(pool.capacity + 2)

        for user in users:
            AbakusGroup.objects.get(name="Abakus").add_user(user)
            registration = Registration.objects.get_or_create(event=event, user=user)[0]
            event.register(registration)

        waiting_list_before = event.waiting_registrations.count()
        regs_before = event.number_of_registrations
        pool_before = pool.registrations.count()

        event.bump(to_pool=pool)

        self.assertEqual(event.number_of_registrations, regs_before + 1)
        self.assertEqual(event.waiting_registrations.count(), waiting_list_before - 1)
        self.assertEqual(event.waiting_registrations.first().user, users[4])
        self.assertEqual(pool.registrations.count(), pool_before + 1)

    def test_unregistering_from_event(self):
        """Test that user can unregister from event"""
        event = Event.objects.get(title="POOLS_NO_REGISTRATIONS")
        pool = event.pools.get(name="Webkom")
        users = get_dummy_users(5)
        for user in users:
            AbakusGroup.objects.get(name="Abakus").add_user(user)
        AbakusGroup.objects.get(name="Webkom").add_user(users[0])

        registration = Registration.objects.get_or_create(event=event, user=users[0])[0]
        event.register(registration)
        registrations_before = event.number_of_registrations
        pool_registrations_before = pool.registrations.count()
        event.unregister(registration)
        event_follow_exists = FollowEvent.objects.filter(
            follower=registration.user, target=event
        ).exists()

        self.assertEqual(event_follow_exists, False)
        self.assertEqual(event.number_of_registrations, registrations_before - 1)
        self.assertEqual(pool.registrations.count(), pool_registrations_before - 1)

    def test_unable_to_unregister_after_started(self):
        """Test that user cannot unregister after start_time"""
        event = Event.objects.get(title="POOLS_WITH_REGISTRATIONS")
        event.start_time = timezone.now() - timedelta(days=1)
        event.save()
        user = User.objects.get(pk=1)
        AbakusGroup.objects.get(name="Abakus").add_user(user)
        registrations_before = event.number_of_registrations
        registration = Registration.objects.get(event=event, user=user)
        with self.assertRaises(ValueError):
            event.unregister(registration)
        self.assertEqual(event.number_of_registrations, registrations_before)

    def test_register_after_unregister(self):
        """Test that user can re-register after having unregistered"""
        event = Event.objects.get(title="POOLS_WITH_REGISTRATIONS")
        user = User.objects.get(pk=1)
        AbakusGroup.objects.get(name="Abakus").add_user(user)
        registrations_before = event.number_of_registrations

        registration = Registration.objects.get(event=event, user=user)
        event.unregister(registration)
        self.assertEqual(event.number_of_registrations, registrations_before - 1)

        event.register(registration)
        self.assertEqual(event.number_of_registrations, registrations_before)

    def test_register_to_waiting_list_after_unregister(self):
        """Test that user can re-register into waiting list after having unregistered"""
        event = Event.objects.get(title="POOLS_WITH_REGISTRATIONS")
        user = get_dummy_users(1)[0]
        AbakusGroup.objects.get(name="Abakus").add_user(user)

        registration = Registration.objects.get_or_create(event=event, user=user)[0]
        event.register(registration)
        self.assertEqual(event.waiting_registrations.count(), 1)

        event.unregister(registration)
        self.assertEqual(event.waiting_registrations.count(), 0)

        event.register(registration)
        self.assertEqual(event.waiting_registrations.count(), 1)

    def test_unregistering_non_existing_user(self):
        """Test that non existing user trying to unregister raises error"""
        event = Event.objects.get(title="POOLS_NO_REGISTRATIONS")
        user = get_dummy_users(1)[0]
        with self.assertRaises(Registration.DoesNotExist):
            registration = Registration.objects.get(event=event, user=user)
            event.unregister(registration)

    def test_popping_from_waiting_list_pre_merge(self):
        """Test popping of first user in waiting list before merge"""
        event = Event.objects.get(title="NO_POOLS_WEBKOM")
        permission_groups = [AbakusGroup.objects.get(name="Webkom")]
        pool = Pool.objects.create(
            name="Webkom",
            capacity=1,
            event=event,
            activation_date=(timezone.now() - timedelta(hours=24)),
        )
        pool.permission_groups.set(permission_groups)
        users = get_dummy_users(pool.capacity + 10)

        for user in users:
            permission_groups[0].add_user(user)
            registration = Registration.objects.get_or_create(event=event, user=user)[0]
            event.register(registration)

        self.assertNotEqual(event.waiting_registrations.count(), 0)
        prev = event.pop_from_waiting_list()
        for top in event.waiting_registrations:
            self.assertLessEqual(prev.registration_date, top.registration_date)
            prev = top

    def test_popping_from_waiting_list_post_merge(self):
        """Test popping of first user in waiting list after merge"""
        event = Event.objects.get(title="NO_POOLS_WEBKOM")
        event.merge_time = timezone.now() - timedelta(hours=12)
        event.save()
        permission_groups = [AbakusGroup.objects.get(name="Webkom")]
        pool = Pool.objects.create(
            name="Webkom",
            capacity=1,
            event=event,
            activation_date=(timezone.now() - timedelta(hours=24)),
        )
        pool.permission_groups.set(permission_groups)
        users = get_dummy_users(pool.capacity + 10)

        for user in users:
            permission_groups[0].add_user(user)
            registration = Registration.objects.get_or_create(event=event, user=user)[0]
            event.register(registration)

        self.assertNotEqual(event.waiting_registrations.count(), 0)
        prev = event.pop_from_waiting_list()
        for registration in event.waiting_registrations:
            self.assertLessEqual(prev.registration_date, registration.registration_date)
            prev = registration

    def test_popping_from_waiting_list_with_to_pool(self):
        """Test popping of first user in waiting list after merge"""
        event = Event.objects.get(title="NO_POOLS_WEBKOM")
        permission_groups = [AbakusGroup.objects.get(name="Webkom")]
        pool = Pool.objects.create(
            name="Webkom",
            capacity=1,
            event=event,
            activation_date=(timezone.now() - timedelta(hours=24)),
        )
        pool.permission_groups.set(permission_groups)
        users = get_dummy_users(2)

        for user in users:
            permission_groups[0].add_user(user)
            registration = Registration.objects.get_or_create(event=event, user=user)[0]
            event.register(registration)

        top = event.pop_from_waiting_list(pool)
        self.assertIsNotNone(top)

    def test_popping_from_waiting_list_with_to_pool_without_heed_penalties(self):
        """Test popping of first user in waiting list after merge"""
        event = Event.objects.get(title="NO_POOLS_WEBKOM")
        event.heed_penalties = False
        event.save()
        permission_groups = [AbakusGroup.objects.get(name="Webkom")]
        pool = Pool.objects.create(
            name="Webkom",
            capacity=1,
            event=event,
            activation_date=(timezone.now() - timedelta(hours=24)),
        )
        pool.permission_groups.set(permission_groups)
        users = get_dummy_users(2)

        for user in users:
            permission_groups[0].add_user(user)
            registration = Registration.objects.get_or_create(event=event, user=user)[0]
            event.register(registration)

        top = event.pop_from_waiting_list(pool)
        self.assertIsNotNone(top)

    def test_unregistering_from_waiting_list(self):
        """Test that user can unregister from waiting list"""
        event = Event.objects.get(title="POOLS_NO_REGISTRATIONS")
        pool = event.pools.first()
        users = get_dummy_users(pool.capacity + 10)

        for user in users:
            AbakusGroup.objects.get(name="Abakus").add_user(user)
            registration = Registration.objects.get_or_create(event=event, user=user)[0]
            event.register(registration)

        event_size_before = event.number_of_registrations
        pool_size_before = pool.registrations.count()
        waiting_list_before = event.waiting_registrations.count()

        registration_last = Registration.objects.get(event=event, user=users[-1])
        event.unregister(registration_last)

        self.assertEqual(event.number_of_registrations, event_size_before)
        self.assertEqual(pool.registrations.count(), pool_size_before)
        self.assertEqual(event.waiting_registrations.count(), waiting_list_before - 1)
        self.assertLessEqual(event.number_of_registrations, event.active_capacity)

    def test_unregistering_and_bumping_pre_merge(self):
        """Test unregistration and that waiting list is bumped accordingly before merge"""
        event = Event.objects.get(title="POOLS_NO_REGISTRATIONS")
        pool = event.pools.first()
        users = get_dummy_users(pool.capacity + 10)

        for user in users:
            AbakusGroup.objects.get(name="Abakus").add_user(user)
            registration = Registration.objects.get_or_create(event=event, user=user)[0]
            event.register(registration)

        waiting_list_before = event.waiting_registrations.count()
        event_size_before = event.number_of_registrations
        pool_size_before = pool.registrations.count()

        user_to_unregister = event.registrations.first().user
        registration_to_unregister = Registration.objects.get(
            event=event, user=user_to_unregister
        )
        event.unregister(registration_to_unregister)

        pool.refresh_from_db()

        self.assertEqual(pool.counter, pool.registrations.count())
        self.assertEqual(pool.registrations.count(), pool_size_before)
        self.assertEqual(event.number_of_registrations, event_size_before)
        self.assertEqual(event.waiting_registrations.count(), waiting_list_before - 1)
        self.assertLessEqual(event.number_of_registrations, event.active_capacity)

    def test_unregistering_and_bumping_post_merge(self):
        """Test unregistration and that waiting list is bumped accordingly after merge"""
        event = Event.objects.get(title="POOLS_NO_REGISTRATIONS")
        event.merge_time = timezone.now() - timedelta(hours=24)
        event.save()
        pool_one = event.pools.get(name="Abakusmember")
        pool_two = event.pools.get(name="Webkom")

        users = get_dummy_users(7)
        abakus_users = users[:3]
        webkom_users = users[3:5]
        admin_user = users[6]

        for user in abakus_users:
            AbakusGroup.objects.get(name="Abakus").add_user(user)
            event.admin_register(
                admin_user, user, pool=pool_one, admin_registration_reason="test"
            )
            event_follow_exists = FollowEvent.objects.filter(
                follower=user, target=event
            ).exists()
            self.assertEqual(event_follow_exists, True)
        for user in webkom_users:
            AbakusGroup.objects.get(name="Webkom").add_user(user)
            event.admin_register(
                admin_user, user, pool=pool_two, admin_registration_reason="test"
            )
            event_follow_exists = FollowEvent.objects.filter(
                follower=user, target=event
            ).exists()
            self.assertEqual(event_follow_exists, True)

        AbakusGroup.objects.get(name="Abakus").add_user(users[5])
        registration = Registration.objects.get_or_create(event=event, user=users[5])[0]
        event.register(registration)

        waiting_list_before = event.waiting_registrations.count()
        event_size_before = event.number_of_registrations
        pool_one_size_before = pool_one.registrations.count()
        pool_two_size_before = pool_two.registrations.count()

        user_to_unregister = pool_two.registrations.first().user
        registration_to_unregister = Registration.objects.get(
            event=event, user=user_to_unregister
        )

        event.unregister(registration_to_unregister)
        event_follow_exists = FollowEvent.objects.filter(
            follower=user_to_unregister, target=event
        ).exists()

        self.assertEqual(event_follow_exists, False)
        self.assertEqual(event.number_of_registrations, event_size_before)
        self.assertEqual(event.waiting_registrations.count(), waiting_list_before - 1)
        self.assertEqual(pool_one.registrations.count(), pool_one_size_before + 1)
        self.assertGreater(pool_one.registrations.count(), pool_one.capacity)
        self.assertEqual(pool_two.registrations.count(), pool_two_size_before - 1)
        self.assertLessEqual(event.number_of_registrations, event.active_capacity)

    def test_bumping_when_bumped_has_several_pools_available(self):
        """Test that user is bumped when user can join multiple pools"""
        event = Event.objects.get(title="POOLS_WITH_REGISTRATIONS")
        users = get_dummy_users(4)
        user_0 = users[0]
        pre_reg = event.registrations.first()
        pool = event.pools.get(name="Webkom")

        pool_registrations_before = pool.registrations.count()
        waiting_list_before = event.waiting_registrations.count()
        number_of_registered_before = event.number_of_registrations

        for user in users:
            AbakusGroup.objects.get(name="Webkom").add_user(user)
            registration = Registration.objects.get_or_create(event=event, user=user)[0]
            event.register(registration)

        self.assertEqual(pool.registrations.count(), pool_registrations_before + 3)
        self.assertEqual(event.waiting_registrations.count(), waiting_list_before + 1)
        self.assertEqual(event.number_of_registrations, number_of_registered_before + 3)

        event.unregister(pre_reg)

        self.assertEqual(pool.registrations.count(), pool_registrations_before + 3)
        self.assertEqual(event.waiting_registrations.count(), waiting_list_before)
        self.assertEqual(event.number_of_registrations, number_of_registered_before + 3)

        registration_to_unregister = Registration.objects.get(event=event, user=user_0)
        event.unregister(registration_to_unregister)

        self.assertEqual(event.number_of_registrations, number_of_registered_before + 2)

    def test_unregistration_date_is_set_at_unregistration(self):
        """Test that unregistration date gets set when unregistering"""
        event = Event.objects.get(title="POOLS_NO_REGISTRATIONS")
        user = get_dummy_users(1)[0]
        AbakusGroup.objects.get(name="Webkom").add_user(user)
        registration = Registration.objects.get_or_create(event=event, user=user)[0]
        event.register(registration)
        registration = event.registrations.first()

        self.assertIsNone(registration.unregistration_date)
        event.unregister(registration)
        registration = event.registrations.first()
        self.assertIsNotNone(registration.unregistration_date)

    def test_bump_after_rebalance(self):
        """Test bumping after pool rebalancing when user unregistrates"""
        event = Event.objects.get(title="POOLS_NO_REGISTRATIONS")
        pool_one = event.pools.get(name="Abakusmember")
        pool_two = event.pools.get(name="Webkom")
        users = get_dummy_users(6)
        abakus_users = users[0:3]
        webkom_users = users[3:6]
        for user in abakus_users:
            AbakusGroup.objects.get(name="Abakus").add_user(user)
        for user in webkom_users:
            AbakusGroup.objects.get(name="Webkom").add_user(user)

        for user in webkom_users:
            registration = Registration.objects.get_or_create(event=event, user=user)[0]
            event.register(registration)
        for user in abakus_users:
            registration = Registration.objects.get_or_create(event=event, user=user)[0]
            event.register(registration)

        pool_one_before = pool_one.registrations.count()
        pool_two_before = pool_two.registrations.count()
        waiting_before = event.waiting_registrations.count()

        registration_to_unregister = Registration.objects.get(
            event=event, user=webkom_users[0]
        )
        event.unregister(registration_to_unregister)
        self.assertEqual(pool_one.registrations.count(), pool_one_before)
        self.assertEqual(pool_two.registrations.count(), pool_two_before)
        self.assertEqual(event.waiting_registrations.count(), waiting_before - 1)

    def test_user_is_moved_after_rebalance(self):
        """Test that user's pool has changed after being rebalanced"""
        event = Event.objects.get(title="POOLS_NO_REGISTRATIONS")
        pool_one = event.pools.get(name="Abakusmember")
        pool_two = event.pools.get(name="Webkom")
        users = get_dummy_users(6)
        abakus_users = users[0:3]
        webkom_users = users[3:6]
        for user in abakus_users:
            AbakusGroup.objects.get(name="Abakus").add_user(user)
        for user in webkom_users:
            AbakusGroup.objects.get(name="Webkom").add_user(user)

        for user in webkom_users:
            registration = Registration.objects.get_or_create(event=event, user=user)[0]
            event.register(registration)
        for user in abakus_users:
            registration = Registration.objects.get_or_create(event=event, user=user)[0]
            event.register(registration)

        moved_user_registration = event.registrations.get(user=webkom_users[2])
        self.assertEqual(moved_user_registration.pool, pool_one)

        registration_to_unregister = Registration.objects.get(
            event=event, user=webkom_users[0]
        )
        event.unregister(registration_to_unregister)
        moved_user_registration = event.registrations.get(user=webkom_users[2])
        self.assertEqual(moved_user_registration.pool, pool_two)

    def test_correct_user_is_bumped_after_rebalance(self):
        """Test that the first user available for the rebalanced pool is bumped"""
        event = Event.objects.get(title="POOLS_NO_REGISTRATIONS")
        pool_one = event.pools.get(name="Abakusmember")
        users = get_dummy_users(7)
        abakus_users = users[0:4]
        webkom_users = users[4:7]
        for user in abakus_users:
            AbakusGroup.objects.get(name="Abakus").add_user(user)
        for user in webkom_users:
            AbakusGroup.objects.get(name="Webkom").add_user(user)

        for user in webkom_users:
            registration = Registration.objects.get_or_create(event=event, user=user)[0]
            event.register(registration)
        for user in abakus_users:
            registration = Registration.objects.get_or_create(event=event, user=user)[0]
            event.register(registration)

        waiting_before = event.waiting_registrations.count()
        user_to_be_bumped = event.waiting_registrations.get(user=abakus_users[2]).user
        user_not_to_be_bumped = event.waiting_registrations.get(
            user=abakus_users[3]
        ).user

        registration_to_unregister = Registration.objects.get(
            event=event, user=webkom_users[0]
        )
        event.unregister(registration_to_unregister)
        self.assertEqual(event.registrations.get(user=user_to_be_bumped).pool, pool_one)
        self.assertIsNone(event.registrations.get(user=user_not_to_be_bumped).pool)
        self.assertEqual(event.waiting_registrations.count(), waiting_before - 1)

    def test_rebalance_pool_method(self):
        """Test rebalancing method by moving registered user's pool to fit waiting list user"""
        event = Event.objects.get(title="POOLS_NO_REGISTRATIONS")
        abakus_pool = event.pools.get(name="Abakusmember")
        webkom_pool = event.pools.get(name="Webkom")
        users = get_dummy_users(4)
        abakus_user = users[0]
        webkom_users = users[1:]
        AbakusGroup.objects.get(name="Abakus").add_user(abakus_user)
        for user in webkom_users:
            AbakusGroup.objects.get(name="Webkom").add_user(user)

        registration_abakus = Registration.objects.get_or_create(
            event=event, user=abakus_user
        )[0]
        event.register(registration_abakus)
        for user in webkom_users[:2]:
            registration = Registration.objects.get_or_create(event=event, user=user)[0]
            event.register(registration)

        self.assertFalse(event.rebalance_pool(abakus_pool, webkom_pool))
        self.assertEqual(abakus_pool.registrations.count(), 1)
        self.assertEqual(webkom_pool.registrations.count(), 2)

        registration_webkom = Registration.objects.get_or_create(
            event=event, user=webkom_users[2]
        )[0]
        event.register(registration_webkom)

        registration_to_unregister = Registration.objects.get(
            event=event, user=webkom_users[0]
        )
        event.unregister(registration_to_unregister)
        self.assertEqual(abakus_pool.registrations.count(), 2)
        self.assertEqual(webkom_pool.registrations.count(), 1)

        self.assertTrue(event.rebalance_pool(abakus_pool, webkom_pool))
        self.assertEqual(abakus_pool.registrations.count(), 1)
        self.assertEqual(webkom_pool.registrations.count(), 2)

    def test_rebalance_pool_method_should_not_overflow(self):
        """Test rebalancing method by moving registered user's pool to fit waiting list user"""
        event = Event.objects.get(title="POOLS_NO_REGISTRATIONS")
        abakus_pool = event.pools.get(name="Abakusmember")
        webkom_pool = event.pools.get(name="Webkom")
        users = get_dummy_users(6)
        for user in users:
            AbakusGroup.objects.get(name="Abakus").add_user(user)

        webkom_users = users[:3]
        abakus_users = users[3:]

        for user in webkom_users:
            registration = Registration.objects.get_or_create(event=event, user=user)[0]
            event.register(registration)

        self.assertEqual(abakus_pool.registrations.count(), 3)
        self.assertEqual(webkom_pool.registrations.count(), 0)

        for user in abakus_users:
            registration = Registration.objects.get_or_create(event=event, user=user)[0]
            event.register(registration)

        self.assertEqual(abakus_pool.registrations.count(), 3)
        self.assertEqual(webkom_pool.registrations.count(), 0)

        for user in webkom_users:
            AbakusGroup.objects.get(name="Webkom").add_user(user)

        event.bump_on_pool_creation_or_expansion()
        self.assertEqual(abakus_pool.registrations.count(), 3)  # Abakus-pool has size 3
        self.assertEqual(webkom_pool.registrations.count(), 2)  # Webkom-pool has size 2

    def test_cant_register_after_event_has_started(self):
        """Test that a user cannot register after the event has started."""
        event = Event.objects.get(title="POOLS_NO_REGISTRATIONS")

        current_time = timezone.now()
        event.start_time = current_time - timedelta(hours=3)
        event.save()

        user = get_dummy_users(1)[0]
        AbakusGroup.objects.get(name="Abakus").add_user(user)

        registration = Registration.objects.get_or_create(event=event, user=user)[0]
        with self.assertRaises(ValueError):
            event.register(registration)
        self.assertEqual(event.number_of_registrations, 0)

    def test_cant_register_after_event_has_closed(self):
        """Test that a user cannot register after the event has started."""
        event = Event.objects.get(title="POOLS_NO_REGISTRATIONS")

        current_time = timezone.now()
        event.start_time = current_time + timedelta(hours=1)

        event.save()

        user = get_dummy_users(1)[0]
        AbakusGroup.objects.get(name="Abakus").add_user(user)

        registration = Registration.objects.get_or_create(event=event, user=user)[0]
        with self.assertRaises(ValueError):
            event.register(registration)
        self.assertEqual(event.number_of_registrations, 0)

    def test_cant_register_after_deadline_hours(self):
        """Test that a user cannot register after the deadline-hours before the event."""
        event = Event.objects.get(title="POOLS_NO_REGISTRATIONS")

        current_time = timezone.now()

        event.start_time = current_time + timedelta(hours=1)
        event.save()

        user = get_dummy_users(1)[0]
        AbakusGroup.objects.get(name="Abakus").add_user(user)

        registration = Registration.objects.get_or_create(event=event, user=user)[0]
        with self.assertRaises(ValueError):
            event.register(registration)
        self.assertEqual(event.number_of_registrations, 0)

    def test_cant_unregister_after_deadline_hours(self):
        """Test that a user cannot unregister after the deadline-hours before the event."""
        event = Event.objects.get(title="POOLS_NO_REGISTRATIONS")

        user = get_dummy_users(1)[0]
        AbakusGroup.objects.get(name="Abakus").add_user(user)
        registration = Registration.objects.get_or_create(event=event, user=user)[0]
        event.register(registration)
        self.assertEqual(event.number_of_registrations, 1)

        current_time = timezone.now()

        event.start_time = current_time + timedelta(hours=2)
        event.save()

        with self.assertRaises(ValueError):
            event.unregister(registration)
        self.assertEqual(event.number_of_registrations, 1)

    def test_presence_method_raises_error_with_illegal_value(self):
        """Test that presence raises error when given an illegal presence choice"""
        event = Event.objects.get(title="POOLS_WITH_REGISTRATIONS")
        registration = event.registrations.first()

        with self.assertRaises(ValueError):
            registration.set_presence("ripvalue")

    def test_bump_on_pool_update(self):
        """Test that waiting registrations are bumped when a pool is expanded"""
        event = Event.objects.get(title="POOLS_NO_REGISTRATIONS")
        pool = event.pools.first()
        users = get_dummy_users(6)
        for user in users:
            AbakusGroup.objects.get(name="Abakus").add_user(user)
            registration = Registration.objects.get_or_create(event=event, user=user)[0]
            event.register(registration)

        no_of_waiting_registrations_before = event.waiting_registrations.count()
        self.assertEqual(no_of_waiting_registrations_before, 3)

        pool.capacity = 5
        pool.save()
        event.bump_on_pool_creation_or_expansion()

        no_of_waiting_registrations_after = event.waiting_registrations.count()
        self.assertEqual(no_of_waiting_registrations_after, 1)

    def test_no_bump_to_illegal_pool_on_expansion(self):
        """Test that waiting regs aren't bumped if they don't have perm to join the expanded pool"""
        event = Event.objects.get(title="POOLS_NO_REGISTRATIONS")
        pool = event.pools.get(name="Webkom")
        users = get_dummy_users(6)
        for user in users:
            AbakusGroup.objects.get(name="Abakus").add_user(user)
            registration = Registration.objects.get_or_create(event=event, user=user)[0]
            event.register(registration)

        no_of_waiting_registrations_before = event.waiting_registrations.count()
        self.assertEqual(no_of_waiting_registrations_before, 3)

        pool.capacity = 5
        pool.save()
        event.bump_on_pool_creation_or_expansion()

        no_of_waiting_registrations_after = event.waiting_registrations.count()
        self.assertEqual(no_of_waiting_registrations_after, 3)

    def test_bump_on_pool_creation(self):
        """Test that waiting registrations are bumped when a new pool is created"""
        event = Event.objects.get(title="POOLS_NO_REGISTRATIONS")
        users = get_dummy_users(6)
        for user in users:
            AbakusGroup.objects.get(name="Abakus").add_user(user)
            registration = Registration.objects.get_or_create(event=event, user=user)[0]
            event.register(registration)

        no_of_waiting_registrations_before = event.waiting_registrations.count()
        self.assertEqual(no_of_waiting_registrations_before, 3)

        new_pool = Pool.objects.create(
            name="test",
            capacity=3,
            event=event,
            activation_date=(timezone.now() - timedelta(hours=24)),
        )
        new_pool.permission_groups.set([AbakusGroup.objects.get(name="Abakus")])
        event.bump_on_pool_creation_or_expansion()

        no_of_waiting_registrations_after = event.waiting_registrations.count()
        self.assertEqual(no_of_waiting_registrations_after, 0)
        self.assertEqual(new_pool.registrations.count(), 3)

    def test_bump_on_several_pools_updated(self):
        """Test that waiting regs are bumped to several pools when several pools are updated"""
        event = Event.objects.get(title="POOLS_NO_REGISTRATIONS")
        pool_one = event.pools.get(name="Abakusmember")
        pool_two = event.pools.get(name="Webkom")
        users = get_dummy_users(7)
        for user in users:
            AbakusGroup.objects.get(name="Webkom").add_user(user)
            registration = Registration.objects.get_or_create(event=event, user=user)[0]
            event.register(registration)

        no_of_waiting_registrations_before = event.waiting_registrations.count()
        self.assertEqual(no_of_waiting_registrations_before, 2)

        pool_one.capacity = pool_one.capacity + 1
        pool_two.capacity = pool_two.capacity + 1
        pool_one.save()
        pool_two.save()
        event.bump_on_pool_creation_or_expansion()

        no_of_waiting_registrations_after = event.waiting_registrations.count()
        self.assertEqual(no_of_waiting_registrations_after, 0)

    def test_register_when_unregister_when_event_is_full(self):
        """Test that counter works when registering after an event is full"""
        event = Event.objects.get(title="POOLS_NO_REGISTRATIONS")
        users = get_dummy_users(6)
        user_one = users[0]
        user_two = users[-1]

        for user in users[:5]:
            AbakusGroup.objects.get(name="Webkom").add_user(user)
            registration = Registration.objects.get_or_create(event=event, user=user)[0]
            event.register(registration)

        AbakusGroup.objects.get(name="Webkom").add_user(user_two)
        registration_one = Registration.objects.get(event=event, user=user_one)
        registration_two = Registration.objects.create(event=event, user=user_two)
        event.unregister(registration_one)

        event.register(registration_two)
        self.assertTrue(registration_two.is_admitted)

    def test_that_is_ready_flag_disables_new_registrations(self):
        """Test that users are not able to register when is_ready is False"""

        event = Event.objects.get(title="POOLS_WITH_REGISTRATIONS")
        event.is_ready = False
        event.save()

        user = get_dummy_users(1)[0]

        AbakusGroup.objects.get(name="Abakus").add_user(user)
        registration = Registration.objects.get_or_create(event=event, user=user)[0]
        with self.assertRaises(EventNotReady):
            event.register(registration)
