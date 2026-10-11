from django.db.models import Prefetch, QuerySet
from rest_framework import viewsets

from lego.apps.permissions.api.views import AllowedPermissionsMixin
from lego.apps.permissions.constants import EDIT
from lego.apps.users import constants
from lego.apps.users.filters import AbakusGroupFilterSet
from lego.apps.users.models import AbakusGroup, Membership
from lego.apps.users.permissions import PreventPermissionElevation
from lego.apps.users.serializers.abakus_groups import (
    MEMBERSHIP_ROLE_PRIORITY,
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

        return DetailedAbakusGroupSerializer

    def get_serializer(self, *args, **kwargs):
        if self.action == "retrieve" and args:
            abakus_group = args[0]

            if self.request.user.has_perm(EDIT, abakus_group):
                serializer_class = DetailedAbakusGroupSerializer
            elif abakus_group.type in constants.PUBLIC_GROUPS:
                serializer_class = PublicDetailedAbakusGroupSerializer
            else:
                serializer_class = PublicAbakusGroupSerializer

            kwargs.setdefault("context", self.get_serializer_context())
            return serializer_class(*args, **kwargs)
        return super().get_serializer(*args, **kwargs)

    def get_queryset(self) -> QuerySet[AbakusGroup]:
        if self.action == "retrieve":
            return AbakusGroup.objects_with_text.prefetch_related("users").all()

        queryset = self.queryset
        if self.request.user.is_authenticated:
            queryset = queryset.prefetch_related(
                Prefetch(
                    "membership_set",
                    queryset=Membership.objects.filter(
                        user=self.request.user, is_active=True
                    ).order_by(MEMBERSHIP_ROLE_PRIORITY),
                    to_attr="user_membership",
                )
            )
        return queryset
