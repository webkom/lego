from datetime import timedelta

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

from lego.apps.achievements.constants import (
    EVENT_RULES,
    EVENT_RULES_IDENTIFIER,
    KEYPRESS_ORDER,
    KEYPRESS_ORDER_IDENTIFIER,
    RankType,
)
from lego.apps.achievements.models import Achievement, RankSnapshot
from lego.apps.achievements.pagination import AchievementLeaderboardPagination
from lego.apps.achievements.serializers import KeypressOrderSerializer
from lego.apps.achievements.tasks import run_all_promotions
from lego.apps.permissions.api.permissions import LegoPermissions
from lego.apps.permissions.constants import CREATE
from lego.apps.users.models import User
from lego.apps.users.serializers.users import PublicUserWithGroupsSerializer


class LeaderBoardViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    serializer_class = PublicUserWithGroupsSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = AchievementLeaderboardPagination

    # AchievementLeaderboardPagination.ordering is only a default - the cursor
    # pagination always calls this to decide sort order, otherwise it would
    # always order by achievements_score regardless of the selected rank_type.
    def get_ordering(self):
        return "achievement_rank"

    # Rank can't be computed via a Window() and then filtered in the same
    # queryset - Django compiles the filter before the window function,
    # so it silently changes what the window sees. Compute rank unfiltered
    # first, then bake it into the filtered queryset via Case/When.
    def get_queryset(self):
        rank_type = self.request.query_params.get("type", RankType.ACHIEVEMENT_SCORE)
        if rank_type not in RankType.values:
            rank_type = RankType.ACHIEVEMENT_SCORE  # fall back rather than 500

        today = timezone.now().date()
        week_ago = today - timedelta(days=7)
        month_ago = today - timedelta(days=30)

        if rank_type == RankType.EVENT_COUNT:
            base_qs = User.objects.annotate(event_count=Count("registrations"))
            distinct_user_ids = base_qs.filter(event_count__gt=0).values_list(
                "id", flat=True
            )
            order_expr = F("event_count").desc()
            rank_source_qs = base_qs.filter(id__in=distinct_user_ids).annotate(
                achievement_rank=Window(expression=Rank(), order_by=order_expr)
            )
        else:
            distinct_user_ids = (
                User.objects.filter(achievements__isnull=False)
                .values_list("id", flat=True)
                .distinct()
            )
            order_expr = F("achievements_score").desc()
            rank_source_qs = User.objects.filter(id__in=distinct_user_ids).annotate(
                achievement_rank=Window(expression=Rank(), order_by=order_expr)
            )

        global_rank_mapping = {
            user.id: user.achievement_rank for user in rank_source_qs
        }

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

        def rank_as_of(date, snapshot_type=rank_type):
            return Subquery(
                RankSnapshot.objects.filter(
                    user=OuterRef("pk"), type=snapshot_type, date__lte=date
                )
                .order_by("-date")
                .values("rank")[:1]
            )

        # event_count is always sourced from the snapshot table, regardless
        # of which type is currently being ranked by - computing it live via
        # Count("registrations") on every request (in addition to whatever
        # the rank_type branch above already does) is the exact cost this
        # was meant to avoid.
        event_count = Subquery(
            RankSnapshot.objects.filter(
                user=OuterRef("pk"), type=RankType.EVENT_COUNT, date__lte=today
            )
            .order_by("-date")
            .values("value")[:1]
        )

        cases = [
            When(pk=pk, then=Value(rank)) for pk, rank in global_rank_mapping.items()
        ]
        annotated_qs = qs_filter.annotate(
            achievement_rank=Case(
                *cases, default=Value(0), output_field=IntegerField()
            ),
            rank_week_ago=rank_as_of(week_ago),
            rank_month_ago=rank_as_of(month_ago),
            event_count=event_count,
        )

        return annotated_qs.order_by("achievement_rank")

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


class AchievementViewSet(viewsets.GenericViewSet):
    permission_classes = [LegoPermissions, permissions.IsAuthenticated]
    queryset = Achievement.objects.none()
    serializer_class = KeypressOrderSerializer

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
