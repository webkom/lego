from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from django.db.models import Q

from lego.apps.lending.models import LendableObject, LendingRequest
from lego.apps.lending.serializers import (
    LendableObjectAdminSerializer,
    LendableObjectSerializer,
    LendingRequestAdminSerializer,
    LendingRequestSerializer,
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
    def get_queryset(self):
        user = self.request.user
        if not user.is_authenticated:
            return LendingRequest.objects.none()
        editable_objects = LendableObject.objects.filter(
            Q(can_edit_users=user) |
            Q(can_edit_groups__in=user.abakus_groups.all())
        ).distinct()
        
        return LendingRequest.objects.filter(
            Q(created_by=user) |
            Q(lendable_object__in=editable_objects)
        ).distinct()
    
    def get_serializer_class(self):
        if self.action in ["create", "update", "partial_update"]:
            return LendingRequestSerializer
        if self.action == "retrieve":
            user = self.request.user
            is_admin = user.has_perm(EDIT, obj=self.get_object().lendable_object)
            return (
                LendingRequestAdminSerializer if is_admin else LendingRequestSerializer
            )
        return LendingRequestSerializer
    permission_classes = [LegoPermissions, IsAuthenticated]
