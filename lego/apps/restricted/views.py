from django.http import HttpResponse
from rest_framework import decorators, exceptions, mixins, viewsets

from lego.apps.permissions.api.views import AllowedPermissionsMixin
from lego.apps.restricted.constants import RESTRICTED_TOKEN_PREFIX
from lego.apps.restricted.filters import RestrictedMailFilterSet
from lego.apps.restricted.models import RestrictedMail
from lego.apps.restricted.serializers import (RestrictedMailDetailSerializer,
                                              RestrictedMailListSerializer,
                                              RestrictedMailSerializer)


class RestrictedMailViewSet(AllowedPermissionsMixin,
                            mixins.ListModelMixin, mixins.RetrieveModelMixin,
                            mixins.CreateModelMixin, viewsets.GenericViewSet):

    filter_class = RestrictedMailFilterSet

    def get_queryset(self):
        if self.request.user.is_authenticated:
            queryset = RestrictedMail.objects.filter(created_by=self.request.user)
            if self.action == 'retrieve':
                return queryset.prefetch_related('users', 'groups', 'events', 'meetings')
            return queryset
        return RestrictedMail.objects.none()

    def get_serializer_class(self):
        if self.action == 'list':
            return RestrictedMailListSerializer
        if self.action == 'retrieve':
            return RestrictedMailDetailSerializer
        return RestrictedMailSerializer

    @decorators.detail_route(methods=['GET'])
    def token(self, *arg, **kwargs):
        """
        Download the token belonging to a restricted mail. This token has to be attached to
        the restricted mail for authentication.
        """
        instance = self.get_object()
        if not instance.token:
            raise exceptions.NotFound

        file_content = f'{RESTRICTED_TOKEN_PREFIX}{instance.token}'

        response = HttpResponse(file_content)
        response['Content-Disposition'] = 'attachment; filename="token"'
        return response
