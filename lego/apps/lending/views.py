from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

from lego.apps.lending.models import LendableObject
from lego.apps.lending.serializers import (
    LendableObjectAdminSerializer,
    LendableObjectSerializer,
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
