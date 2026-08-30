import heapq
from datetime import timedelta
from typing import NamedTuple

from django.db.models import (
    Case,
    Count,
    F,
    IntegerField,
    OuterRef,
    Q,
    Subquery,
    Value,
    When,
)
from django.db.models.expressions import Window
from django.db.models.functions import Rank
from django.utils import timezone
from rest_framework import mixins, permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

import sentry_sdk

from lego.apps.achievements.constants import (
    EVENT_RULES,
    EVENT_RULES_IDENTIFIER,
    KEYPRESS_ORDER,
    KEYPRESS_ORDER_IDENTIFIER,
    MANUAL_ACHIEVEMENTS,
    RankType,
)
from lego.apps.achievements.models import Achievement, RankSnapshot
from lego.apps.achievements.pagination import AchievementLeaderboardPagination
from lego.apps.achievements.ranking import (
    build_histogram,
    current_values_for,
    latest_snapshot_values,
    rarity_by_identifier_and_level,
    rarity_lookup,
)
from lego.apps.achievements.serializers import (
    AchievementGrantBulkSerializer,
    AchievementGrantSerializer,
    AchievementRevokeSerializer,
    AchievementSerializer,
    KeypressOrderSerializer,
    RankSnapshotSerializer,
)
from lego.apps.achievements.tasks import run_all_promotions
from lego.apps.achievements.utils.calculation_utils import ACHIEVEMENT_RARITIES
from lego.apps.events.constants import SUCCESS_REGISTER
from lego.apps.featureflags.models import FeatureFlag
from lego.apps.permissions.api.permissions import LegoPermissions
from lego.apps.permissions.constants import CREATE
from lego.apps.users.models import User
from lego.apps.users.serializers.users import PublicUserWithGroupsSerializer

TROPHY_GRANT_ALL_FLAG_IDENTIFIER = "trophy-grant-all"
MANUAL_ACHIEVEMENT_IDENTIFIERS = {
    data["identifier"] for data in MANUAL_ACHIEVEMENTS.values()
}


def _trophy_grant_all_enabled(user) -> bool:
    flag = FeatureFlag.objects.filter(
        identifier=TROPHY_GRANT_ALL_FLAG_IDENTIFIER
    ).first()
    return bool(flag and flag.can_see_flag(user))


def _is_webkom_member(user) -> bool:
    """
    Gate for the manual trophy grant/revoke endpoints - matches the same
    "Webkom" check SiteMetaViewSet uses to populate isAllowed.sudo, which is
    what actually gates the sudo trophy grant page on the frontend. Kept
    local to achievements/views.py rather than added to the User model,
    since nothing else needs it.
    """
    return (
        user.is_authenticated
        and user.memberships.filter(
            abakus_group__name="Webkom", is_active=True
        ).exists()
    )


def _ensure_identifier_allowed(identifier: str, user) -> Response | None:
    if identifier in MANUAL_ACHIEVEMENT_IDENTIFIERS:
        return None
    if _trophy_grant_all_enabled(user):
        return None
    return Response(
        {
            "detail": (
                f'"{identifier}" is not a manual achievement, and the '
                f'"{TROPHY_GRANT_ALL_FLAG_IDENTIFIER}" feature flag is disabled.'
            )
        },
        status=status.HTTP_400_BAD_REQUEST,
    )


def _ensure_level_in_range(identifier: str, level: int) -> Response | None:
    rarity_list = ACHIEVEMENT_RARITIES.get(identifier)
    if rarity_list is None or not (0 <= level < len(rarity_list)):
        return Response(
            {"detail": f'Level {level} is not valid for "{identifier}".'},
            status=status.HTTP_400_BAD_REQUEST,
        )
    return None


