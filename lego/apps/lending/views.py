from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

from lego.apps.lending.models import LendableObject
from lego.apps.lending.serializers import LendableObjectSerializer
from lego.apps.permissions.api.permissions import LegoPermissions
from lego.apps.permissions.api.views import AllowedPermissionsMixin


class LendableObjectViewSet(AllowedPermissionsMixin, viewsets.ModelViewSet):
    queryset = LendableObject.objects.all()
    serializer_class = LendableObjectSerializer
    permission_classes = [LegoPermissions, IsAuthenticated]
