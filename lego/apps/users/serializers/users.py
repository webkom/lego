from rest_framework import exceptions, serializers

from lego.apps.email.serializers import PublicEmailListSerializer
from lego.apps.files.fields import ImageField
from lego.apps.ical.models import ICalToken
from lego.apps.users import constants
from lego.apps.users.models import AbakusGroup, Penalty, User
from lego.apps.users.serializers.abakus_groups import PublicAbakusGroupSerializer
from lego.apps.users.serializers.memberships import (
    MembershipSerializer,
    PastMembershipSerializer,
)
from lego.apps.users.serializers.penalties import PenaltySerializer
from lego.utils.fields import PrimaryKeyRelatedFieldNoPKOpt


class DetailedUserSerializer(serializers.ModelSerializer):

    abakus_groups = PublicAbakusGroupSerializer(many=True)
    past_memberships = PastMembershipSerializer(many=True)
    penalties = serializers.SerializerMethodField("get_valid_penalties")
    profile_picture = ImageField(required=False, options={"height": 200, "width": 200})
    profile_picture_placeholder = ImageField(
        source="profile_picture",
        required=False,
        options={"height": 20, "width": 20, "filters": ["blur(20)"]},
    )

    def get_valid_penalties(self, user):
        qs = Penalty.objects.valid().filter(user=user)
        serializer = PenaltySerializer(instance=qs, many=True)
        return serializer.data

    class Meta:
        model = User
        fields = (
            "id",
            "username",
            "first_name",
            "last_name",
            "full_name",
            "gender",
            "email",
            "email_address",
            "email_lists_enabled",
            "profile_picture",
            "profile_picture_placeholder",
            "allergies",
            "is_active",
            "penalties",
            "abakus_groups",
            "past_memberships",
            "permissions_per_group",
        )


class PublicUserSerializer(serializers.ModelSerializer):

    profile_picture = ImageField(required=False, options={"height": 200, "width": 200})
    profile_picture_placeholder = ImageField(
        source="profile_picture",
        required=False,
        options={"height": 20, "width": 20, "filters": ["blur(20)"]},
    )

    class Meta:
        model = User
        fields = (
            "id",
            "username",
            "first_name",
            "last_name",
            "full_name",
            "gender",
            "profile_picture",
            "profile_picture_placeholder",
            "internal_email_address",
        )
        read_only_fields = ("username",)


class PublicUserWithAbakusGroupsSerializer(PublicUserSerializer):
    abakus_groups = PublicAbakusGroupSerializer(many=True)

    class Meta(PublicUserSerializer.Meta):
        fields = PublicUserSerializer.Meta.fields + ("abakus_groups",)  # type: ignore


class PublicUserWithGroupsSerializer(PublicUserSerializer):
    abakus_groups = PublicAbakusGroupSerializer(many=True)
    past_memberships = PastMembershipSerializer(many=True)
    memberships = MembershipSerializer(many=True)

    class Meta(PublicUserSerializer.Meta):
        fields = PublicUserSerializer.Meta.fields + (  # type: ignore
            "abakus_groups",
            "past_memberships",
            "memberships",
        )


class AdministrateUserSerializer(PublicUserSerializer):
    """
    Used by the events app when listing user registrations.
    """

    class Meta(PublicUserSerializer.Meta):
        fields = PublicUserSerializer.Meta.fields + (  # type: ignore
            "abakus_groups",
            "allergies",
        )


class AdministrateUserExportSerializer(PublicUserSerializer):
    """
    Used by the events app when listing user registrations, and has permission to export user data.
    """

    class Meta(PublicUserSerializer.Meta):
        fields = AdministrateUserSerializer.Meta.fields + ("email", "phone_number")  # type: ignore


