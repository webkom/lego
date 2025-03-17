from datetime import timedelta
from unittest.mock import patch

from django.db import transaction
from django.urls import reverse
from django.utils import timezone
from rest_framework import status

from lego.apps.achievements.constants import (
    EVENT_IDENTIFIER,
    EVENT_PRICE_IDENTIFIER,
    EVENT_RANK_IDENTIFIER,
    GALA_IDENTIFIER,
    GENFORS_IDENTIFIER,
    MEETING_IDENTIFIER,
    PENALTY_IDENTIFIER,
    POLL_IDENTIFIER,
    QUOTE_IDENTIFIER,
)
from lego.apps.achievements.models import Achievement
from lego.apps.achievements.promotion import (
    check_all_promotions,
    check_event_related_single_user,
    check_penalty_related_single_user,
    check_poll_related_single_user,
    check_quote_related_single_user,
    check_rank_promotions,
)
from lego.apps.achievements.tasks import run_all_promotions
from lego.apps.events.constants import PAYMENT_SUCCESS
from lego.apps.events.models import Event, Pool, Registration
from lego.apps.events.tests.utils import get_dummy_users
from lego.apps.meetings.models import Meeting
from lego.apps.polls.models import Option, Poll
from lego.apps.quotes.models import Quote
from lego.apps.users.constants import MEMBER_GROUP
from lego.apps.users.models import AbakusGroup, Penalty, User
from lego.utils.test_utils import BaseAPITestCase, BaseTestCase


def _get_registrations_list_url(event_pk):
    return reverse("api:v1:registrations-list", kwargs={"event_pk": event_pk})


class EventAchievementAPITestCase(BaseAPITestCase):
    fixtures = [
        "test_abakus_groups.yaml",
        "test_users.yaml",
        "test_multiple_events.yaml",
    ]

    def setUp(self):
        # Get or create the user and add to necessary groups
        self.user = User.objects.get(username="test1")
        AbakusGroup.objects.get(name="Abakus").add_user(self.user)
        AbakusGroup.objects.get(name="Webkom").add_user(self.user)
        Event.objects.all().update(
            start_time=timezone.now() + timedelta(hours=3),
            merge_time=timezone.now() + timedelta(hours=12),
            heed_penalties=True,
        )
        # Authenticate the user for API requests
        self.client.force_authenticate(self.user)

    def register_user_for_event(self, event):
        """
        Helper function to register the user for an event and finalize it.
        """
        pool = event.pools.first()
        pool.capacity = 55  # Ensure capacity is sufficient
        pool.save()
        registration = Registration.objects.get_or_create(event=event, user=self.user)[
            0
        ]
        event.register(registration)
        event.end_time = timezone.now() - timedelta(days=2)  # Mark as completed
        event.save()

    def test_event_count_achievement_after_api_registration(self):
        # Step 1: Register the user for 10 events using the internal helper function
        for i in range(1, 11):
            event = Event.objects.get(pk=i)
            self.register_user_for_event(event)

        # Step 2: Register the user for the 11th event using the API
        event = Event.objects.get(title="INFINITE_EVENT")

        # Perform the registration via API
        registration_response = self.client.post(
            _get_registrations_list_url(event.id),
            {"captchaResponse": "XXXX.DUMMY.TOKEN.XXXX", "feedback": ""},
        )

        self.assertEqual(
            registration_response.status_code,
            status.HTTP_202_ACCEPTED,
            "API registration should succeed for the 11th event",
        )

        # Step 3: Verify the achievement for attending 10 events is unlocked
        achievement = Achievement.objects.filter(
            user=self.user, identifier=EVENT_IDENTIFIER, level=0
        )
        self.assertTrue(
            achievement.exists(),
            "User should have unlocked the level 0 achievement for attending 10 events.",
        )


