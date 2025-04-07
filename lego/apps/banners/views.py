from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from lego.apps.banners.models import Banners
from lego.apps.banners.serializers import BannerSerializer
from lego.apps.permissions.api.permissions import LegoPermissions


class BannersViewSet(viewsets.ModelViewSet):
    lookup_value_regex = r"\d+"
    serializer_class = BannerSerializer
    queryset = Banners.objects.all()
    permission_classes = [LegoPermissions, IsAuthenticated]

    @action(
        detail=False,
        methods=["get"],
        url_path="current-private",
        url_name="current-private",
        permission_classes=[IsAuthenticated],
    )
    def current_private(self, request, *args, **kwargs):
        banner = self.get_queryset().filter(current_private=True).first()
        if banner is None:
            return Response(status=status.HTTP_204_NO_CONTENT)
        serializer = self.get_serializer(banner)
        return Response(serializer.data)

    @action(
        detail=False,
        methods=["get"],
        url_path="current-public",
        url_name="current-public",
        permission_classes=[AllowAny],
    )
    def current_public(self, request, *args, **kwargs):
        banner = self.get_queryset().filter(current_public=True).first()
        if banner is None:
            return Response(status=status.HTTP_204_NO_CONTENT)
        serializer = self.get_serializer(banner)
        return Response(serializer.data)

    def update(self, request, *args, **kwargs):
        partial = request.query_params.get("partial", "false").lower() == "true"
        kwargs["partial"] = partial
        return super().update(request, *args, **kwargs)
