from rest_framework import mixins, viewsets
from rest_framework.permissions import AllowAny, IsAuthenticated

from lego.apps.featureflags.models import FeatureFlag
from lego.apps.featureflags.serializers import (
    FeatureFlagAdminSerializer,
    FeatureFlagPublicSerializer,
)
from lego.apps.permissions.api.permissions import LegoPermissions


class FeatureFlagsPublicViewSet(mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    queryset = FeatureFlag.objects.all()
    lookup_field = "identifier"
    permission_classes = [AllowAny]
    serializer_class = FeatureFlagPublicSerializer


class FeatureFlagsAdminViewSet(viewsets.ModelViewSet):
    permission_classes = [LegoPermissions, IsAuthenticated]
    queryset = FeatureFlag.objects.all()
    serializer_class = FeatureFlagAdminSerializer