class RankPromotionTestCase(BaseTestCase):
    fixtures = [
        "test_abakus_groups.yaml",
        "test_users.yaml",
        "test_multiple_events.yaml",
    ]

    def setUp(self):
        Event.objects.all().update(
            start_time=timezone.now() + timedelta(hours=3),
            merge_time=timezone.now() + timedelta(hours=12),
            heed_penalties=True,
        )
        for i in range(1, 20):
            event = Event.objects.get(pk=i)
            pool = event.pools.first()
            pool.capacity = 55
            pool.save()

        # Get two users and assign initial rankings
        self.user1 = User.objects.get(username="test1")  # Initially rank 1
        self.user2 = User.objects.get(username="test2")  # Initially rank 2
        AbakusGroup.objects.get(name="Abakus").add_user(self.user1)
        AbakusGroup.objects.get(name="Abakus").add_user(self.user2)

        # Register user1 for more events than user2
        for i in range(1, 15):
            event = Event.objects.get(pk=i)
            registration = Registration.objects.create(event=event, user=self.user1)
            event.register(registration)
            event.end_time = timezone.now() - timezone.timedelta(days=2)
            event.save()

        for i in range(1, 10):
            event = Event.objects.get(pk=i)
            registration = Registration.objects.create(event=event, user=self.user2)
            event.register(registration)
            event.end_time = timezone.now() - timezone.timedelta(days=2)
            event.save()

        check_rank_promotions()

    def test_rank_promotion_after_more_event_registrations(self):
        """Test that a user who surpasses another in event count is promoted in rank."""
        # Ensure user1 initially holds rank 1
        self.assertTrue(
            Achievement.objects.filter(
                user=self.user1, identifier="event_rank", level=2
            ).exists(),
            "User1 should initially have rank 1 achievement",
        )
        self.assertTrue(
            Achievement.objects.filter(
                user=self.user2, identifier="event_rank", level=1
            ).exists(),
            "User2 should initially have rank 2 achievement",
        )

        # Register user2 for more events to surpass user1
        for i in range(15, 20):
            event = Event.objects.get(pk=i)
            registration = Registration.objects.create(event=event, user=self.user2)
            event.register(registration)
            event.end_time = timezone.now() - timezone.timedelta(days=2)
            event.save()

        transaction.on_commit(lambda: check_all_promotions())
        # Ensure rankings are updated
        transaction.on_commit(
            lambda: self.assertTrue(
                Achievement.objects.filter(
                    user=self.user2, identifier="event_rank", level=2
                ).exists(),
                "User2 should now have rank 1 achievement",
            )
        )

        transaction.on_commit(
            lambda: self.assertTrue(
                Achievement.objects.filter(
                    user=self.user1, identifier="event_rank_2", level=1
                ).exists(),
                "User1 should now have rank 2 achievement",
            )
        )


class GenforsAchievementTestCase(BaseTestCase):
    fixtures = [
        "test_abakus_groups.yaml",
        "test_users.yaml",
        "test_multiple_events.yaml",
    ]

    def setUp(self):
        self.user = User.objects.get(username="test1")
        AbakusGroup.objects.get(name="Abakus").add_user(self.user)

    def test_genfors_achievement_levels(self):
        """Test that users unlock achievements for attending Genfors events."""
        abakus_group = AbakusGroup.objects.get(name="Abakus")
        for i in range(55, 70):
            event = Event.objects.create(
                title=f"generalforsamling 202{i}",
                end_time=timezone.now() + timezone.timedelta(days=2),
                start_time=timezone.now() + timezone.timedelta(days=1),
            )
            pool = Pool.objects.create(
                name="Abakus",
                capacity=55,
                event=event,
                activation_date=(timezone.now() - timedelta(hours=5)),
            )
            pool.permission_groups.add(abakus_group)
            pool.save()
            registration = Registration.objects.create(event=event, user=self.user)
            event.register(registration)
            event.save()
            event.end_time = timezone.now() - timezone.timedelta(days=2)
            event.save()

        transaction.on_commit(lambda: check_all_promotions())
        transaction.on_commit(
            lambda: self.assertTrue(
                Achievement.objects.filter(
                    identifier=GENFORS_IDENTIFIER, level=4, user=self.user
                ).exists(),
                "Achievement for genfors should be unlocked",
            )
        )