def _grant_achievement(target_user: User, identifier: str, level: int):
    """
    Set target_user's level for identifier, creating the row if needed and
    restoring it if it was soft-deleted.

    update_or_create (rather than a manual select-then-create) specifically
    because it's race-safe under concurrent requests for the same (user,
    identifier): a hand-rolled "look for an existing row, create one if
    missing" has a check-then-act gap - select_for_update() only locks a row
    that already exists, so two requests that both find nothing can both
    attempt to create, and the second hits the unique constraint. Django's
    update_or_create catches that IntegrityError internally and retries as
    an update, which is exactly the "level up then immediately level down,
    before the first request's response has updated the UI" case this
    endpoint needs to survive.
    """
    return Achievement.all_objects.update_or_create(
        user=target_user,
        identifier=identifier,
        defaults={"level": level, "deleted": False},
    )


class _Climber(NamedTuple):
    user_id: int
    rank_now: int
    rank_week_ago: int
    delta: int


class LeaderBoardViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    serializer_class = PublicUserWithGroupsSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = AchievementLeaderboardPagination

    def _get_rank_type(self):
        rank_type = self.request.query_params.get("type", RankType.ACHIEVEMENT_SCORE)
        if rank_type not in RankType.values:
            rank_type = RankType.ACHIEVEMENT_SCORE  # fall back rather than 500
        return rank_type

    def get_serializer_context(self):
        # Computed once per request instead of once per achievement - see
        # AchievementSerializer.get_percentage.
        context = super().get_serializer_context()
        context["rarity_lookup"] = rarity_lookup()
        return context

    # AchievementLeaderboardPagination.ordering is only a default - the cursor
    # pagination always calls this to decide sort order, otherwise it would
    # always order by achievements_score regardless of the selected rank_type.
    #
    # "id" is appended as a tiebreaker: the rank field is a SQL RANK() output,
    # so many rows share the same value, and cursor pagination needs a fully
    # deterministic ordering to compute a stable position/offset - otherwise
    # ties can be returned in a different order on each request.
    def get_ordering(self):
        is_event_count = self._get_rank_type() == RankType.EVENT_COUNT
        field = "event_count_rank" if is_event_count else "achievement_score_rank"
        return (field, "id")

    # Rank can't be computed via a Window() and then filtered in the same
    # queryset - Django compiles the filter before the window function,
    # so it silently changes what the window sees. Compute rank unfiltered
    # first, then bake it into the filtered queryset via Case/When.
    # Shared by get_queryset (the paginated feed) and top_climbers (a
    # standalone top-5 action) so the "who's ranked, and at what live rank"
    # Window(Rank()) query - the fragile/expensive part - is only written
    # once.
    def _live_rank_data(self, rank_type):
        if rank_type == RankType.EVENT_COUNT:
            base_qs = User.objects.annotate(
                event_count=Count(
                    "registrations",
                    filter=Q(
                        registrations__status=SUCCESS_REGISTER,
                        registrations__event__end_time__lte=timezone.now(),
                        registrations__pool__isnull=False,
                    ),
                )
            )
            distinct_user_ids = base_qs.filter(event_count__gt=0).values_list(
                "id", flat=True
            )
            order_expr = F("event_count").desc()
            rank_source_qs = base_qs.filter(id__in=distinct_user_ids).annotate(
                live_rank=Window(expression=Rank(), order_by=order_expr)
            )
        else:
            distinct_user_ids = (
                User.objects.filter(achievements__isnull=False)
                .values_list("id", flat=True)
                .distinct()
            )
            order_expr = F("achievements_score").desc()
            rank_source_qs = User.objects.filter(id__in=distinct_user_ids).annotate(
                live_rank=Window(expression=Rank(), order_by=order_expr)
            )

        global_rank_mapping = {user.id: user.live_rank for user in rank_source_qs}
        return global_rank_mapping, distinct_user_ids

    def get_queryset(self):
        rank_type = self._get_rank_type()

        today = timezone.now().date()
        week_ago = today - timedelta(days=7)
        month_ago = today - timedelta(days=30)

        global_rank_mapping, distinct_user_ids = self._live_rank_data(rank_type)

        qs_filter = User.objects.filter(id__in=distinct_user_ids)

        user_full_name = self.request.query_params.get("userFullName")
        if user_full_name:
            qs_filter = qs_filter.filter(
                Q(first_name__icontains=user_full_name)
                | Q(last_name__icontains=user_full_name)
            )

        group_ids_str = self.request.query_params.get("abakusGroupIds")
        if group_ids_str:
            group_ids = [
                int(p.strip()) for p in group_ids_str.split(",") if p.strip().isdigit()
            ]
            qs_filter = qs_filter.filter(
                membership__is_active=True, membership__abakus_group__in=group_ids
            )

        def rank_as_of(date, snapshot_type):
            return Subquery(
                RankSnapshot.objects.filter(
                    user=OuterRef("pk"), type=snapshot_type, date__lte=date
                )
                .order_by("-date")
                .values("rank")[:1]
            )

        # event_count's value is always sourced from the snapshot table,
        # regardless of which type is currently being ranked by - computing
        # it live via Count("registrations") on every request (in addition
        # to whatever the rank_type branch above already does) is the exact
        # cost this was meant to avoid.
        event_count_value = Subquery(
            RankSnapshot.objects.filter(
                user=OuterRef("pk"), type=RankType.EVENT_COUNT, date__lte=today
            )
            .order_by("-date")
            .values("value")[:1]
        )

        cases = [
            When(pk=pk, then=Value(rank)) for pk, rank in global_rank_mapping.items()
        ]
        live_rank = Case(*cases, default=Value(0), output_field=IntegerField())
        no_rank = Value(None, output_field=IntegerField())

        # Only the requested type's live rank is computed above (the window
        # query is what's fragile/expensive) - the other type's rank is left
        # null. History for both types is cheap either way, it's just a
        # snapshot lookup, so both are always populated.
        is_event_count = rank_type == RankType.EVENT_COUNT
        annotated_qs = qs_filter.annotate(
            achievement_score_rank=no_rank if is_event_count else live_rank,
            event_count_rank=live_rank if is_event_count else no_rank,
            achievement_score_rank_week_ago=rank_as_of(
                week_ago, RankType.ACHIEVEMENT_SCORE
            ),
            achievement_score_rank_month_ago=rank_as_of(
                month_ago, RankType.ACHIEVEMENT_SCORE
            ),
            event_count_rank_week_ago=rank_as_of(week_ago, RankType.EVENT_COUNT),
            event_count_rank_month_ago=rank_as_of(month_ago, RankType.EVENT_COUNT),
            event_count=event_count_value,
        )

        return annotated_qs.order_by(*self.get_ordering())

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @action(
        detail=False, methods=["GET"], permission_classes=[permissions.IsAuthenticated]
    )
    def distribution(self, request, *args, **kwargs):
        rank_type = self._get_rank_type()
        values_by_user = current_values_for(rank_type)
        values = list(values_by_user.values())

        your_value = values_by_user.get(request.user.id)
        percentile = None
        if your_value is not None and values:
            percentile = round(
                sum(value < your_value for value in values) / len(values) * 100, 1
            )

        return Response(
            {
                "bins": build_histogram(values),
                "total_count": len(values),
                "your_value": your_value,
                "percentile": percentile,
            }
        )

    @action(
        detail=False, methods=["GET"], permission_classes=[permissions.IsAuthenticated]
    )
    def rank_history(self, request, *args, **kwargs):
        rank_type = self._get_rank_type()
        snapshots = RankSnapshot.objects.filter(
            user=request.user, type=rank_type
        ).order_by("date")
        return Response(RankSnapshotSerializer(snapshots, many=True).data)

    @action(
        detail=False, methods=["GET"], permission_classes=[permissions.IsAuthenticated]
    )
    def top_climbers(self, request, *args, **kwargs):
        """
        Top 5 users by rank improvement over the last 7 days - the same
        rolling window (date__lte=week_ago, most recent snapshot on or
        before that date) as the personal week-ago/month-ago columns on the
        leaderboard, so "top climbers" and "Siste uke" always agree.
        """
        rank_type = self._get_rank_type()
        today = timezone.now().date()
        week_ago = today - timedelta(days=7)

        current_rank_mapping, _ = self._live_rank_data(rank_type)
        week_ago_rank_mapping = latest_snapshot_values(
            rank_type, "rank", date__lte=week_ago
        )

        climbers: list[_Climber] = []
        for user_id, rank_week_ago in week_ago_rank_mapping.items():
            rank_now = current_rank_mapping.get(user_id)
            if rank_now is None:
                continue
            delta = rank_week_ago - rank_now
            if delta > 0:
                climbers.append(_Climber(user_id, rank_now, rank_week_ago, delta))

        top = heapq.nlargest(5, climbers, key=lambda climber: climber.delta)

        users_by_id = User.objects.in_bulk([climber.user_id for climber in top])
        results = []
        for climber in top:
            user = users_by_id[climber.user_id]
            results.append(
                {
                    "username": user.username,
                    "full_name": user.full_name,
                    "rank": climber.rank_now,
                    "rank_week_ago": climber.rank_week_ago,
                }
            )
        return Response(results)


