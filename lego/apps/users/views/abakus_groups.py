from random import sample

from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from lego.apps.permissions.api.views import AllowedPermissionsMixin
from lego.apps.permissions.constants import EDIT
from lego.apps.users import constants
from lego.apps.users.filters import AbakusGroupFilterSet
from lego.apps.users.models import AbakusGroup
from lego.apps.users.permissions import PreventPermissionElevation
from lego.apps.users.serializers.abakus_groups import (
    DetailedAbakusGroupSerializer,
    PublicAbakusGroupSerializer,
    PublicDetailedAbakusGroupSerializer,
    PublicListAbakusGroupSerializer,
)


class AbakusGroupViewSet(AllowedPermissionsMixin, viewsets.ModelViewSet):
    queryset = AbakusGroup.objects.all()
    ordering = "id"
    filterset_class = AbakusGroupFilterSet
    pagination_class = None
    permission_classes = [PreventPermissionElevation]

    def get_serializer_class(self):
        if self.action == "list":
            return PublicListAbakusGroupSerializer

        if self.action == "create":
            return DetailedAbakusGroupSerializer

        if self.action == "retrieve":
            abakus_group = self.get_object()
            if self.request.user.has_perm(EDIT, abakus_group):
                return DetailedAbakusGroupSerializer

            if abakus_group.type in constants.PUBLIC_GROUPS:
                return PublicDetailedAbakusGroupSerializer
            return PublicAbakusGroupSerializer

        return DetailedAbakusGroupSerializer

    def get_queryset(self):
        if self.action == "retrieve":
            return AbakusGroup.objects_with_text.prefetch_related("users").all()

        return self.queryset

    @action(detail=False, methods=["GET"])
    def random_interests(self, request):
        queryset = self.get_queryset().filter(type="interesse", active=True)

        values = queryset.values_list("pk", flat=True)
        if not values:
            return Response(status=status.HTTP_204_NO_CONTENT)

        values = list(values)

        if len(values) > 3:
            values = sample(values, 3)

        random_qs = queryset.filter(pk__in=values)

        serializer = self.get_serializer(random_qs, many=True)
        return Response(serializer.data)
