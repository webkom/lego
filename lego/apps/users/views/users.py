from django.db import transaction
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import PermissionDenied, ValidationError
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from structlog import get_logger

from lego.apps.achievements.promotion import check_complete_user_profile
from lego.apps.jwt.handlers import get_jwt_token
from lego.apps.permissions.api.views import AllowedPermissionsMixin
from lego.apps.permissions.constants import CREATE, EDIT
from lego.apps.users import constants
from lego.apps.users.models import AbakusGroup, User
from lego.apps.users.registrations import Registrations
from lego.apps.users.serializers.photo_consents import PhotoConsentSerializer
from lego.apps.users.serializers.registration import RegistrationConfirmationSerializer
from lego.apps.users.serializers.users import (
    ChangeGradeSerializer,
    CurrentUserSerializer,
    Oauth2UserDataSerializer,
    PublicUserSerializer,
    PublicUserWithGroupsSerializer,
)

log = get_logger()


class UsersViewSet(AllowedPermissionsMixin, viewsets.ModelViewSet):
    queryset = User.objects.all()
    lookup_field = "username"
    serializer_class = PublicUserSerializer
    ordering = "id"

    def get_queryset(self):
        if self.action == "retrieve":
            return self.queryset.prefetch_related("abakus_groups")
        return self.queryset

    def get_serializer_class(self):
        """
        Users should receive the CurrentUserSerializer if they try to get themselves or have the
        EDIT permission.
        """
        if self.action in ["retrieve", "update", "partial_update"]:
            try:
                instance = self.get_object()
            except AssertionError:
                return PublicUserWithGroupsSerializer

            if (
                self.request.user.has_perm(EDIT, instance)
                or self.request.user == instance
            ):
                return CurrentUserSerializer

            return PublicUserWithGroupsSerializer

        elif self.action == "create":
            return RegistrationConfirmationSerializer

        return super().get_serializer_class()

    def get_permissions(self):
        """
        The create action are used to register user, we do not require authentication on that
        endpoint.
        """
        if self.action == "create":
            return [AllowAny()]

        return super().get_permissions()

    @action(
        detail=False,
        methods=["GET"],
        # The oauth lib will give permission if it has scope user
        permission_classes=[IsAuthenticated],
        serializer_class=Oauth2UserDataSerializer,
    )
    def oauth2_userdata(self, request):
        """
        Read-only endpoint used to retrieve information about the authenticated user.
        """
        serializer = self.get_serializer(request.user)
        return Response(serializer.data)

    @action(
        detail=False,
        methods=["GET"],
        permission_classes=[IsAuthenticated],
        serializer_class=CurrentUserSerializer,
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
        if not request.GET.get("token", False):
            raise ValidationError(detail="Registration token is required.")

        token_email = Registrations.validate_registration_token(
            request.GET.get("token", False)
        )

        if token_email is None:
            raise ValidationError(detail="Token expired or invalid.")

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = User.objects.create_user(email=token_email, **serializer.validated_data)
        user.set_password(serializer.validated_data["password"])
        user.save()

        user_group = AbakusGroup.objects.get(name=constants.USER_GROUP)
        user_group.add_user(user)

        payload = get_jwt_token(user)
        return Response(payload, status=status.HTTP_201_CREATED)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop("partial", False)
        user = self.get_object()
        serializer = self.get_serializer(user, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        is_abakus_member = serializer.validated_data.pop("is_abakus_member", None)
        with transaction.atomic():
            super().perform_update(serializer)
            if is_abakus_member is None or is_abakus_member == user.is_abakus_member:
                return Response(data=serializer.data, status=status.HTTP_200_OK)
            if not user.is_verified_student():
                raise ValidationError(
                    detail="You have to be a verified student to perform this action"
                )
            abakus_group = AbakusGroup.objects.get(name=constants.MEMBER_GROUP)
            if is_abakus_member:
                abakus_group.add_user(user)
            else:
                abakus_group.remove_user(user)
        payload = serializer.data
        payload["is_abakus_member"] = is_abakus_member
        check_complete_user_profile(request.user)
        return Response(data=payload, status=status.HTTP_200_OK)

    @action(
        detail=True,
        methods=["POST"],
        permission_classes=[IsAuthenticated],
        serializer_class=ChangeGradeSerializer,
    )
    def change_grade(self, request, *args, **kwargs):
        """
        Attempts to change the grade of the user based selected input
        """
        if not request.user.has_perm(CREATE, AbakusGroup):
            return Response(status=status.HTTP_403_FORBIDDEN)

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = self.get_object()
        newGrade = serializer.validated_data["group"]

        with transaction.atomic():
            grade = user.grade
            if grade is not None:
                grade.remove_user(user)
            if newGrade is not None:
                newGrade.add_user(user)

        return Response(CurrentUserSerializer(user).data)

    def destroy(self, request, *args, **kwargs):
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)

    @action(
        detail=True,
        methods=["POST"],
        permission_classes=[IsAuthenticated],
        serializer_class=PhotoConsentSerializer,
    )
    def update_photo_consent(self, request, *args, **kwargs):
        user = self.get_object()

        if not request.user.has_perm(EDIT, user):
            raise PermissionDenied(detail="Cannot update other user's consent")

        serializer = self.get_serializer(data={"user": user, **request.data})

        serializer.is_valid(raise_exception=True)

        serializer.save()

        return Response(CurrentUserSerializer(user).data)
