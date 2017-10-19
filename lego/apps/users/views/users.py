from rest_framework import status, viewsets
from rest_framework.decorators import list_route
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from structlog import get_logger

from lego.apps.jwt.handlers import get_jwt_token
from lego.apps.permissions.api.views import AllowedPermissionsMixin
from lego.apps.permissions.constants import EDIT
from lego.apps.users import constants
from lego.apps.users.models import AbakusGroup, User
from lego.apps.users.registrations import Registrations
from lego.apps.users.serializers.registration import RegistrationConfirmationSerializer
from lego.apps.users.serializers.users import (DetailedUserSerializer, MeSerializer,
                                               PublicUserWithGroupsSerializer)

log = get_logger()


class UsersViewSet(AllowedPermissionsMixin, viewsets.ModelViewSet):

    queryset = User.objects.all()
    lookup_field = 'username'
    serializer_class = PublicUserWithGroupsSerializer
    ordering = 'id'

    def get_queryset(self):
        if self.action in ['list', 'retrieve']:
            return self.queryset.prefetch_related('abakus_groups')
        return self.queryset

    def get_serializer_class(self):
        """
        Users should receive the DetailedUserSerializer if they tries to get themselves or have the
        EDIT permission.
        """
        if self.action in ['retrieve', 'update', 'partial_update']:

            try:
                instance = self.get_object()
            except AssertionError:
                return super().get_serializer_class()

            if self.request.user.has_perm(EDIT, instance) or self.request.user == instance:
                return DetailedUserSerializer

        elif self.action == 'create':
            return RegistrationConfirmationSerializer

        return super().get_serializer_class()

    def get_permissions(self):
        """
        The create action are used to register user, we do not require authentication on that
        endpoint.
        """
        if self.action == 'create':
            return [AllowAny()]

        return super().get_permissions()

    @list_route(
        methods=['GET'], permission_classes=[IsAuthenticated],
        serializer_class=MeSerializer
    )
    def me(self, request):
        """
        Read-only endpoint used to retrieve information about the authenticated user.
        """
        serializer = self.get_serializer(request.user)
        return Response(serializer.data)

    def create(self, request, *args, **kwargs):
        """
        Attempts to register a new user based on the registration token.
        """
        if not request.GET.get('token', False):
            raise ValidationError(detail='Registration token is required.')

        token_email = Registrations.validate_registration_token(request.GET.get('token', False))

        if token_email is None:
            raise ValidationError(detail='Token expired or invalid.')

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = User.objects.create_user(
            email=token_email, **serializer.validated_data
        )

        user_group = AbakusGroup.objects.get(name=constants.USER_GROUP)
        user_group.add_user(user)

        payload = get_jwt_token(user)
        return Response(payload, status=status.HTTP_201_CREATED)
