from rest_framework import mixins, viewsets

from lego.apps.email.models import EmailList
from lego.apps.email.permissions import GroupEmailPermissionHandler, UserEmailPermissionHandler
from lego.apps.email.serializers import (AbakusGroupEmailSerializer, EmailListCreateSerializer,
                                         EmailListSerializer, UserEmailSerializer)
from lego.apps.permissions.api.views import AllowedPermissionsMixin
from lego.apps.users.models import AbakusGroup, User


class EmailListViewSet(AllowedPermissionsMixin,
                       mixins.CreateModelMixin,
                       mixins.RetrieveModelMixin,
                       mixins.UpdateModelMixin,
                       mixins.ListModelMixin,
                       viewsets.GenericViewSet):
    """
    Destroy are disabled. The external_sync don't support group destroy either!
    """
    queryset = EmailList.objects.all().prefetch_related('users', 'groups')
    ordering = 'id'

    def get_serializer_class(self):
        if self.action == 'create':
            return EmailListCreateSerializer
        return EmailListSerializer


class UserEmailViewSet(AllowedPermissionsMixin,
                       mixins.ListModelMixin,
                       mixins.RetrieveModelMixin,
                       mixins.UpdateModelMixin,
                       viewsets.GenericViewSet):

    queryset = User.objects.all()
    serializer_class = UserEmailSerializer
    ordering = 'id'
    permission_handler = UserEmailPermissionHandler()


class AbakusGroupEmailViewSet(AllowedPermissionsMixin,
                              mixins.ListModelMixin,
                              mixins.RetrieveModelMixin,
                              mixins.UpdateModelMixin,
                              viewsets.GenericViewSet):

    queryset = AbakusGroup.objects.all()
    serializer_class = AbakusGroupEmailSerializer
    ordering = 'id'
    permission_handler = GroupEmailPermissionHandler()
