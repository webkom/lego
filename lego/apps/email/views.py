from rest_framework import mixins, viewsets

from lego.apps.email.filters import EmailListFilterSet, EmailUserFilterSet
from lego.apps.email.models import EmailList
from lego.apps.email.permissions import UserEmailPermissionHandler
from lego.apps.email.serializers import (EmailListCreateSerializer, EmailListSerializer,
                                         UserEmailCreateSerializer, UserEmailSerializer)
from lego.apps.permissions.api.views import AllowedPermissionsMixin
from lego.apps.users.models import User


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
    filter_class = EmailListFilterSet

    def get_serializer_class(self):
        if self.action == 'create':
            return EmailListCreateSerializer
        return EmailListSerializer


class UserEmailViewSet(AllowedPermissionsMixin,
                       mixins.CreateModelMixin,
                       mixins.ListModelMixin,
                       mixins.RetrieveModelMixin,
                       mixins.UpdateModelMixin,
                       viewsets.GenericViewSet):

    queryset = User.objects.all().exclude(internal_email=None)
    serializer_class = UserEmailSerializer
    ordering = 'id'
    filter_class = EmailUserFilterSet
    permission_handler = UserEmailPermissionHandler()

    def get_serializer_class(self):
        if self.action == 'create':
            return UserEmailCreateSerializer
        return super().get_serializer_class()
