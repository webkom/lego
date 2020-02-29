from rest_framework import viewsets

from lego.apps.permissions.api.views import AllowedPermissionsMixin
from lego.apps.users.filters import MembershipFilterSet
from lego.apps.users.models import AbakusGroup, Membership
from lego.apps.users.serializers.memberships import MembershipSerializer


class MembershipViewSet(AllowedPermissionsMixin, viewsets.ModelViewSet):
    serializer_class = MembershipSerializer
    filter_class = MembershipFilterSet
    ordering = "id"

    def get_queryset(self):
        group = self.kwargs["group_pk"]
        descendants = self.request.query_params.get("descendants", None)
        if descendants == "true":
            return AbakusGroup.objects.get(pk=group).memberships

        return Membership.objects.filter(abakus_group_id=group)

    def create(self, request, *args, **kwargs):
        request.data["abakus_group"] = kwargs["group_pk"]
        return super(MembershipViewSet, self).create(request, *args, **kwargs)
