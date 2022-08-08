from rest_framework import mixins, permissions, viewsets

from oauth2_provider.models import AccessToken
from oauth2_provider.views import AuthorizationView

from lego.apps.permissions.api.views import AllowedPermissionsMixin

from .models import APIApplication
from .serializers import AccessTokenSerializer, ApplicationSerializer


class LegoAuthorizationView(AuthorizationView):
    """
    Custom AuthorizationView with a custom template.
    """

    template_name = "oauth2/authorize.html"


class ApplicationViewSet(AllowedPermissionsMixin, viewsets.ModelViewSet):
    """
    list:
    List all applications the current user us responsible for.
    """

    serializer_class = ApplicationSerializer
    ordering = "id"
    queryset = APIApplication.objects.all()


class AccessTokenViewSet(
    mixins.ListModelMixin, mixins.DestroyModelMixin, viewsets.GenericViewSet
):
    """
    list:
    List grants or access-tokens the current user has created.

    destroy:
    Delete an access token created by the user.
    """

    serializer_class = AccessTokenSerializer
    permission_classes = [permissions.IsAuthenticated]
    ordering = "id"

    def get_queryset(self):
        if self.request is None:
            return AccessToken.objects.none()

        return AccessToken.objects.filter(user=self.request.user).select_related(
            "application"
        )
