from django.db.models import Count
from django.utils import timezone

from lego.apps.achievements.constants import RankType
from lego.apps.achievements.models import RankSnapshot
from lego.apps.users.models import User


def _ordered_values_for(rank_type: str):
    if rank_type == RankType.ACHIEVEMENT_SCORE:
        return (
            User.objects.filter(achievements__isnull=False)
            .order_by("-achievements_score")
            .values_list("id", "achievements_score")
        )
    if rank_type == RankType.EVENT_COUNT:
        return (
            User.objects.annotate(event_count=Count("registrations"))
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


def snapshot_rank_type(rank_type: str) -> int:
    today = timezone.now().date()

    latest_by_user = dict(
        RankSnapshot.objects.filter(type=rank_type)
        .order_by("user_id", "-date")
        .distinct("user_id")
        .values_list("user_id", "rank")
    )

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
