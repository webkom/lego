from django.db.models import Case, Count, F, IntegerField, Q, Value, When
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
)
from lego.apps.achievements.models import Achievement
from lego.apps.achievements.pagination import AchievementLeaderboardPagination
from lego.apps.achievements.serializers import KeypressOrderSerializer
from lego.apps.events.constants import SUCCESS_REGISTER
from lego.apps.users.models import User
from lego.apps.users.serializers.users import PublicUserWithGroupsSerializer


class LeaderBoardViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    serializer_class = PublicUserWithGroupsSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = AchievementLeaderboardPagination

    # The reason for not using a django filter is due to how django compiles SQL
    # making it impossible to compute global rank
    def get_queryset(self):
        distinct_user_ids = (
            User.objects.filter(achievements__isnull=False)
            .values_list("id", flat=True)
            .distinct()
        )

        qs = User.objects.filter(id__in=distinct_user_ids).annotate(
            achievement_rank=Window(
                expression=Rank(), order_by=F("achievements_score").desc()
            )
        )

        global_rank_mapping = {user.id: user.achievement_rank for user in qs}

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

        cases = [
            When(pk=pk, then=Value(rank)) for pk, rank in global_rank_mapping.items()
        ]
        annotated_qs = qs_filter.annotate(
            achievement_rank=Case(
                *cases, default=Value(0), output_field=IntegerField()
            ),
            event_count=Count(
                "registrations",
                filter=Q(
                    registrations__status=SUCCESS_REGISTER,
                    registrations__event__end_time__lte=timezone.now(),
                    registrations__pool__isnull=False,
                ),
                distinct=True,
            ),
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
    permission_classes = [permissions.IsAuthenticated]

    serializer_class = KeypressOrderSerializer

    @action(detail=False, methods=["POST"])
    def getting_wood(self, request, *args, **kwargs):
        achievement, created = Achievement.objects.get_or_create(
            identifier=EVENT_RULES[EVENT_RULES_IDENTIFIER]["identifier"],
            user=request.user,
            level=0,
        )
        if created:
            return Response(status=status.HTTP_201_CREATED)
        else:
            return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=False, methods=["POST"])
    def keypress_order(self, request, *args, **kwargs):
        code = [38, 38, 40, 40, 37, 39, 37, 39, 66, 65]
        if request.data.get("code", []) == code:
            achievement, created = Achievement.objects.get_or_create(
                identifier=KEYPRESS_ORDER[KEYPRESS_ORDER_IDENTIFIER]["identifier"],
                user=request.user,
                level=0,
            )
            if created:
                return Response(status=status.HTTP_201_CREATED)
            else:
                return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(status=status.HTTP_204_NO_CONTENT)
