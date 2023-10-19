from rest_framework import (
    decorators,
    exceptions,
    mixins,
    permissions,
    renderers,
    status,
    viewsets,
)
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from lego.apps.lending.filters import LendableObjectFilterSet, LendingInstanceFilterSet
from lego.apps.lending.models import LendableObject, LendingInstance
from lego.apps.lending.serializers import (
    LendableObjectSerializer,
    LendingInstanceSerializer,
)
from lego.apps.permissions.api.views import AllowedPermissionsMixin


class LendableObjectViewSet(
    AllowedPermissionsMixin,
    mixins.CreateModelMixin,
    mixins.DestroyModelMixin,
    mixins.ListModelMixin,
    GenericViewSet,
):
    queryset = LendableObject.objects.all()
    serializer_class = LendableObjectSerializer
    filterset_class = LendableObjectFilterSet
    http_method_names = ["get", "post", "patch", "delete", "head", "options"]
    permission_classes = [
        permissions.IsAuthenticated,
    ]


class LendingInstanceViewSet(
    AllowedPermissionsMixin,
    mixins.CreateModelMixin,
    mixins.DestroyModelMixin,
    mixins.ListModelMixin,
    GenericViewSet,
):
    queryset = LendingInstance.objects.all()
    serializer_class = LendingInstanceSerializer
    filterset_class = LendingInstanceFilterSet
    http_method_names = ["get", "post", "patch", "delete", "head", "options"]
    permission_classes = [
        permissions.IsAuthenticated,
    ]

    def create(self, request):
        serializer = LendingInstanceSerializer(data=request.data, context={'request': request})
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response(data=serializer.data, status=status.HTTP_201_CREATED)

        return Response(data=serializer.errors, status=status.HTTP_400_BAD_REQUEST)
