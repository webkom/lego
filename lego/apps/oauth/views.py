from oauth2_provider.models import AccessToken
from oauth2_provider.views import AuthorizationView
from rest_framework import mixins, permissions, viewsets

from lego.apps.permissions.views import PermissionsMixin

from .models import APIApplication
from .serializers import AccessTokenSerializer, ApplicationSerializer


class LegoAuthorizationView(AuthorizationView):
    """
    Custom AuthorizationView with a custom template.
    """

    template_name = 'oauth2/authorize.html'


class ApplicationViewSet(PermissionsMixin, viewsets.ModelViewSet):
    """
    Manage applications. This viewset requires keyword permissions, but object permissions can be
    implemented when we opens up / if we opens up the API.
    """
    serializer_class = ApplicationSerializer
    queryset = APIApplication.objects.all()
    ordering = 'id'


class AccessTokenViewSet(mixins.ListModelMixin,
                         mixins.DestroyModelMixin,
                         viewsets.GenericViewSet):
    """
    List access tokens. This list is filtered based on the current user.
    """
    serializer_class = AccessTokenSerializer
    permission_classes = [permissions.IsAuthenticated]
    queryset = AccessToken.objects.all()
    ordering = 'id'

    def get_queryset(self):
        return AccessToken.objects.filter(user=self.request.user).select_related('application')
