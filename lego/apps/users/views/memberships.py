from rest_framework import mixins, status, viewsets
from rest_framework.response import Response

from lego.apps.permissions.api.views import AllowedPermissionsMixin
from lego.apps.users.filters import MembershipFilterSet
from lego.apps.users.models import AbakusGroup, Membership
from lego.apps.users.serializers.memberships import MembershipGroupSerializer, MembershipSerializer


class MembershipViewSet(AllowedPermissionsMixin, viewsets.ModelViewSet):
    queryset = Membership.objects.all().select_related('user')
    serializer_class = MembershipSerializer
    filter_class = MembershipFilterSet
    ordering = 'id'


class MembershipSetViewSet(AllowedPermissionsMixin, mixins.CreateModelMixin,
                           viewsets.GenericViewSet):
    """We only use `CreateModelMixin, since we only want POSTs to be allowed.
    If one want to remove a membership or add a single membership, use
    the `/memberships/` endpoint."""
    queryset = Membership.objects.all().select_related('user')
    filter_class = MembershipFilterSet
    ordering = 'id'

    def get_queryset(self):
        queryset = super().get_queryset()
        group_pk = self.kwargs.get('group_pk', None)
        if group_pk:
            return queryset.filter(pk=group_pk)
        return Membership.objects.none()

    def create(self, request, *args, **kwargs):
        serializer = MembershipGroupSerializer(
                data=request.data.get('memberships', None), many=True)
        serializer.is_valid(raise_exception=True)
        group_pk = kwargs.get('group_pk', None)
        group = AbakusGroup.objects.get(pk=group_pk)
        if not group:
            return Response(status=status.HTTP_404_NOT_FOUND)
        # delete all meberships
        group.memberships.delete(force=True)
        # and make new ones
        new_memberships = []
        for membership in serializer.validated_data:
            obj = {
                'user': membership['user'],
                'abakus_group': group,
                'role': membership.get('role', 'member')
            }
            (membership, did_create) = Membership.objects.get_or_create(**obj)
            new_memberships.append(membership)

        membership_data = MembershipSerializer(new_memberships, many=True).data
        return Response(data=membership_data, status=status.HTTP_201_CREATED)
