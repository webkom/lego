import calendar
from datetime import datetime

from django.db.models import Q
from django.utils import timezone
from rest_framework import mixins, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from lego.apps.lending.constants import LENDING_REQUEST_STATUSES
from lego.apps.lending.filters import LendingRequestFilterSet
from lego.apps.lending.models import LendableObject, LendingRequest, TimelineEntry
from lego.apps.lending.serializers import (
    LendableObjectAdminSerializer,
    LendableObjectSerializer,
    LendingRequestCreateAndUpdateSerializer,
    LendingRequestDetailSerializer,
    LendingRequestListSerializer,
    TimelineEntryCreateAndUpdateSerializer,
)
from lego.apps.permissions.api.permissions import LegoPermissions
from lego.apps.permissions.api.views import AllowedPermissionsMixin
from lego.apps.permissions.constants import EDIT
from lego.apps.users.models import User


class LendableObjectViewSet(AllowedPermissionsMixin, viewsets.ModelViewSet):
    queryset = LendableObject.objects.all()
    serializer_class = LendableObjectSerializer
    permission_classes = [LegoPermissions, IsAuthenticated]

    def get_serializer_class(self):
        if self.action in ["create", "update", "partial_update"]:
            return LendableObjectAdminSerializer
        if self.action == "retrieve":
            user = self.request.user
            is_admin = user.has_perm(EDIT, obj=self.get_object())
            return (
                LendableObjectAdminSerializer if is_admin else LendableObjectSerializer
            )
        return LendableObjectSerializer

    @action(detail=True, methods=["GET"])
    def availability(self, request, *args, **kwargs):
        """
        Returns time ranges when the object is unavailable (has approved lending requests)
        for a specified month and year.
        """
        lendable_object = self.get_object()

        try:
            month = int(request.query_params.get("month", ""))
            year = int(request.query_params.get("year", ""))

            if not 1 <= month <= 12:
                return Response(
                    {"detail": "Month must be between 1 and 12."},
                    status=status.HTTP_400_BAD_REQUEST,
                )
        except ValueError:
            return Response(
                {"detail": "Month and year must be valid integers."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        start_of_month = timezone.make_aware(datetime(year, month, 1))
        last_day = calendar.monthrange(year, month)[1]
        end_of_month = timezone.make_aware(datetime(year, month, last_day, 23, 59, 59))

        approved_status = LENDING_REQUEST_STATUSES["LENDING_APPROVED"]["value"]

        overlapping_requests = (
            LendingRequest.objects.filter(
                lendable_object=lendable_object, status=approved_status
            )
            .filter(Q(start_date__lte=end_of_month) & Q(end_date__gte=start_of_month))
            .order_by("start_date")
        )

        unavailable_ranges = []
        for request in overlapping_requests:
            range_start = max(request.start_date, start_of_month)
            range_end = min(request.end_date, end_of_month)

            unavailable_ranges.append([range_start, range_end, request.created_by])

        formatted_ranges = []
        for i in range(len(unavailable_ranges)):
            temp_list = []
            start, end, created_by = unavailable_ranges[i]
            temp_list.append(start.isoformat())
            temp_list.append(end.isoformat())
            if created_by is None:
                temp_list.append(None)
            elif isinstance(created_by, str):
                usr = User.objects.filter(username=created_by).first()
                if usr:
                    temp_list.append(usr.get_full_name())
                else:
                    temp_list.append(None)
            elif isinstance(created_by, User):
                temp_list.append(created_by.get_full_name())
            else:
                temp_list.append(None)
            temp_list.append(None if (created_by is None) else created_by.username)
            formatted_ranges.append(temp_list)

        return Response(formatted_ranges)


class LendingRequestViewSet(AllowedPermissionsMixin, viewsets.ModelViewSet):
    permission_classes = [LegoPermissions, IsAuthenticated]
    filterset_class = LendingRequestFilterSet

    def get_queryset(self):
        user = self.request.user
        if not user.is_authenticated:
            return LendingRequest.objects.none()

        if self.action == "admin":
            editable_objects = LendableObject.objects.filter(
                Q(can_edit_users=user) | Q(can_edit_groups__in=user.abakus_groups.all())
            ).distinct()
            return LendingRequest.objects.filter(
                lendable_object__in=editable_objects
            ).distinct()

        elif self.action == "list":
            return LendingRequest.objects.filter(created_by=user)

        else:
            editable_objects = LendableObject.objects.filter(
                Q(can_edit_users=user) | Q(can_edit_groups__in=user.abakus_groups.all())
            ).distinct()
            return LendingRequest.objects.filter(
                Q(created_by=user) | Q(lendable_object__in=editable_objects)
            ).distinct()

    def get_serializer_class(self):
        if self.action in ["create", "update", "partial_update"]:
            return LendingRequestCreateAndUpdateSerializer
        if self.action in ["list", "admin"]:
            return LendingRequestListSerializer
        return LendingRequestDetailSerializer

    @action(detail=False, methods=["get"], url_path="admin")
    def admin(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


class TimelineEntryViewSet(viewsets.GenericViewSet, mixins.CreateModelMixin):
    queryset = TimelineEntry.objects.all()
    serializer_class = TimelineEntryCreateAndUpdateSerializer
    permission_classes = [IsAuthenticated]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)

        timeline_entry = serializer.instance
        lending_request = timeline_entry.lending_request

        lending_request_serializer = LendingRequestDetailSerializer(
            lending_request, context={"request": request}
        )
        return Response(lending_request_serializer.data, status=status.HTTP_201_CREATED)
