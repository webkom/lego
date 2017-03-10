from rest_framework import status, viewsets
from rest_framework.decorators import list_route
from rest_framework.exceptions import PermissionDenied, ValidationError
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from lego.apps.permissions.views import AllowedPermissionsMixin
from lego.apps.users.models import User
from lego.apps.users.permissions import UsersPermissions
from lego.apps.users.serializers.registration import RegistrationConfirmationSerializer
from lego.apps.users.serializers.users import DetailedUserSerializer, MeSerializer, UserSerializer


class UsersViewSet(AllowedPermissionsMixin, viewsets.ModelViewSet):
    queryset = User.objects.all()
    lookup_field = 'username'
    serializer_class = UserSerializer
    permission_classes = (IsAuthenticated, UsersPermissions)
    ordering = 'id'

    """
    Override permission classes as @permission_classes on methods do not work with ModelViewSets.
    """
    def get_permissions(self):
        if self.request.method == 'POST':
            # Allow anyone to POST (i.e. visitors that are not registered)
            self.permission_classes = [AllowAny, ]
        else:
            # Rest of the methods require the visitor / user to be authenticated.
            self.permission_classes = [IsAuthenticated, UsersPermissions]

        return super(UsersViewSet, self).get_permissions()

    @list_route(
        methods=['GET'], permission_classes=[IsAuthenticated],
        serializer_class=MeSerializer
    )
    def me(self, request):
        serializer = self.get_serializer(request.user)
        return Response(serializer.data)

    """
    Attempts to register a new user based on the registration token.
    """
    def create(self, request, *args, **kwargs):
        if request.user.is_authenticated():
            # Authenticated users are not allowed to
            # create / register new users unless they are an admin.
            # TODO: add admin user registration.
            raise PermissionDenied()

        if not request.GET.get('token', False):
            # Raise a validation error if the token is not set.
            raise ValidationError(detail='Registration token is required.')

        # Validating the token returns the username of the user that registered.
        token_username = User.validate_registration_token(request.GET.get('token', False))

        if token_username is None:
            # Raise error if the token has expired or is invalid.
            raise ValidationError(detail='Token expired or invalid.')

        # Initialize the registration confirmation serializer.
        serializer = RegistrationConfirmationSerializer(data={**{
            # The username that is saved within the token.
            'username': token_username,
            # Prefix the NTNU student mail with the username.
            'email': '%s@stud.ntnu.no' % token_username,
        }, **request.data})

        # Check if the data is valid.
        serializer.is_valid(raise_exception=True)

        # Initialize the new User object.
        new_user = User.objects.create_user(**serializer.validated_data)

        # TODO: Set roles, etc.

        # Return the user object.
        return Response(DetailedUserSerializer(new_user).data, status=status.HTTP_201_CREATED)
