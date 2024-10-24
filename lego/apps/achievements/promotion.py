from django.db.models import Count
from django.utils import timezone

from lego.apps.achievements.models import Achievement
from lego.apps.events.constants import SUCCESS_REGISTER
from lego.apps.events.models import Registration
from lego.apps.meetings.models import Meeting
from lego.apps.users.models import User

from .constants import (
    EVENT_ACHIEVEMENTS,
    EVENT_IDENTIFIER,
    EVENT_PRICE_ACHIEVEMENTS,
    EVENT_PRICE_IDENTIFIER,
    EVENT_RANK_ACHIEVEMENTS,
    MEETING_ACHIEVEMENTS,
    POLL_ACHIEVEMENTS,
    POLL_IDENTIFIER,
    QUOTE_ACHIEVEMENTS,
    QUOTE_IDENTIFIER,
    AchievementCollection,
)


def check_leveled_promotions(
    user: User, identifier: str, input_achievements: AchievementCollection
):
    current_achievement = Achievement.objects.filter(
        user=user, identifier=identifier
    ).first()

    if not current_achievement:
        level = 0
        initial_achievement_key = next(
            (
                key
                for key, data in input_achievements.items()
                if data.get("identifier") == identifier and data.get("level") == level
            ),
            None,
        )

        if initial_achievement_key and input_achievements[initial_achievement_key][
            "requirement_function"
        ](user):
            current_achievement = Achievement.objects.create(
                user=user,
                identifier=identifier,
                level=level,
            )
        else:
            return

    next_level = current_achievement.level + 1

    while True:
        next_achievement_key = next(
            (
                key
                for key, data in input_achievements.items()
                if data.get("identifier") == identifier
                and data.get("level") == next_level
            ),
            None,
        )

        if not next_achievement_key:
            break

        next_achievement_data = input_achievements[next_achievement_key]

        if next_achievement_data["requirement_function"](user):
            current_achievement.level = next_level
            current_achievement.save()
            next_level += 1
        else:
            break


def check_rank_promotions():
    def get_top_rank_users() -> dict:
        top_users = list(
            Registration.objects.filter(
                status=SUCCESS_REGISTER, event__end_time__lte=timezone.now()
            )
            .values("user")
            .annotate(event_count=Count("id"))
            .order_by("-event_count")[:3]
        )
        # Map user IDs to their rank (1, 2, or 3)
        return {entry["user"]: idx + 1 for idx, entry in enumerate(top_users)}

    current_top_ranks = get_top_rank_users()
    for user in User.objects.all():
        for rank, rank_key in enumerate(EVENT_RANK_ACHIEVEMENTS.keys(), start=1):
            rank_data = EVENT_RANK_ACHIEVEMENTS[rank_key]
            achievement_exists = Achievement.objects.filter(
                identifier=rank_data["identifier"], level=rank_data["level"], user=user
            ).exists()

            if current_top_ranks.get(user.id) == rank:
                if not achievement_exists:
                    Achievement.objects.create(
                        identifier=rank_data["identifier"],
                        level=rank_data["level"],
                        user=user,
                    )
            else:
                if achievement_exists:
                    Achievement.objects.filter(
                        identifier=rank_data["identifier"],
                        level=rank_data["level"],
                        user=user,
                    ).delete()


def check_meeting_hidden(owner: User, user: User, meeting: Meeting):
    if owner == user and meeting.invited_users.count() == 1:
        if not Achievement.objects.filter(
            user=user, identifier=MEETING_ACHIEVEMENTS["meeting_hidden"]["identifier"]
        ).exists():

            Achievement.objects.create(
                identifier=MEETING_ACHIEVEMENTS["meeting_hidden"]["identifier"],
                user=user,
                level=MEETING_ACHIEVEMENTS["meeting_hidden"]["level"],
            )
        return True
    return False


def check_event_related_single_user(user: User):
    check_leveled_promotions(user, EVENT_IDENTIFIER, EVENT_ACHIEVEMENTS)
    check_leveled_promotions(user, EVENT_PRICE_IDENTIFIER, EVENT_PRICE_ACHIEVEMENTS)


def check_poll_related_single_user(user: User):
    check_leveled_promotions(user, POLL_IDENTIFIER, POLL_ACHIEVEMENTS)


def check_quote_related_single_user(user: User):
    check_leveled_promotions(user, QUOTE_IDENTIFIER, QUOTE_ACHIEVEMENTS)


def check_all_promotions():
    for user in User.objects.all():
        check_quote_related_single_user(user)
        check_event_related_single_user(user)
        check_poll_related_single_user(user)
    check_rank_promotions()
