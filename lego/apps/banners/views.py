from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from lego.apps.banners.models import Banners
from lego.apps.banners.serializers import BannersSerializer
from lego.apps.permissions.api.permissions import LegoPermissions


class BannersViewSet(viewsets.ModelViewSet):
    lookup_value_regex = r"\d+"
    serializer_class = BannersSerializer
    queryset = Banners.objects.all()
    permission_classes = [LegoPermissions, AllowAny]

    def get_queryset(self):
        if self.action == "current_private":
            return Banners.objects.filter(current_private=True)
        if self.action == "current_public":
            return Banners.objects.filter(current_public=True)
        return super().get_queryset()

    @action(
        detail=False,
        methods=["get"],
        url_path="current_private",
        permission_classes=[AllowAny],
    )
    def current_private(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        banner = queryset.first()
        if banner is None:
            return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)
        serializer = self.get_serializer(banner)
        return Response(serializer.data)

    @action(
        detail=False,
        methods=["get"],
        url_path="current_public",
        permission_classes=[AllowAny],
    )
    def current_public(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        banner = queryset.first()
        if banner is None:
            return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)
        serializer = self.get_serializer(banner)
        return Response(serializer.data)
