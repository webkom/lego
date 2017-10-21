from rest_framework import mixins, viewsets

from lego.apps.email.filters import EmailListFilterSet, EmailUserFilterSet
from lego.apps.email.models import EmailList
from lego.apps.email.permissions import UserEmailPermissionHandler
from lego.apps.email.serializers import (EmailListCreateSerializer, EmailListDetailSerializer,
                                         EmailListSerializer, UserEmailCreateSerializer,
                                         UserEmailSerializer)
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
    queryset = EmailList.objects.all()
    ordering = 'id'
    filter_class = EmailListFilterSet

    def get_serializer_class(self):
        if self.action == 'create':
            return EmailListCreateSerializer
        if self.action == 'retrieve':
            return EmailListDetailSerializer
        return EmailListSerializer

    def get_queryset(self):
        queryset = super().get_queryset()
        if self.action == 'retrieve':
            return queryset.prefetch_related('users', 'groups')
        return queryset


class UserEmailViewSet(AllowedPermissionsMixin,
                       mixins.CreateModelMixin,
                       mixins.ListModelMixin,
                       mixins.RetrieveModelMixin,
                       mixins.UpdateModelMixin,
                       viewsets.GenericViewSet):

    queryset = User.objects.filter(internal_email__isnull=False)
    serializer_class = UserEmailSerializer
    ordering = 'id'
    filter_class = EmailUserFilterSet
    permission_handler = UserEmailPermissionHandler()

    def get_serializer_class(self):
        if self.action == 'create':
            return UserEmailCreateSerializer
        return super().get_serializer_class()
