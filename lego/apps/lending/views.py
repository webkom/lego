from rest_framework import decorators, permissions, status, viewsets
from rest_framework.response import Response

from lego.apps.lending.filters import LendableObjectFilterSet, LendingInstanceFilterSet
from lego.apps.lending.models import LendableObject, LendingInstance
from lego.apps.lending.serializers import (
    DetailedAdminLendableObjectSerializer,
    DetailedLendableObjectSerializer,
    DetailedLendingInstanceSerializer,
    LendingInstanceCreateAndUpdateSerializer,
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

    @decorators.action(
        detail=True, methods=["get"], permission_classes=[permissions.IsAuthenticated]
    )
    def lendingInstance(self, request, pk=None):
        try:
            lendable_object = LendableObject.objects.get(pk=pk)
        except LendableObject.DoesNotExist:
            return Response(
                {"error": "LendableObject not found"}, status=status.HTTP_404_NOT_FOUND
            )
        permission_handler = get_permission_handler(LendingInstance)
        lending_instances = permission_handler.filter_queryset(
            self.request.user,
            LendingInstance.objects.filter(lendable_object=lendable_object),
        )
        serializer = DetailedLendingInstanceSerializer(
            lending_instances, many=True, context={"request": request}
        )
        return Response(serializer.data)


class LendingInstanceViewSet(AllowedPermissionsMixin, viewsets.ModelViewSet):
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
            LendingInstance.objects.prefetch_related("lendable_object"),
        )

    def get_serializer_class(self):
        if self.request and self.request.user.is_authenticated:
            return DetailedLendingInstanceSerializer
        return super().get_serializer_class()

    def create(self, request):
        serializer = LendingInstanceCreateAndUpdateSerializer(
            data=request.data, context={"request": request}
        )
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response(data=serializer.data, status=status.HTTP_201_CREATED)