class GalaAchievementTestCase(BaseTestCase):
    fixtures = [
        "test_abakus_groups.yaml",
        "test_users.yaml",
        "test_multiple_events.yaml",
    ]

    def setUp(self) -> None:
        self.user = User.objects.get(username="test1")
        AbakusGroup.objects.get(name=MEMBER_GROUP).add_user(self.user)

    def test_gala_achievement_levels(self) -> None:
        abakus_group = AbakusGroup.objects.get(name=MEMBER_GROUP)
        event_names = (
            "Halvingfest Komtek",
            "Immatrikuleringsball",
            "itDAGENE-bankett",
            "Julebord",
            "Ukom-jubileum",
        )

        for event_name in event_names:
            for i in range(69, 72):
                event = Event.objects.create(
                    title=f"{event_name} 20{i}",
                    start_time=timezone.now() + timedelta(days=1),
                    end_time=timezone.now() + timedelta(days=2),
                )
                pool = Pool.objects.create(
                    name=MEMBER_GROUP,
                    capacity=55,
                    event=event,
                    activation_date=timezone.now() - timedelta(hours=5),
                )
                pool.permission_groups.add(abakus_group)
                pool.save()
                registration = Registration.objects.create(event=event, user=self.user)
                event.register(registration)
                event.save()
                event.end_time = timezone.now() - timedelta(days=2)
                event.save()

        transaction.on_commit(check_all_promotions)
        transaction.on_commit(
            lambda: self.assertTrue(
                Achievement.objects.filter(
                    identifier=GALA_IDENTIFIER, level=3, user=self.user
                ).exists(),
                "Achievement for gala should be unlocked",
            )
        )


