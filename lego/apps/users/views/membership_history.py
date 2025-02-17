from rest_framework import mixins, permissions, status, viewsets
from rest_framework.response import Response

from lego.apps.permissions.constants import EDIT
from lego.apps.users.constants import GROUP_INTEREST, PUBLIC_GROUPS
from lego.apps.users.filters import MembershipHistoryFilterSet
from lego.apps.users.models import AbakusGroup, Membership, MembershipHistory
from lego.apps.users.serializers.membership_history import MembershipHistorySerializer


class MembershipHistoryViewSet(
    mixins.ListModelMixin, mixins.RetrieveModelMixin, viewsets.GenericViewSet
):
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = MembershipHistorySerializer
    filterset_class = MembershipHistoryFilterSet
    ordering = "id"

    def get_queryset(self):
        if self.request is None:
            return MembershipHistory.objects.none()

        queryset = MembershipHistory.objects.filter(
            abakus_group__deleted=False
        ).select_related("user", "abakus_group")

        if not self.request.user.has_perm(EDIT, Membership):
            return queryset.filter(abakus_group__type__in=PUBLIC_GROUPS)

        return queryset

    def delete(self, request):
        try:
            group = AbakusGroup.objects.get(id=request.data["group_id"])
            user_membership_history = MembershipHistory.objects.filter(
                user__id=request.user.id, abakus_group__id=group.id
            )

            if group.type == GROUP_INTEREST and len(user_membership_history) != 0:
                name = user_membership_history[0].abakus_group.name
                user_membership_history.delete()
                return Response(
                    {"result": f"{name} got deleted"}, status=status.HTTP_200_OK
                )
            return Response(
                {"result": "Nothing to delete"}, status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            return Response(
                {"result": f"Unexpected error: {str(e)}"}, status=status.HTTP_400_BAD_REQUEST
            )
