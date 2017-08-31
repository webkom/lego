from rest_framework import status, viewsets
from rest_framework.decorators import list_route
from rest_framework.exceptions import PermissionDenied, ValidationError
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from structlog import get_logger

from lego.apps.permissions.api.views import AllowedPermissionsMixin
from lego.apps.users import constants
from lego.apps.users.models import AbakusGroup, User
from lego.apps.users.serializers.registration import RegistrationConfirmationSerializer
from lego.apps.users.serializers.users import DetailedUserSerializer, MeSerializer, UserSerializer

log = get_logger()


class UsersViewSet(AllowedPermissionsMixin, viewsets.ModelViewSet):
    queryset = User.objects.all()
    lookup_field = 'username'
    serializer_class = UserSerializer
    ordering = 'id'

    def get_permissions(self):
        """
        Override permission classes as @permission_classes on methods
        do not work with ModelViewSets.
        """
        if self.request.method == 'POST':
            # Allow anyone to POST (i.e. visitors that are not registered)
            self.permission_classes = [AllowAny, ]

        return super(UsersViewSet, self).get_permissions()

    @list_route(
        methods=['GET'], permission_classes=[IsAuthenticated],
        serializer_class=MeSerializer
    )
    def me(self, request):
        serializer = self.get_serializer(request.user)
        return Response(serializer.data)

    def create(self, request, *args, **kwargs):
        """
        Attempts to register a new user based on the registration token.
        """
        if request.user.is_authenticated():
            # Authenticated users are not allowed to
            # create / register new users unless they are an admin.
            # TODO: add admin user registration.
            log.warn('admin_registration_not_implemented')
            raise PermissionDenied()

        if not request.GET.get('token', False):
            raise ValidationError(detail='Registration token is required.')

        token_email = User.validate_registration_token(request.GET.get('token', False))

        if token_email is None:
            raise ValidationError(detail='Token expired or invalid.')

        serializer = RegistrationConfirmationSerializer(data={
            **request.data,
            'email': token_email,
        })

        serializer.is_valid(raise_exception=True)

        new_user = User.objects.create_user(**serializer.validated_data)
        user_group = AbakusGroup.objects.get(name=constants.USER_GROUP)
        user_group.add_user(new_user)

        return Response(DetailedUserSerializer(new_user).data, status=status.HTTP_201_CREATED)
