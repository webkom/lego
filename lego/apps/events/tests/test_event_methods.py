from datetime import timedelta

from django.utils import timezone

from lego.apps.events.models import Event, Pool, Registration
from lego.apps.events.serializers.events import (
    EventAdministrateSerializer,
    populate_event_registration_users_with_grade,
)
from lego.apps.users.constants import GROUP_GRADE, GROUP_OTHER
from lego.apps.users.models import AbakusGroup
from lego.utils.test_utils import BaseTestCase

from .utils import get_dummy_users


class EventMethodTest(BaseTestCase):
    fixtures = [
        "test_abakus_groups.yaml",
        "test_users.yaml",
        "test_companies.yaml",
        "test_events.yaml",
    ]

    def setUp(self):
        Event.objects.all().update(start_time=timezone.now() + timedelta(hours=3))

    def test_str(self):
        event = Event.objects.get(pk=1)
        self.assertEqual(str(event), event.title)

    def test_event_save(self):
        event = Event.objects.get(title="POOLS_NO_REGISTRATIONS")
        event.merge_time = timezone.now() - timedelta(days=1)
        users = get_dummy_users(2)
        webkom = AbakusGroup.objects.get(name="Webkom")
        for user in users:
            webkom.add_user(user)
            reg = Registration.objects.create(event=event, user=user)
            event.register(reg)

        for pool in event.pools.all():
            self.assertEqual(pool.counter, 0)
        event.save()
        event.refresh_from_db()
        for pool in event.pools.all():
            self.assertEqual(pool.counter, pool.registrations.count())

    def test_populate_event_registration_users_with_grade(self):
        """Test that grades get correctly populated in registration users"""
        event = Event.objects.get(title="POOLS_WITH_REGISTRATIONS")
        pool = event.pools.first()
        grade = AbakusGroup.objects.create(name="DummyGrade", type=GROUP_GRADE)
        other_abakus_group = AbakusGroup.objects.create(
            name="DummyGroup", type=GROUP_OTHER
        )
        grade_values = {"id": grade.id, "name": "DummyGrade"}
        reg1, reg2 = event.registrations.filter(pool=pool)[:2]
        grade.add_user(reg1.user)
        other_abakus_group.add_user(reg1.user)
        other_abakus_group.add_user(reg2.user)
        event_dict = EventAdministrateSerializer(event).data

        populated_event = populate_event_registration_users_with_grade(event_dict)

        for populated_pool in populated_event["pools"]:
            if pool.id == populated_pool["id"]:
                for populated_registration in populated_pool["registrations"]:
                    user_grade = populated_registration["user"]["grade"]
                    if reg1.id == populated_registration["id"]:
                        self.assertEqual(user_grade, grade_values)
                    else:
                        self.assertEqual(user_grade, None)

    def test_populate_event_registration_users_with_grade_without_grades(self):
        """Test that grade is None for registration users when they are not in grade"""
        event = Event.objects.get(title="POOLS_WITH_REGISTRATIONS")
        pool = event.pools.first()
        other_abakus_group = AbakusGroup.objects.create(
            name="DummyGroup", type=GROUP_OTHER
        )
        reg1, reg2 = event.registrations.filter(pool=pool)[:2]
        other_abakus_group.add_user(reg1.user)
        other_abakus_group.add_user(reg2.user)
        event_dict = EventAdministrateSerializer(event).data

        populated_event = populate_event_registration_users_with_grade(event_dict)

        for populated_pool in populated_event["pools"]:
            if pool.id == populated_pool["id"]:
                for populated_registration in populated_pool["registrations"]:
                    user_grade = populated_registration["user"]["grade"]
                    self.assertEqual(user_grade, None)

    def test_calculate_full_pools(self):
        """Test calculation of open and full pools for usage in registering method"""
        event = Event.objects.get(title="POOLS_NO_REGISTRATIONS")
        abakus_pool = event.pools.get(name="Abakusmember")
        webkom_pool = event.pools.get(name="Webkom")
        users = get_dummy_users(5)
        for user in users:
            AbakusGroup.objects.get(name="Webkom").add_user(user)

        full_pools, open_pools = event.calculate_full_pools([abakus_pool, webkom_pool])
        self.assertEqual(len(full_pools), 0)
        self.assertEqual(len(open_pools), 2)

        for user in users[:3]:
            registration = Registration.objects.get_or_create(event=event, user=user)[0]
            event.register(registration)
        full_pools, open_pools = event.calculate_full_pools([abakus_pool, webkom_pool])
        self.assertEqual(len(full_pools), 1)
        self.assertEqual(len(open_pools), 1)

        for user in users[3:]:
            registration = Registration.objects.get_or_create(event=event, user=user)[0]
            event.register(registration)
        full_pools, open_pools = event.calculate_full_pools([abakus_pool, webkom_pool])
        self.assertEqual(len(full_pools), 2)
        self.assertEqual(len(open_pools), 0)

    def test_doesnt_have_pool_permission(self):
        """Test method checking that user does not have the appropriate permission groups"""
        event = Event.objects.get(title="POOLS_NO_REGISTRATIONS")
        user = get_dummy_users(1)[0]
        abakus_pool = event.pools.get(name="Abakusmember")
        webkom_pool = event.pools.get(name="Webkom")
        self.assertFalse(event.has_pool_permission(user, abakus_pool))
        self.assertFalse(event.has_pool_permission(user, webkom_pool))

    def test_has_some_pool_permissions(self):
        """Test method checking that user one of the appropriate permission groups"""
        event = Event.objects.get(title="POOLS_NO_REGISTRATIONS")
        user = get_dummy_users(1)[0]
        abakus_pool = event.pools.get(name="Abakusmember")
        webkom_pool = event.pools.get(name="Webkom")
        AbakusGroup.objects.get(name="Abakus").add_user(user)
        self.assertTrue(event.has_pool_permission(user, abakus_pool))
        self.assertFalse(event.has_pool_permission(user, webkom_pool))

    def test_has_all_pool_permissions(self):
        """Test method checking that user have all the appropriate permission groups"""
        event = Event.objects.get(title="POOLS_NO_REGISTRATIONS")
        user = get_dummy_users(1)[0]
        abakus_pool = event.pools.get(name="Abakusmember")
        webkom_pool = event.pools.get(name="Webkom")
        AbakusGroup.objects.get(name="Webkom").add_user(user)
        self.assertTrue(event.has_pool_permission(user, abakus_pool))
        self.assertTrue(event.has_pool_permission(user, webkom_pool))

    def test_find_most_exclusive_pool(self):
        """Test method calculating the most exclusive pool for the registering user"""
        event = Event.objects.get(title="POOLS_NO_REGISTRATIONS")
        webkom_pool = event.pools.get(name="Webkom")
        abakus_pool = event.pools.get(name="Abakusmember")

        users = get_dummy_users(3)
        user_three = users.pop()
        for user in users:
            AbakusGroup.objects.get(name="Abakus").add_user(user)
        AbakusGroup.objects.get(name="Webkom").add_user(user_three)

        self.assertEqual(
            event.find_most_exclusive_pools([webkom_pool, abakus_pool])[0], webkom_pool
        )
        self.assertEqual(
            len(event.find_most_exclusive_pools([webkom_pool, abakus_pool])), 1
        )

    def test_find_most_exclusive_when_equal(self):
        """Test method calculating the most exclusive pool when they are equally exclusive"""
        event = Event.objects.get(title="POOLS_NO_REGISTRATIONS")
        webkom_pool = event.pools.get(name="Webkom")
        abakus_pool = event.pools.get(name="Abakusmember")
        users = get_dummy_users(3)
        for user in users:
            AbakusGroup.objects.get(name="Webkom").add_user(user)
        self.assertEqual(
            len(event.find_most_exclusive_pools([webkom_pool, abakus_pool])), 2
        )

    def test_select_highest_capacity(self):
        """Test method selecting the pool with the highest capacity"""
        event = Event.objects.get(title="POOLS_NO_REGISTRATIONS")
        webkom_pool = event.pools.get(name="Webkom")
        abakus_pool = event.pools.get(name="Abakusmember")
        self.assertEqual(
            event.select_highest_capacity([abakus_pool, webkom_pool]), abakus_pool
        )

    def test_get_earliest_registration_time_without_pools_provided(self):
        """Test method calculating the earliest registration time for user without provided pools"""
        event = Event.objects.get(title="POOLS_NO_REGISTRATIONS")
        webkom_pool = event.pools.get(name="Webkom")
        abakus_pool = event.pools.get(name="Abakusmember")

        current_time = timezone.now()
        webkom_pool.activation_date = current_time
        webkom_pool.save()
        abakus_pool.activation_date = current_time - timedelta(hours=1)
        abakus_pool.save()

        user = get_dummy_users(1)[0]
        AbakusGroup.objects.get(name="Webkom").add_user(user)
        earliest_reg = event.get_earliest_registration_time(user)

        self.assertEqual(earliest_reg, abakus_pool.activation_date)

    def test_get_earliest_registration_time_no_penalties(self):
        """Test method calculating the earliest registration time for two pools"""
        event = Event.objects.get(title="POOLS_NO_REGISTRATIONS")
        webkom_pool = event.pools.get(name="Webkom")
        abakus_pool = event.pools.get(name="Abakusmember")

        current_time = timezone.now()
        webkom_pool.activation_date = current_time
        webkom_pool.save()
        abakus_pool.activation_date = current_time - timedelta(hours=1)
        abakus_pool.save()

        user = get_dummy_users(1)[0]
        AbakusGroup.objects.get(name="Webkom").add_user(user)

        earliest_reg = event.get_earliest_registration_time(
            user, [webkom_pool, abakus_pool]
        )
        self.assertEqual(earliest_reg, current_time - timedelta(hours=1))

    def test_number_of_waiting_registrations(self):
        """Test method counting the number of registrations in waiting list"""
        event = Event.objects.get(title="POOLS_NO_REGISTRATIONS")
        pool = event.pools.get(name="Abakusmember")
        people_to_place_in_waiting_list = 3
        users = get_dummy_users(pool.capacity + 3)

        for user in users:
            AbakusGroup.objects.get(name="Abakus").add_user(user)
            registration = Registration.objects.get_or_create(event=event, user=user)[0]
            event.register(registration)

        self.assertEqual(
            event.waiting_registrations.count(), people_to_place_in_waiting_list
        )

    def test_spots_left_for_user_before_merge(self):
        """Test that spots_left_for_user returns correct number of spots"""
        event = Event.objects.get(title="POOLS_WITH_REGISTRATIONS")

        pool = event.pools.get(name="Abakusmember")
        pool.capacity = 10
        pool.save()
        user = get_dummy_users(1)[0]
        AbakusGroup.objects.get(name="Abakus").add_user(user)

        self.assertEqual(event.spots_left_for_user(user), 8)

    def test_spots_left_for_user_before_merge_multiple_pools(self):
        """Test that spots_left_for_user returns correct number of spots with multiple pools"""
        event = Event.objects.get(title="POOLS_WITH_REGISTRATIONS")

        pool = event.pools.get(name="Abakusmember")
        pool.capacity = 10
        pool.save()
        user = get_dummy_users(1)[0]
        AbakusGroup.objects.get(name="Webkom").add_user(user)

        self.assertEqual(event.spots_left_for_user(user), 11)

    def test_spots_left_for_user_after_merge(self):
        """Test that spots_left_for_user returns correct number of spots after merge"""
        event = Event.objects.get(title="POOLS_WITH_REGISTRATIONS")

        event.merge_time = timezone.now() - timedelta(days=1)
        event.save()
        user = get_dummy_users(1)[0]
        AbakusGroup.objects.get(name="Abakus").add_user(user)

        self.assertEqual(event.spots_left_for_user(user), 3)

    def test_is_full_when_not_full(self):
        event = Event.objects.get(title="POOLS_WITH_REGISTRATIONS")
        self.assertEqual(event.is_full, False)

    def test_is_full_when_full(self):
        event = Event.objects.get(title="POOLS_WITH_REGISTRATIONS")

        users = get_dummy_users(5)

        for user in users:
            AbakusGroup.objects.get(name="Webkom").add_user(user)
            registration = Registration.objects.get_or_create(event=event, user=user)[0]
            event.register(registration)

        self.assertEqual(event.is_full, True)

    def test_is_full_when_unlimited(self):
        event = Event.objects.get(title="NO_POOLS_ABAKUS")

        pool = Pool.objects.create(
            name="Pool1",
            event=event,
            capacity=0,
            activation_date=timezone.now() - timedelta(days=1),
        )
        webkom_group = AbakusGroup.objects.get(name="Webkom")
        pool.permission_groups.set([webkom_group])
        users = get_dummy_users(5)

        for user in users:
            webkom_group.add_user(user)
            registration = Registration.objects.get_or_create(event=event, user=user)[0]
            event.register(registration)

        self.assertEqual(event.is_full, False)

    def test_bump_on_pool_expansion(self):
        event = Event.objects.get(title="POOLS_NO_REGISTRATIONS")
        pool = event.pools.get(name="Abakusmember")
        users = get_dummy_users(event.total_capacity + 1)

        for user in users:
            AbakusGroup.objects.get(name="Webkom").add_user(user)
            registration = Registration.objects.get_or_create(event=event, user=user)[0]
            event.register(registration)

        self.assertEqual(event.waiting_registrations.count(), 1)

        pool.capacity = pool.capacity + 1
        pool.save()

        event.bump_on_pool_creation_or_expansion()

        self.assertEqual(event.waiting_registrations.count(), 0)

    def test_bump_on_pool_creation(self):
        event = Event.objects.get(title="POOLS_NO_REGISTRATIONS")
        users = get_dummy_users(event.total_capacity + 1)
        webkom_group = AbakusGroup.objects.get(name="Webkom")

        for user in users:
            webkom_group.add_user(user)
            registration = Registration.objects.get_or_create(event=event, user=user)[0]
            event.register(registration)

        self.assertEqual(event.waiting_registrations.count(), 1)

        pool = Pool.objects.create(
            name="Pool1",
            event=event,
            capacity=1,
            activation_date=timezone.now() - timedelta(days=1),
        )
        pool.permission_groups.set([webkom_group])

        event.bump_on_pool_creation_or_expansion()

        self.assertEqual(event.waiting_registrations.count(), 0)

    def test_bump_on_pool_expansion_or_creation_when_no_change(self):
        event = Event.objects.get(title="POOLS_NO_REGISTRATIONS")
        users = get_dummy_users(event.total_capacity + 1)

        for user in users:
            AbakusGroup.objects.get(name="Webkom").add_user(user)
            registration = Registration.objects.get_or_create(event=event, user=user)[0]
            event.register(registration)

        self.assertEqual(event.waiting_registrations.count(), 1)

        event.bump_on_pool_creation_or_expansion()

        self.assertEqual(event.waiting_registrations.count(), 1)

    def test_bump_on_pool_expansion_or_creation_when_no_change_post_merge(self):
        event = Event.objects.get(title="POOLS_NO_REGISTRATIONS")
        users = get_dummy_users(event.total_capacity + 1)
        event.merge_time = timezone.now() - timedelta(hours=1)
        event.save()

        for user in users:
            AbakusGroup.objects.get(name="Abakus").add_user(user)
            registration = Registration.objects.get_or_create(event=event, user=user)[0]
            event.register(registration)

        self.assertEqual(event.waiting_registrations.count(), 1)

        last_user = users[-1]
        AbakusGroup.objects.get(name="Webkom").add_user(last_user)
        event.bump_on_pool_creation_or_expansion()

        self.assertEqual(event.waiting_registrations.count(), 1)