class SearchUserSerializer(serializers.ModelSerializer):

    profile_picture = ImageField(required=False, options={"height": 200, "width": 200})
    profile_picture_placeholder = ImageField(
        source="profile_picture",
        required=False,
        options={"height": 20, "width": 20, "filters": ["blur(20)"]},
    )

    class Meta:
        model = User
        fields = (
            "id",
            "username",
            "first_name",
            "last_name",
            "full_name",
            "gender",
            "profile_picture",
            "profile_picture_placeholder",
        )


class SearchGroupSerializer(serializers.ModelSerializer):
    logo = ImageField(required=False, options={"height": 200, "width": 200})

    class Meta:
        model = AbakusGroup
        fields = ("id", "name", "type", "logo")


class Oauth2UserDataSerializer(serializers.ModelSerializer):
    """
    Basic serailizer
    """

    abakus_groups = PublicAbakusGroupSerializer(many=True)
    memberships = MembershipSerializer(many=True)
    profile_picture = ImageField(required=False, options={"height": 200, "width": 200})
    is_student = serializers.SerializerMethodField()
    is_abakus_member = serializers.BooleanField()

    class Meta:
        model = User
        fields = (
            "id",
            "username",
            "first_name",
            "last_name",
            "full_name",
            "email_address",
            "profile_picture",
            "gender",
            "is_active",
            "is_student",
            "abakus_groups",
            "is_abakus_member",
            "is_abakom_member",
            "memberships",
        )

    def get_is_student(self, user):
        return user.is_verified_student()


class MeSerializer(serializers.ModelSerializer):
    """
    Serializer for the /me, retrieve and update endpoint with EDIT permissions.
    Also used by our JWT handler and returned to the user when a user obtains a JWT token.
    """

    abakus_groups = PublicAbakusGroupSerializer(many=True)
    memberships = MembershipSerializer(many=True)
    profile_picture = ImageField(
        required=False, options={"height": 200, "width": 200}, allow_null=True
    )
    profile_picture_placeholder = ImageField(
        source="profile_picture",
        required=False,
        options={"height": 20, "width": 20, "filters": ["blur(20)"]},
    )
    ical_token = serializers.SerializerMethodField("get_user_ical_token")
    penalties = serializers.SerializerMethodField("get_valid_penalties")
    is_student = serializers.SerializerMethodField()
    is_abakus_member = serializers.BooleanField()
    past_memberships = PastMembershipSerializer(many=True)
    abakus_email_lists = PublicEmailListSerializer(many=True)

    def get_user_ical_token(self, user):
        ical_token = ICalToken.objects.get_or_create(user=user)[0]
        return ical_token.token

    def get_valid_penalties(self, user):
        qs = Penalty.objects.valid().filter(user=user)
        serializer = PenaltySerializer(instance=qs, many=True)
        return serializer.data

    def get_is_student(self, user):
        return user.is_verified_student()

    def validate_username(self, username):
        """
        It is not possible to change username tom something that exists.
        Used to remove case-sensitivity.
        """
        username_exists = (
            User.objects.filter(username__iexact=username)
            .exclude(id=self.instance.id)
            .exists()
        )

        if username_exists:
            raise exceptions.ValidationError("Username exists")

        return username

    class Meta:
        model = User
        fields = (
            "id",
            "username",
            "first_name",
            "last_name",
            "full_name",
            "email",
            "email_address",
            "phone_number",
            "email_lists_enabled",
            "profile_picture",
            "profile_picture_placeholder",
            "gender",
            "allergies",
            "is_active",
            "is_student",
            "abakus_email_lists",
            "abakus_groups",
            "is_abakus_member",
            "is_abakom_member",
            "penalties",
            "ical_token",
            "memberships",
            "past_memberships",
            "internal_email_address",
            "selected_theme",
            "permissions_per_group",
        )


class ChangeGradeSerializer(serializers.Serializer):
    group = PrimaryKeyRelatedFieldNoPKOpt(
        allow_null=True,
        queryset=AbakusGroup.objects.all().filter(type=constants.GROUP_GRADE),
    )