class AchievementViewSet(viewsets.GenericViewSet):
    permission_classes = [LegoPermissions, permissions.IsAuthenticated]
    queryset = Achievement.objects.none()
    serializer_class = KeypressOrderSerializer

    @action(
        detail=False, methods=["GET"], permission_classes=[permissions.IsAuthenticated]
    )
    def rarity(self, request, *args, **kwargs):
        """% of users who have earned each achievement, per level."""
        return Response(rarity_by_identifier_and_level())

    @action(
        detail=False, methods=["POST"], permission_classes=[permissions.IsAuthenticated]
    )
    def getting_wood(self, request, *args, **kwargs):
        _, created = Achievement.objects.get_or_create(
            identifier=EVENT_RULES[EVENT_RULES_IDENTIFIER]["identifier"],
            user=request.user,
            level=0,
        )
        if created:
            return Response(status=status.HTTP_201_CREATED)
        else:
            return Response(status=status.HTTP_304_NOT_MODIFIED)

    @action(
        detail=False, methods=["POST"], permission_classes=[permissions.IsAuthenticated]
    )
    def keypress_order(self, request, *args, **kwargs):
        code = [38, 38, 40, 40, 37, 39, 37, 39, 66, 65]
        if request.data.get("code", []) == code:
            _, created = Achievement.objects.get_or_create(
                identifier=KEYPRESS_ORDER[KEYPRESS_ORDER_IDENTIFIER]["identifier"],
                user=request.user,
                level=0,
            )
            if created:
                return Response(status=status.HTTP_201_CREATED)
            else:
                return Response(status=status.HTTP_304_NOT_MODIFIED)
        return Response(status=status.HTTP_304_NOT_MODIFIED)

    @action(
        detail=False,
        methods=["GET"],
        permission_classes=[LegoPermissions, permissions.IsAuthenticated],
    )
    def recheck_all(self, request, *args, **kwargs):
        user = request.user
        if not user.has_perm(CREATE, Achievement):
            return Response(status=status.HTTP_401_UNAUTHORIZED)
        run_all_promotions.delay()
        return Response(
            {"detail": "Recheck task has been triggered."},
            status=status.HTTP_202_ACCEPTED,
        )

    @action(
        detail=False,
        methods=["GET"],
        permission_classes=[permissions.IsAuthenticated],
    )
    def user_achievements(self, request, *args, **kwargs):
        """List every achievement a given user currently holds - admin lookup
        for the sudo trophy grant page (mode 1)."""
        if not _is_webkom_member(request.user):
            return Response(status=status.HTTP_401_UNAUTHORIZED)

        user_id = request.query_params.get("user_id")
        if not user_id:
            return Response(
                {"detail": "user_id query param is required."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        try:
            target_user = User.objects.get(pk=user_id)
        except (User.DoesNotExist, ValueError):
            return Response(
                {"detail": "User not found."}, status=status.HTTP_404_NOT_FOUND
            )

        achievements = Achievement.objects.filter(user=target_user).order_by(
            "identifier", "level"
        )
        return Response(AchievementSerializer(achievements, many=True).data)

    @action(
        detail=False,
        methods=["POST"],
        permission_classes=[permissions.IsAuthenticated],
    )
    def grant(self, request, *args, **kwargs):
        if not _is_webkom_member(request.user):
            return Response(status=status.HTTP_401_UNAUTHORIZED)

        serializer = AchievementGrantSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        identifier_error = _ensure_identifier_allowed(data["identifier"], request.user)
        if identifier_error:
            return identifier_error
        level_error = _ensure_level_in_range(data["identifier"], data["level"])
        if level_error:
            return level_error

        try:
            target_user = User.objects.get(pk=data["user_id"])
        except User.DoesNotExist:
            return Response(
                {"detail": "User not found."}, status=status.HTTP_404_NOT_FOUND
            )

        achievement, created = _grant_achievement(
            target_user, data["identifier"], data["level"]
        )

        sentry_sdk.capture_message(
            f"Achievement grant: admin={request.user.username} "
            f"target={target_user.username} identifier={data['identifier']} "
            f"level={data['level']} created={created} "
            f"reason={data['reason']!r}",
            "info",
        )

        return Response(
            AchievementSerializer(achievement).data,
            status=status.HTTP_201_CREATED if created else status.HTTP_200_OK,
        )

    @action(
        detail=False,
        methods=["POST"],
        permission_classes=[permissions.IsAuthenticated],
    )
    def revoke(self, request, *args, **kwargs):
        if not _is_webkom_member(request.user):
            return Response(status=status.HTTP_401_UNAUTHORIZED)

        serializer = AchievementRevokeSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        identifier_error = _ensure_identifier_allowed(data["identifier"], request.user)
        if identifier_error:
            return identifier_error

        try:
            target_user = User.objects.get(pk=data["user_id"])
        except User.DoesNotExist:
            return Response(
                {"detail": "User not found."}, status=status.HTTP_404_NOT_FOUND
            )

        achievement = Achievement.objects.filter(
            user=target_user, identifier=data["identifier"]
        ).first()
        if achievement is None:
            return Response(status=status.HTTP_404_NOT_FOUND)

        level = achievement.level
        achievement.delete()

        sentry_sdk.capture_message(
            f"Achievement revoke: admin={request.user.username} "
            f"target={target_user.username} identifier={data['identifier']} "
            f"level={level} reason={data['reason']!r}",
            "info",
        )
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        detail=False,
        methods=["POST"],
        permission_classes=[permissions.IsAuthenticated],
    )
    def grant_bulk(self, request, *args, **kwargs):
        if not _is_webkom_member(request.user):
            return Response(status=status.HTTP_401_UNAUTHORIZED)

        serializer = AchievementGrantBulkSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        identifier_error = _ensure_identifier_allowed(data["identifier"], request.user)
        if identifier_error:
            return identifier_error
        level_error = _ensure_level_in_range(data["identifier"], data["level"])
        if level_error:
            return level_error

        users_by_id = User.objects.in_bulk(data["user_ids"])
        missing_ids = set(data["user_ids"]) - set(users_by_id)
        if missing_ids:
            return Response(
                {"detail": f"Unknown user id(s): {sorted(missing_ids)}"},
                status=status.HTTP_404_NOT_FOUND,
            )

        granted_count = 0
        created_count = 0
        for target_user in users_by_id.values():
            _, created = _grant_achievement(
                target_user, data["identifier"], data["level"]
            )
            granted_count += 1
            created_count += created

        sentry_sdk.capture_message(
            f"Achievement grant_bulk: admin={request.user.username} "
            f"identifier={data['identifier']} level={data['level']} "
            f"user_count={granted_count} newly_created={created_count} "
            f"user_ids={sorted(users_by_id)} reason={data['reason']!r}",
            "info",
        )

        return Response(
            {"granted": granted_count, "created": created_count},
            status=status.HTTP_200_OK,
        )