class AchievementTestCase(BaseTestCase):
    fixtures = [
        "test_abakus_groups.yaml",
        "test_users.yaml",
        "test_multiple_events.yaml",
        "test_quotes.yaml",
        "test_companies.yaml",
        "test_polls.yaml",
    ]

    def setUp(self):
        Event.objects.all().update(
            start_time=timezone.now() + timedelta(hours=3),
            merge_time=timezone.now() + timedelta(hours=12),
            heed_penalties=True,
        )

    def test_get_level_0_event_achievement(self):
        """Test get first level of event achievement"""
        user = get_dummy_users(1)[0]
        AbakusGroup.objects.get(name="Abakus").add_user(user)
        AbakusGroup.objects.get(name="Webkom").add_user(user)
        for i in range(1, 11):
            event = Event.objects.get(pk=i)
            pool = event.pools.first()
            pool.capacity = 55
            pool.save()
            registration = Registration.objects.get_or_create(event=event, user=user)[0]
            event.register(registration)
            event.end_time = timezone.now() - timedelta(days=2)
            event.save()

        check_event_related_single_user(user.id)
        achievement = Achievement.objects.filter(
            user=user, identifier=EVENT_IDENTIFIER, level=0
        )
        self.assertTrue(
            achievement.exists(),
            "Achievement for 10 events (level 0) should be unlocked",
        )

    def test_get_level_1_event_achievement(self):
        """Test get second level of event achievement"""
        user = get_dummy_users(1)[0]
        AbakusGroup.objects.get(name="Abakus").add_user(user)
        AbakusGroup.objects.get(name="Webkom").add_user(user)
        for i in range(1, 29):
            event = Event.objects.get(pk=i)
            pool = event.pools.first()
            pool.capacity = 55
            pool.save()
            registration = Registration.objects.get_or_create(event=event, user=user)[0]
            event.register(registration)
            event.end_time = timezone.now() - timedelta(days=2)
            event.save()

        check_event_related_single_user(user.id)
        achievement = Achievement.objects.filter(
            user=user, identifier=EVENT_IDENTIFIER, level=1
        )
        self.assertTrue(
            achievement.exists(),
            "Achievement for 25 events (level 1) should be unlocked",
        )

    def test_rank_event_achievement(self):
        """Test get first rank of event achievement"""
        users = get_dummy_users(5)
        for _, user in enumerate(users):
            AbakusGroup.objects.get(name="Abakus").add_user(user)
            AbakusGroup.objects.get(name="Webkom").add_user(user)
            # Register each user for 1 event to unlock the achievement
            for j in range(1, 2):
                event = Event.objects.get(pk=j)
                pool = event.pools.first()
                pool.capacity = 55
                pool.save()
                registration = Registration.objects.get_or_create(
                    event=event, user=user
                )[0]
                event.register(registration)
                event.end_time = timezone.now() - timedelta(days=2)
                event.save()
                check_event_related_single_user(user.id)

        main_character = User.objects.first()
        AbakusGroup.objects.get(name="Abakus").add_user(main_character)
        AbakusGroup.objects.get(name="Webkom").add_user(main_character)

        for j in range(2, 20):
            event = Event.objects.get(pk=j)
            pool = event.pools.first()
            pool.capacity = 55
            pool.save()
            registration = Registration.objects.get_or_create(
                event=event, user=main_character
            )[0]
            event.register(registration)
            event.end_time = timezone.now() - timedelta(days=2)
            event.save()
            check_event_related_single_user(main_character.id)

        # Ensure all promotions are processed before checking achievements
        transaction.on_commit(lambda: check_all_promotions())

        # After the transaction completes, verify the achievement
        transaction.on_commit(
            lambda: self.assertTrue(
                Achievement.objects.filter(
                    identifier=EVENT_RANK_IDENTIFIER, level=2, user=main_character
                ).exists(),
                "Achievement for rank 1 should be unlocked",
            )
        )

    def test_lose_rank_event_achievement(self):
        """Test achievement rank loss when another user overtakes."""
        users = get_dummy_users(5)

        # Register initial users to unlock the achievement
        for _, user in enumerate(users):
            AbakusGroup.objects.get(name="Abakus").add_user(user)
            AbakusGroup.objects.get(name="Webkom").add_user(user)
            # Register each user for 1 event to unlock a base achievement
            for j in range(1, 2):
                event = Event.objects.get(pk=j)
                pool = event.pools.first()
                pool.capacity = 55
                pool.save()
                registration = Registration.objects.get_or_create(
                    event=event, user=user
                )[0]
                event.register(registration)
                event.end_time = timezone.now() - timedelta(days=2)
                event.save()
                check_event_related_single_user(user.id)

        # Main character who initially earns the rank achievement
        main_character = User.objects.first()
        AbakusGroup.objects.get(name="Abakus").add_user(main_character)
        AbakusGroup.objects.get(name="Webkom").add_user(main_character)

        # Register main_character for multiple events to gain higher rank achievement
        for j in range(2, 20):
            event = Event.objects.get(pk=j)
            pool = event.pools.first()
            pool.capacity = 55
            pool.save()
            registration = Registration.objects.get_or_create(
                event=event, user=main_character
            )[0]
            event.register(registration)
            event.end_time = timezone.now() - timedelta(days=2)
            event.save()
            check_event_related_single_user(main_character.id)

        # Commit transaction to apply rank achievement for main_character
        transaction.on_commit(lambda: check_all_promotions())

        # Verify main_character initially has rank achievement
        transaction.on_commit(
            lambda: self.assertTrue(
                Achievement.objects.filter(
                    identifier=EVENT_RANK_IDENTIFIER, level=2, user=main_character
                ).exists(),
                "Achievement for rank 1 should be unlocked for main_character",
            )
        )

        # Second character who will overtake the main_character
        second_character = User.objects.get(pk=2)
        AbakusGroup.objects.get(name="Abakus").add_user(second_character)
        AbakusGroup.objects.get(name="Webkom").add_user(second_character)

        # Register second_character for events to match or exceed main_character's rank
        for j in range(2, 30):
            event = Event.objects.get(pk=j)
            pool = event.pools.first()
            pool.capacity = 55
            pool.save()
            registration = Registration.objects.get_or_create(
                event=event, user=second_character
            )[0]
            event.register(registration)
            event.end_time = timezone.now() - timedelta(days=2)
            event.save()
            check_event_related_single_user(second_character.id)

        # Commit transaction to apply rank achievement for second_character
        transaction.on_commit(lambda: check_all_promotions())

        # Verify second_character has achieved rank and main_character has lost it
        transaction.on_commit(
            lambda: (
                self.assertTrue(
                    Achievement.objects.filter(
                        identifier=EVENT_RANK_IDENTIFIER, level=2, user=second_character
                    ).exists(),
                    "Achievement for rank 1 should be unlocked for second_character",
                ),
                self.assertFalse(
                    Achievement.objects.filter(
                        identifier=EVENT_RANK_IDENTIFIER, level=2, user=main_character
                    ).exists(),
                    "Achievement for rank 1 should be removed from main_character",
                ),
            )
        )

    def test_money_spent_achievement(self):
        """Test get money spent achievements"""
        user = get_dummy_users(1)[0]
        AbakusGroup.objects.get(name="Abakus").add_user(user)
        AbakusGroup.objects.get(name="Webkom").add_user(user)
        for i in range(1, 29):
            event = Event.objects.get(pk=i)
            pool = event.pools.first()
            pool.capacity = 55
            pool.save()
            registration = Registration.objects.get_or_create(
                event=event,
                user=user,
                payment_amount=500000,
                payment_status=PAYMENT_SUCCESS,
            )[0]
            event.register(registration)
            event.end_time = timezone.now() - timedelta(days=2)
            event.is_priced = True
            event.save()

        check_event_related_single_user(user.id)
        achievement = Achievement.objects.filter(
            user=user, identifier=EVENT_PRICE_IDENTIFIER, level=2
        )
        self.assertTrue(
            achievement.exists(), "Achievement for 10K paid should be unlocked"
        )

    def test_poll_achievement(self):
        """Test get poll achievement"""
        user = get_dummy_users(1)[0]
        AbakusGroup.objects.get(name="Abakus").add_user(user)
        AbakusGroup.objects.get(name="Webkom").add_user(user)
        for _ in range(1, 27):
            poll = Poll.objects.create()
            option = Option.objects.create(poll=poll)
            poll.save()
            option.save()
            poll.vote(user=user, option_id=option.id)

        check_poll_related_single_user(user)
        achievement = Achievement.objects.filter(
            user=user, identifier=POLL_IDENTIFIER, level=1
        )
        self.assertTrue(
            achievement.exists(), "Achievement for 25 answered polls should be unlocked"
        )

    def test_penalty_achievement(self) -> None:
        """Test penalty achievement based on event attendance and penalty history."""
        now = timezone.now()
        user = get_dummy_users(1)[0]
        AbakusGroup.objects.get(name="Abakus").add_user(user)
        AbakusGroup.objects.get(name="Webkom").add_user(user)
        grade1 = AbakusGroup.objects.create(
            name="1. klasse Datateknologi", type="klasse"
        )
        grade1.add_user(user)

        # Initial check: No achievements should be awarded, as the user attended no events
        check_penalty_related_single_user(user)
        self.assertFalse(
            Achievement.objects.filter(
                user=user, identifier=PENALTY_IDENTIFIER, level=0
            ).exists(),
            "User should not have unlocked the achievement as they have not attended any events.",
        )

        # Create events in the future and attach an open pool for registration
        events = []
        for _, __ in enumerate((1, 185, 450), 1):
            # Initially set event times in the future
            event = Event.objects.create(
                start_time=now + timedelta(days=30), end_time=now + timedelta(days=31)
            )
            # Attach a pool that allows registration
            pool = Pool.objects.create(
                capacity=69, activation_date=now - timedelta(days=1), event=event
            )
            pool.permission_groups.add(grade1)
            pool.save()
            events.append(event)

        # Register user for the first and third events while they are in the future
        for idx in (0, 2):
            event = events[idx]
            registration, _ = Registration.objects.get_or_create(event=event, user=user)
            event.register(registration)
            event.save()

        # Move the first and third events to the past to simulate that they already took place
        for i, days in zip((0, 2), (1, 450), strict=True):
            event = events[i]
            event.start_time = now - timedelta(days=days + 1)
            event.end_time = now - timedelta(days=days)
            event.save()

        # Move the second event to the future for registration, then move it to the past
        event = events[1]
        event.start_time = now + timedelta(days=30)
        event.end_time = now + timedelta(days=31)
        event.save()

        # Register user for the second event while it is in the future
        registration, _ = Registration.objects.get_or_create(event=event, user=user)
        event.register(registration)
        event.save()

        # Now move the second event back to simulate it took place 185 days ago
        event.start_time = now - timedelta(days=185 + 1)
        event.end_time = now - timedelta(days=185)
        event.save()

        # Check that the achievement is now awarded for going a year without penalties
        check_penalty_related_single_user(user)
        self.assertTrue(
            Achievement.objects.filter(
                user=user, identifier=PENALTY_IDENTIFIER, level=0
            ).exists(),
            """User should have unlocked the achievement
            as events are within a year and no penalties exist.""",
        )

        # Add a penalty within the last year, which should revoke the achievement
        penalty = Penalty.objects.create(
            user=user,
            reason="Ran beside the Olympic swimming pool holding scissors.",
            source_event=events[1],
        )
        penalty.created_at = now - timedelta(days=100)
        penalty.save()

        achievement = Achievement.objects.get(
            user=user, identifier=PENALTY_IDENTIFIER, level=0
        )
        achievement.delete(force=True)
        check_penalty_related_single_user(user)
        self.assertFalse(
            Achievement.objects.filter(
                user=user, identifier=PENALTY_IDENTIFIER, level=0
            ).exists(),
            "User should not have the achievement due to receiving a penalty within the last year.",
        )

        penalty.created_at = now - timedelta(days=400)
        penalty.save()

        # Recheck achievement status after updating the penalty date
        check_penalty_related_single_user(user)
        self.assertTrue(
            Achievement.objects.filter(
                user=user, identifier=PENALTY_IDENTIFIER, level=0
            ).exists(),
            """User should have unlocked the achievement
            for going a year without receiving a penalty.""",
        )

    def test_achievement_percentage(self):
        """Test that the percentage calculation."""
        # Create multiple users
        users = get_dummy_users(5)
        for _, user in enumerate(users):
            AbakusGroup.objects.get(name="Abakus").add_user(user)
            AbakusGroup.objects.get(name="Webkom").add_user(user)
            # Register each user for 10 events to unlock the achievement
            for j in range(1, 11):
                event = Event.objects.get(pk=j)
                pool = event.pools.first()
                pool.capacity = 55
                pool.save()
                registration = Registration.objects.get_or_create(
                    event=event, user=user
                )[0]
                event.register(registration)
                event.end_time = timezone.now() - timedelta(days=2)
                event.save()

            check_event_related_single_user(user.id)

        # Check if all users have unlocked the achievement for 10 events (level 0)
        for user in users:
            achievement = Achievement.objects.filter(
                user=user, identifier=EVENT_IDENTIFIER, level=0
            )
            self.assertTrue(
                achievement.exists(),
                f"User {user.username} should have unlocked level 0 achievement",
            )

        # Check the percentage of users who unlocked the achievement
        first_user_achievement = Achievement.objects.get(
            user=users[0], identifier=EVENT_IDENTIFIER, level=0
        )
        expected_percentage = first_user_achievement.percentage

        # There are 5 users, and all 5 have unlocked the achievement, so it should be 100%
        self.assertEqual(
            expected_percentage,
            (5 / len(User.objects.all())) * 100,
            "Percentage of users unlocking the achievement should be correct",
        )

    def test_get_quote_achievement(self):
        """Test registering user to event with a single unlimited pool"""
        user = get_dummy_users(1)[0]
        AbakusGroup.objects.get(name="Abakus").add_user(user)
        AbakusGroup.objects.get(name="Webkom").add_user(user)
        Quote.objects.get_or_create(
            created_by=user, approved=True, source="Jonas", text="Hei"
        )
        check_quote_related_single_user(user=user)
        achievement = Achievement.objects.filter(
            user=user, identifier=QUOTE_IDENTIFIER, level=0
        )
        self.assertTrue(
            achievement.exists(),
            f"User {user.username} should have unlocked level 0 achievement",
        )

    def test_does_not_get_any_achievements(self):
        """User does not get achievement when does not do anything"""
        user = get_dummy_users(1)[0]
        AbakusGroup.objects.get(name="Abakus").add_user(user)
        AbakusGroup.objects.get(name="Webkom").add_user(user)

        check_all_promotions()

        quote_achievement = Achievement.objects.filter(
            user=user, identifier=QUOTE_IDENTIFIER, level=0
        )
        self.assertFalse(
            quote_achievement.exists(),
            f"User {user.username} should not have unlocked achievement",
        )

        event_achievement = Achievement.objects.filter(
            user=user, identifier=EVENT_IDENTIFIER, level=0
        )
        self.assertFalse(
            event_achievement.exists(),
            f"User {user.username} should not have unlocked achievement",
        )

        event_rank_0_achievement = Achievement.objects.filter(
            user=user, identifier=EVENT_RANK_IDENTIFIER, level=0
        )
        self.assertFalse(
            event_rank_0_achievement.exists(),
            f"User {user.username} should not have unlocked achievement",
        )

        event_rank_1_achievement = Achievement.objects.filter(
            user=user, identifier=EVENT_RANK_IDENTIFIER, level=1
        )
        self.assertFalse(
            event_rank_1_achievement.exists(),
            f"User {user.username} should not have unlocked achievement",
        )

        event_rank_2_achievement = Achievement.objects.filter(
            user=user, identifier=EVENT_RANK_IDENTIFIER, level=2
        )
        self.assertFalse(
            event_rank_2_achievement.exists(),
            f"User {user.username} should not have unlocked achievement",
        )

        poll_achievement = Achievement.objects.filter(
            user=user, identifier=POLL_IDENTIFIER, level=0
        )
        self.assertFalse(
            poll_achievement.exists(),
            f"User {user.username} should not have unlocked achievement",
        )

        event_price_achievement = Achievement.objects.filter(
            user=user, identifier=EVENT_PRICE_IDENTIFIER, level=0
        )
        self.assertFalse(
            event_price_achievement.exists(),
            f"User {user.username} should not have unlocked achievement",
        )


