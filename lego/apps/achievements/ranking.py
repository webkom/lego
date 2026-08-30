from django.db.models import Count, Q
from django.utils import timezone

from lego.apps.achievements.constants import RankType
from lego.apps.achievements.models import Achievement, RankSnapshot
from lego.apps.achievements.utils.calculation_utils import (
    ACHIEVEMENT_RARITIES,
    achievement_score_percentage,
)
from lego.apps.events.constants import SUCCESS_REGISTER
from lego.apps.users.models import User


def _ordered_values_for(rank_type: str):
    if rank_type == RankType.ACHIEVEMENT_SCORE:
        return (
            User.objects.filter(achievements__isnull=False)
            .distinct()
            .order_by("-achievements_score")
            .values_list("id", "achievements_score")
        )
    if rank_type == RankType.EVENT_COUNT:
        return (
            User.objects.annotate(
                event_count=Count(
                    "registrations",
                    filter=Q(
                        registrations__status=SUCCESS_REGISTER,
                        registrations__event__end_time__lte=timezone.now(),
                        registrations__pool__isnull=False,
                    ),
                )
            )
            .order_by("-event_count")
            .values_list("id", "event_count")
        )
    raise ValueError(f"Unknown rank type: {rank_type}")


def _compute_ranks(users_ordered_by_value):
    rank = 0
    prev_value = None
    for i, (user_id, value) in enumerate(users_ordered_by_value, start=1):
        if value != prev_value:
            rank = i
        prev_value = value
        yield user_id, rank, value


def latest_snapshot_values(
    rank_type: str, field: str, **filters
) -> dict[int, int | float]:
    """
    {user_id: <field>} from each user's most recent RankSnapshot matching
    the given filters. RankSnapshot is a sparse history - a row only exists
    when a user's rank/value actually changed - so "the most recent row
    matching these filters" correctly answers "what was this field as of
    that filter" even when a user has no row exactly on a given date.
    """
    return dict(
        RankSnapshot.objects.filter(type=rank_type, **filters)
        .order_by("user_id", "-date")
        .distinct("user_id")
        .values_list("user_id", field)
    )


def snapshot_rank_type(rank_type: str) -> int:
    today = timezone.now().date()

    latest_by_user = latest_snapshot_values(rank_type, "rank")

    to_create = [
        RankSnapshot(
            user_id=user_id, type=rank_type, rank=rank, value=value, date=today
        )
        for user_id, rank, value in _compute_ranks(_ordered_values_for(rank_type))
        if latest_by_user.get(user_id) != rank
    ]

    RankSnapshot.objects.filter(type=rank_type, date=today).delete()
    RankSnapshot.objects.bulk_create(to_create)
    return len(to_create)


def current_values_for(rank_type: str) -> dict[int, float]:
    """
    Return {user_id: current value} for the given rank type. Deliberately
    sourced from cheap, already-indexed columns rather than a live query -
    achievements_score is stored directly on User, and event_count is read
    from the daily RankSnapshot cache instead of aggregating Registrations
    on every request (see the cost comment on LeaderBoardViewSet.get_queryset).
    """
    if rank_type == RankType.ACHIEVEMENT_SCORE:
        return {
            user_id: achievement_score_percentage(score)
            for user_id, score in User.objects.filter(
                achievements__isnull=False
            ).values_list("id", "achievements_score")
        }
    if rank_type == RankType.EVENT_COUNT:
        return latest_snapshot_values(rank_type, "value", value__gt=0)
    raise ValueError(f"Unknown rank type: {rank_type}")


def build_histogram(values: list[float], bin_count: int = 10) -> list[dict]:
    """Bucket values into bin_count equal-width bins covering [min, max]."""
    if not values:
        return []

    lo, hi = min(values), max(values)
    if lo == hi:
        return [{"min": lo, "max": hi, "count": len(values)}]

    bin_size = (hi - lo) / bin_count
    counts = [0] * bin_count
    for value in values:
        index = min(int((value - lo) / bin_size), bin_count - 1)
        counts[index] += 1

    return [
        {"min": lo + i * bin_size, "max": lo + (i + 1) * bin_size, "count": count}
        for i, count in enumerate(counts)
    ]


def rarity_percentage(identifier: str, min_level: int = 0) -> float:
    """
    % of users who have earned `identifier` at level >= min_level (unrounded).
    Shared by Achievement.percentage (single instance) and
    rarity_by_identifier_and_level (bulk, one query per request instead of one
    query per achievement level).
    """
    total_users = User.objects.count() or 1
    achievers = (
        Achievement.objects.filter(identifier=identifier, level__gte=min_level)
        .values("user")
        .distinct()
        .count()
    )
    return achievers / total_users * 100


def rarity_by_identifier_and_level() -> list[dict]:
    """
    % of users who have earned each achievement identifier, per level,
    cumulative (>= that level) - matching rarity_percentage's semantics for
    every defined level, in one query instead of one per (identifier, level).

    A user has at most one Achievement row per identifier - level is updated
    in place as they're promoted (see promotion.py) rather than a new row
    being added per level - so summing the exact-level counts from the top
    level down gives the same "at least this level" percentage as filtering
    level__gte would, without querying per level.
    """
    total_users = User.objects.count() or 1
    exact_counts = {
        (row["identifier"], row["level"]): row["count"]
        for row in Achievement.objects.values("identifier", "level").annotate(
            count=Count("user", distinct=True)
        )
    }

    results = []
    for identifier, rarity_list in ACHIEVEMENT_RARITIES.items():
        cumulative_by_level = []
        cumulative = 0
        for level in reversed(range(len(rarity_list))):
            cumulative += exact_counts.get((identifier, level), 0)
            cumulative_by_level.append(cumulative)
        cumulative_by_level.reverse()

        results.extend(
            {
                "identifier": identifier,
                "level": level,
                "percentage": round(cumulative / total_users * 100, 2),
            }
            for level, cumulative in enumerate(cumulative_by_level)
        )
    return results


def rarity_lookup() -> dict[tuple[str, int], float]:
    """
    {(identifier, level): percentage} for every defined achievement level -
    pass this via serializer context (see AchievementSerializer.get_percentage)
    to serialize a list of achievements in 2 queries total instead of 2 per
    achievement.
    """
    return {
        (row["identifier"], row["level"]): row["percentage"]
        for row in rarity_by_identifier_and_level()
    }
