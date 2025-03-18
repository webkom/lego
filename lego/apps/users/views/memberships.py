from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, status, viewsets
from rest_framework.response import Response

from lego.apps.permissions.api.filters import LegoPermissionFilter
from lego.apps.permissions.api.views import AllowedPermissionsMixin
from lego.apps.users import constants
from lego.apps.users.filters import MembershipFilterSet
from lego.apps.users.models import AbakusGroup, Membership
from lego.apps.users.serializers.memberships import MembershipSerializer


class MembershipViewSet(AllowedPermissionsMixin, viewsets.ModelViewSet):
    serializer_class = MembershipSerializer
    filterset_class = MembershipFilterSet
    ordering_fields = ["id", "role"]
    filter_backends = (
        DjangoFilterBackend,
        filters.OrderingFilter,
        LegoPermissionFilter,
    )
    ordering = "id"

    def get_queryset(self):
        if self.request is None:
            return Membership.objects.none()

        group = self.kwargs["group_pk"]
        descendants = self.request.query_params.get("descendants", None)
        if descendants == "true":
            return AbakusGroup.objects.get(pk=group).memberships.distinct()

        return Membership.objects.filter(abakus_group_id=group).distinct()

    def create(self, request, *args, **kwargs):
        request.data["abakus_group"] = kwargs["group_pk"]
        group_id = kwargs["group_pk"]
        group = AbakusGroup.objects.get(pk=group_id)

        if group.type == constants.GROUP_INTEREST and not request.user.has_grade_group:
            return Response(status=status.HTTP_403_FORBIDDEN)

        return super(MembershipViewSet, self).create(request, *args, **kwargs)
