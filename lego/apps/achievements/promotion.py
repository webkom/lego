from django.db import transaction
from django.db.models import Count
from django.utils import timezone

from lego.apps.achievements.constants import (
    COMPLETE_ACHIEVEMENT,
    COMPLETE_IDENTIFIER,
    EVENT_ACHIEVEMENTS,
    EVENT_IDENTIFIER,
    EVENT_PRICE_ACHIEVEMENTS,
    EVENT_PRICE_IDENTIFIER,
    EVENT_RANK_ACHIEVEMENTS,
    GALA_ACHIEVEMENTS,
    GALA_IDENTIFIER,
    GENFORS_ACHIEVEMENTS,
    GENFORS_IDENTIFIER,
    MEETING_ACHIEVEMENTS,
    PENALTY_ACHIEVEMENTS,
    PENALTY_IDENTIFIER,
    POLL_ACHIEVEMENTS,
    POLL_IDENTIFIER,
    QUOTE_ACHIEVEMENTS,
    QUOTE_IDENTIFIER,
    AchievementCollection,
)
from lego.apps.achievements.models import Achievement
from lego.apps.events.constants import SUCCESS_REGISTER
from lego.apps.events.models import Registration
from lego.apps.meetings.models import Meeting
from lego.apps.users.models import User


def check_leveled_promotions(
    user_id: int, identifier: str, input_achievements: AchievementCollection
) -> None:
    try:
        user = User.objects.get(pk=user_id)
    except User.DoesNotExist:
        return

    with transaction.atomic():
        current_achievement = (
            Achievement.objects.select_for_update()
            .filter(user=user, identifier=identifier)
            .first()
        )

        if not current_achievement:
            level = 0
            initial_achievement_key = next(
                (
                    key
                    for key, data in input_achievements.items()
                    if data.get("identifier") == identifier
                    and data.get("level") == level
                ),
                None,
            )

            if initial_achievement_key and input_achievements[initial_achievement_key][
                "requirement_function"
            ](user):
                current_achievement, _ = Achievement.objects.get_or_create(
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
                status=SUCCESS_REGISTER,
                event__end_time__lte=timezone.now(),
                pool__isnull=False,
            )
            .values("user")
            .annotate(event_count=Count("id"))
            .order_by("-event_count")[:3]
        )
        # Map user IDs to their rank (1, 2, or 3)
        return {entry["user"]: idx + 1 for idx, entry in enumerate(top_users)}

    # Define a mapping from rank numbers to achievement keys
    rank_to_key = {
        1: "event_rank_1",
        2: "event_rank_2",
        3: "event_rank_3",
    }

    current_top_ranks = get_top_rank_users()
    for user in User.objects.all():
        user_rank = current_top_ranks.get(user.id)
        if user_rank:
            rank_key = rank_to_key[user_rank]  # Get the corresponding achievement key
            rank_data = EVENT_RANK_ACHIEVEMENTS[rank_key]
            achievement_exists = Achievement.objects.filter(
                identifier=rank_data["identifier"], user=user
            ).exists()

            # Grant the achievement if the user does not have it
            if not achievement_exists:
                Achievement.objects.get_or_create(
                    identifier=rank_data["identifier"],
                    level=rank_data["level"],
                    user=user,
                )
            # The achiv exists so we update instead
            else:
                Achievement.objects.filter(
                    identifier=rank_data["identifier"], user=user
                ).update(level=rank_data["level"])
        else:
            # If the user is not in top 3, remove their rank achievements if they have any
            for _, rank_data in EVENT_RANK_ACHIEVEMENTS.items():
                achievement_exists = Achievement.objects.filter(
                    identifier=rank_data["identifier"],
                    level=rank_data["level"],
                    user=user,
                ).exists()

                if achievement_exists:
                    Achievement.objects.filter(
                        identifier=rank_data["identifier"],
                        level=rank_data["level"],
                        user=user,
                    ).delete(force=True)


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


def check_event_related_single_user(user_id: int) -> None:
    check_leveled_promotions(user_id, EVENT_IDENTIFIER, EVENT_ACHIEVEMENTS)
    check_leveled_promotions(user_id, EVENT_PRICE_IDENTIFIER, EVENT_PRICE_ACHIEVEMENTS)


def check_poll_related_single_user(user: User) -> None:
    check_leveled_promotions(user.id, POLL_IDENTIFIER, POLL_ACHIEVEMENTS)


def check_quote_related_single_user(user: User) -> None:
    check_leveled_promotions(user.id, QUOTE_IDENTIFIER, QUOTE_ACHIEVEMENTS)


def check_penalty_related_single_user(user: User) -> None:
    check_leveled_promotions(user.id, PENALTY_IDENTIFIER, PENALTY_ACHIEVEMENTS)


def check_genfors_related_single_user(user: User) -> None:
    check_leveled_promotions(user.id, GENFORS_IDENTIFIER, GENFORS_ACHIEVEMENTS)


def check_gala_related_single_user(user: User) -> None:
    check_leveled_promotions(user.id, GALA_IDENTIFIER, GALA_ACHIEVEMENTS)


def check_complete_user_profile(user: User) -> None:
    check_leveled_promotions(user.id, COMPLETE_IDENTIFIER, COMPLETE_ACHIEVEMENT)


def check_all_promotions() -> None:
    for user in User.objects.all():
        check_quote_related_single_user(user)
        check_event_related_single_user(user.id)
        check_poll_related_single_user(user)
        check_penalty_related_single_user(user)
        check_genfors_related_single_user(user)
        check_complete_user_profile(user)

    check_rank_promotions()