def _get_list_url():
    return reverse("api:v1:meeting-list")


def _get_detail_url(pk):
    return reverse("api:v1:meeting-detail", kwargs={"pk": pk})


class SelfInviteTestCase(BaseAPITestCase):
    fixtures = [
        "test_abakus_groups.yaml",
        "test_users.yaml",
        "test_meetings.yaml",
    ]

    def setUp(self):
        self.abakommer = User.objects.get(username="abakommer")
        AbakusGroup.objects.get(name="Abakom").add_user(self.abakommer)

        # Create a new meeting where only the creator (self.abakommer) is part of
        self.client.force_authenticate(user=self.abakommer)
        res = self.client.post(
            _get_list_url(),
            {
                "title": "Self Invite Test Meeting",
                "location": "Plebkom",
                "report": "<p>Self invite test report</p>",
                "start_time": "2024-10-23T13:20:30Z",
                "end_time": "2024-10-23T14:00:30Z",
            },
        )
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.meeting = Meeting.objects.get(pk=res.data["id"])

    def test_self_invite_using_bulk_invite(self):
        """Test inviting oneself to a meeting using the bulk_invite API."""
        # Authenticate as the creator
        self.client.force_authenticate(user=self.abakommer)

        # Use bulk_invite to invite the creator to the meeting
        res = self.client.post(
            _get_detail_url(self.meeting.id) + "bulk_invite/",
            {
                "groups": [],
                "users": [self.abakommer.id],
            },  # Inviting only the creator (themselves)
        )

        # Verify that the invite was successful
        self.assertEqual(res.status_code, status.HTTP_200_OK)

        # Check that the creator is now invited to the meeting
        is_invited = self.meeting.invited_users.filter(id=self.abakommer.id).exists()
        self.assertTrue(
            is_invited,
            "The creator should be successfully invited to their own meeting.",
        )
        achievement = Achievement.objects.filter(
            user=self.abakommer, identifier=MEETING_IDENTIFIER, level=0
        )
        self.assertTrue(
            achievement.exists(),
            f"User {self.abakommer.username} should have unlocked meeting achievement",
        )

    def test_does_not_get_meeting_achievements(self):
        """User does not get achievement when does not do anything"""
        user = get_dummy_users(1)[0]
        AbakusGroup.objects.get(name="Abakus").add_user(user)
        AbakusGroup.objects.get(name="Webkom").add_user(user)

        check_all_promotions()

        meeting_achievement = Achievement.objects.filter(
            user=user, identifier=MEETING_IDENTIFIER, level=0
        )
        self.assertTrue(
            not meeting_achievement.exists(),
            f"User {user.username} should not have unlocked achievement",
        )


