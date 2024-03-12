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
    DetailedLendableObjectSerializer,
    DetailedLendingInstanceSerializer,
    DetailedAdminLendableObjectSerializer,
    DetailedAdminLendingInstanceSerializer
)
from lego.apps.permissions.api.views import AllowedPermissionsMixin
from lego.apps.permissions.utils import get_permission_handler


class LendableObjectViewSet(AllowedPermissionsMixin, viewsets.ModelViewSet):
    queryset = LendableObject.objects.all()
    serializer_class = DetailedLendableObjectSerializer
    filterset_class = LendableObjectFilterSet
    http_method_names = ["get", "post", "patch", "delete", "head", "options"]
    permission_classes = [
        permissions.IsAuthenticated,
    ]

    def get_serializer_class(self):
        if self.request and self.request.user.is_authenticated:
            return DetailedAdminLendableObjectSerializer
        return super().get_serializer_class()


class LendingInstanceViewSet(AllowedPermissionsMixin, viewsets.ModelViewSet):
    queryset = LendingInstance.objects.all()
    serializer_class = DetailedLendingInstanceSerializer
    filterset_class = LendingInstanceFilterSet
    http_method_names = ["get", "post", "patch", "delete", "head", "options"]
    permission_classes = [
        permissions.IsAuthenticated,
    ]
    
    def get_queryset(self):
        if self.request is None:
            return LendingInstance.objects.none()

        permission_handler = get_permission_handler(LendingInstance)
        return permission_handler.filter_queryset(
            self.request.user,
        )

    def get_serializer_class(self):
        if self.request and self.request.user.is_authenticated:
            return DetailedAdminLendingInstanceSerializer
        return super().get_serializer_class()


    def create(self, request):
        serializer = DetailedLendingInstanceSerializer(
            data=request.data, context={"request": request}
        )
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response(data=serializer.data, status=status.HTTP_201_CREATED)

        return Response(data=serializer.errors, status=status.HTTP_400_BAD_REQUEST)
