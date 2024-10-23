from datetime import timedelta

from django.db import transaction
from django.urls import reverse
from django.utils import timezone
from rest_framework import status

from lego.apps.achievements.constants import (
    EVENT_IDENTIFIER,
    EVENT_PRICE_IDENTIFIER,
    EVENT_RANK_IDENTIFIER,
    MEETING_IDENTIFIER,
    POLL_IDENTIFIER,
    QUOTE_IDENTIFIER,
)
from lego.apps.achievements.models import Achievement
from lego.apps.achievements.promotion import (
    check_all_promotions,
    check_event_related_single_user,
    check_poll_related_single_user,
    check_quote_related_single_user,
)
from lego.apps.events.constants import PAYMENT_SUCCESS
from lego.apps.events.models import Event, Registration
from lego.apps.events.tests.utils import get_dummy_users
from lego.apps.meetings.models import Meeting
from lego.apps.polls.models import Option, Poll
from lego.apps.quotes.models import Quote
from lego.apps.users.models import AbakusGroup, User
from lego.utils.test_utils import BaseAPITestCase, BaseTestCase


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

        check_event_related_single_user(user)
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

        check_event_related_single_user(user)
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
                check_event_related_single_user(user=user)

        main_character = User.objects.first()
        AbakusGroup.objects.get(name="Abakus").add_user(main_character)
        AbakusGroup.objects.get(name="Webkom").add_user(main_character)

        for j in range(2, 30):
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
            check_event_related_single_user(user=main_character)

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

        check_event_related_single_user(user)
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

            check_event_related_single_user(user)

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
        self.assertTrue(
            not quote_achievement.exists(),
            f"User {user.username} should not have unlocked achievement",
        )

        event_achievement = Achievement.objects.filter(
            user=user, identifier=EVENT_IDENTIFIER, level=0
        )
        self.assertTrue(
            not event_achievement.exists(),
            f"User {user.username} should not have unlocked achievement",
        )

        event_rank_0_achievement = Achievement.objects.filter(
            user=user, identifier=EVENT_RANK_IDENTIFIER, level=0
        )
        self.assertTrue(
            not event_rank_0_achievement.exists(),
            f"User {user.username} should not have unlocked achievement",
        )

        event_rank_1_achievement = Achievement.objects.filter(
            user=user, identifier=EVENT_RANK_IDENTIFIER, level=1
        )
        self.assertTrue(
            not event_rank_1_achievement.exists(),
            f"User {user.username} should not have unlocked achievement",
        )

        event_rank_2_achievement = Achievement.objects.filter(
            user=user, identifier=EVENT_RANK_IDENTIFIER, level=2
        )
        self.assertTrue(
            not event_rank_2_achievement.exists(),
            f"User {user.username} should not have unlocked achievement",
        )

        poll_achievement = Achievement.objects.filter(
            user=user, identifier=POLL_IDENTIFIER, level=0
        )
        self.assertTrue(
            not poll_achievement.exists(),
            f"User {user.username} should not have unlocked achievement",
        )

        event_price_achievement = Achievement.objects.filter(
            user=user, identifier=EVENT_PRICE_IDENTIFIER, level=0
        )
        self.assertTrue(
            not event_price_achievement.exists(),
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