class RunAllPromotionsTestCase(BaseTestCase):
    fixtures = [
        "test_abakus_groups.yaml",
        "test_users.yaml",
        "test_multiple_events.yaml",
    ]

    def setUp(self):
        # Setup a user and register them to events to be eligible for an achievement
        self.user = User.objects.get(username="test1")
        AbakusGroup.objects.get(name="Abakus").add_user(self.user)
        AbakusGroup.objects.get(name="Webkom").add_user(self.user)
        Event.objects.all().update(
            start_time=timezone.now() + timedelta(hours=3),
            merge_time=timezone.now() + timedelta(hours=12),
            heed_penalties=True,
        )
        # Register the user for 10 events to qualify for a level 0 achievement
        for j in range(1, 11):
            event = Event.objects.get(pk=j)
            pool = event.pools.first()
            pool.capacity = 55
            pool.save()
            registration = Registration.objects.get_or_create(
                event=event, user=self.user
            )[0]
            event.register(registration)
            event.end_time = timezone.now() - timedelta(days=2)
            event.save()

    @patch("lego.apps.achievements.tasks.check_all_promotions")
    def test_run_all_promotions_task_invokes_check_all_promotions(
        self, mock_check_all_promotions
    ):
        """Test that the run_all_promotions task calls check_all_promotions"""
        run_all_promotions.apply()  # Trigger the task

        # Verify that check_all_promotions was called within the task
        mock_check_all_promotions.assert_called_once()

    def test_run_all_promotions_awards_achievement(self):
        """Test that the task awards achievements to eligible users"""
        # Run the task to check for achievements
        run_all_promotions.apply()

        # Verify the user received the level 0 event achievement
        achievement = Achievement.objects.filter(
            user=self.user, identifier=EVENT_IDENTIFIER, level=0
        )
        self.assertTrue(
            achievement.exists(),
            "User should have unlocked level 0 event achievement after task run.",
        )


