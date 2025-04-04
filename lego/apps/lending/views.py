from django.db.models import Q
from rest_framework import mixins, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

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
