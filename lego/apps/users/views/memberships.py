from datetime import datetime
from typing import Any

from django.http import HttpRequest
from django.utils import timezone
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, viewsets
from rest_framework.response import Response

from lego.apps.permissions.api.filters import LegoPermissionFilter
from lego.apps.permissions.api.views import AllowedPermissionsMixin
from lego.apps.users.filters import MembershipFilterSet
from lego.apps.users.models import AbakusGroup, Membership, MembershipHistory, User
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
            return AbakusGroup.objects.get(pk=group).memberships

        return Membership.objects.filter(abakus_group_id=group)

    def create(self, request, *args, **kwargs):
        request.data["abakus_group"] = kwargs["group_pk"]
        return super(MembershipViewSet, self).create(request, *args, **kwargs)

    def update(self, request: HttpRequest, *args: Any, **kwargs: Any) -> Response:
        """Create a new membership history object when a membership is updated"""

        user = User.objects.get(pk=request.data["membership"]["id"])
        group = AbakusGroup.objects.get(pk=request.data["membership"]["abakus_group"])
        start_date = datetime.strptime(
            request.data["membership"]["created_at"], "%Y-%m-%dT%H:%M:%S.%fZ"
        )
        MembershipHistory.objects.create(
            user=user,
            abakus_group=group,
            role=request.data["role"],
            start_date=start_date,
            end_date=timezone.now(),
        )

        return super(MembershipViewSet, self).update(request, *args, **kwargs)
