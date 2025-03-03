from django.db.models import F, Window
from django.db.models.functions import Rank
from rest_framework import mixins, permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Window, F, Q
from django.db.models.functions import Rank
from django.db.models import F
from lego.apps.achievements.constants import (
    EVENT_RULES,
    EVENT_RULES_IDENTIFIER,
    KEYPRESS_ORDER,
    KEYPRESS_ORDER_IDENTIFIER,
)
from lego.apps.achievements.models import Achievement
from lego.apps.achievements.pagination import AchievementLeaderboardPagination
from lego.apps.achievements.serializers import KeypressOrderSerializer
from lego.apps.users.models import User
from lego.apps.users.serializers.users import PublicUserWithGroupsSerializer

class LeaderBoardViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    serializer_class = PublicUserWithGroupsSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = AchievementLeaderboardPagination

    def get_queryset(self):
        # Get distinct user IDs that have at least one achievement.
        distinct_user_ids = (
            User.objects
            .filter(achievements__isnull=False)
            .values_list('id', flat=True)
            .distinct()
        )

        # Build the queryset based on those distinct user IDs and annotate with Rank().
        qs = User.objects.filter(id__in=distinct_user_ids).annotate(
            achievement_rank=Window(
                expression=Rank(),
                order_by=F('achievements_score').desc()
            )
        )

        # Optionally filter by user full name.
        user_full_name = self.request.query_params.get("userFullName")
        if user_full_name:
            qs = qs.filter(
                Q(first_name__icontains=user_full_name) |
                Q(last_name__icontains=user_full_name)
            )

        # Optionally filter by group IDs.
        group_ids_str = self.request.query_params.get("abakusGroupIds")
        if group_ids_str:
            group_ids = [int(p.strip()) for p in group_ids_str.split(",") if p.strip().isdigit()]
            qs = qs.filter(
                membership__is_active=True,
                membership__abakus_group__in=group_ids
            )

        return qs.order_by('achievement_rank')




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
        code = [38, 38, 40, 40, 37, 39, 37, 39, 66, 65, 13]
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