class SimultaneousEventRegistrationAPITestCase(BaseAPITestCase):
    fixtures = [
        "test_abakus_groups.yaml",
        "test_users.yaml",
        "test_multiple_events.yaml",
    ]

    def setUp(self):
        # Set up a test user and add them to the necessary groups
        self.user = User.objects.get(username="test1")
        AbakusGroup.objects.get(name="Abakus").add_user(self.user)
        AbakusGroup.objects.get(name="Webkom").add_user(self.user)
        Event.objects.all().update(
            start_time=timezone.now() + timedelta(hours=3),
            merge_time=timezone.now() + timedelta(hours=12),
            heed_penalties=True,
        )

        # Authenticate the user for API requests
        self.client.force_authenticate(self.user)

        # Register the user for 10 events programmatically
        for i in range(1, 11):
            event = Event.objects.get(pk=i)
            pool = event.pools.first()
            pool.capacity = 55
            pool.save()
            registration = Registration.objects.get_or_create(
                event=event, user=self.user
            )[0]
            event.register(registration)
            event.end_time = timezone.now() - timedelta(days=2)
            event.save()

    def _get_registrations_list_url(self, event_pk):
        return reverse("api:v1:registrations-list", kwargs={"event_pk": event_pk})

    def test_simultaneous_event_registration_for_single_achievement(self):
        """Test that simultaneous API registrations result in a single event achievement"""

        # Prepare two events for simultaneous registration via API
        event1 = Event.objects.get(pk=11)
        event2 = Event.objects.get(pk=12)

        def register_user_via_api(event):
            response = self.client.post(
                self._get_registrations_list_url(event.id),
                {"captchaResponse": "XXXX.DUMMY.TOKEN.XXXX", "feedback": ""},
            )
            return response

        # Register for two events simultaneously using API
        res1 = register_user_via_api(event1)
        res2 = register_user_via_api(event2)

        # Check that both API responses are accepted
        self.assertEqual(
            res1.status_code,
            status.HTTP_202_ACCEPTED,
            "First API registration should succeed",
        )
        self.assertEqual(
            res2.status_code,
            status.HTTP_202_ACCEPTED,
            "Second API registration should succeed",
        )

        # Verify only one event-count achievement is unlocked
        achievements = Achievement.objects.filter(
            user=self.user, identifier=EVENT_IDENTIFIER, level=0
        )
        self.assertEqual(
            achievements.count(),
            1,
            "User should only have a single event-count achievement",
        )
