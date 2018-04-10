from rest_framework import exceptions, serializers

from lego.apps.files.fields import ImageField
from lego.apps.ical.models import ICalToken
from lego.apps.users.models import AbakusGroup, Penalty, User
from lego.apps.users.serializers.abakus_groups import PublicAbakusGroupSerializer
from lego.apps.users.serializers.penalties import PenaltySerializer


class DetailedUserSerializer(serializers.ModelSerializer):

    abakus_groups = PublicAbakusGroupSerializer(many=True)
    penalties = serializers.SerializerMethodField('get_valid_penalties')
    profile_picture = ImageField(required=False, options={'height': 200, 'width': 200})

    def get_valid_penalties(self, user):
        qs = Penalty.objects.valid().filter(user=user)
        serializer = PenaltySerializer(instance=qs, many=True)
        return serializer.data

    class Meta:
        model = User
        fields = (
            'id', 'username', 'first_name', 'last_name', 'full_name', 'gender', 'email',
            'email_address', 'email_lists_enabled', 'profile_picture', 'allergies', 'is_active',
            'penalties', 'abakus_groups'
        )


class PublicUserSerializer(serializers.ModelSerializer):

    profile_picture = ImageField(required=False, options={'height': 200, 'width': 200})

    class Meta:
        model = User
        fields = (
            'id', 'username', 'first_name', 'last_name', 'full_name', 'gender', 'profile_picture'
        )
        read_only_fields = ('username', )


class PublicUserWithGroupsSerializer(PublicUserSerializer):
    abakus_groups = PublicAbakusGroupSerializer(many=True)

    class Meta(PublicUserSerializer.Meta):
        fields = PublicUserSerializer.Meta.fields + ('abakus_groups', )


class AdministrateUserSerializer(PublicUserSerializer):
    """
    Used by the events app when listing user registrations.
    """

    class Meta(PublicUserSerializer.Meta):
        fields = PublicUserSerializer.Meta.fields + (
            'abakus_groups',
            'allergies',
        )


class SearchUserSerializer(serializers.ModelSerializer):

    profile_picture = ImageField(required=False, options={'height': 200, 'width': 200})

    class Meta:
        model = User
        fields = (
            'id',
            'username',
            'first_name',
            'last_name',
            'full_name',
            'gender',
            'profile_picture',
        )


class SearchGroupSerializer(serializers.ModelSerializer):
    logo = ImageField(required=False, options={'height': 200, 'width': 200})

    class Meta:
        model = AbakusGroup
        fields = ('id', 'name', 'type', 'logo')


class MeSerializer(serializers.ModelSerializer):
    """
    Serializer for the /me, retrieve and update endpoint with EDIT permissions.
    Also used by our JWT handler and returned to the user when a user obtains a JWT token.
    """

    abakus_groups = PublicAbakusGroupSerializer(many=True)
    profile_picture = ImageField(required=False, options={'height': 200, 'width': 200})
    ical_token = serializers.SerializerMethodField('get_user_ical_token')
    penalties = serializers.SerializerMethodField('get_valid_penalties')
    is_student = serializers.SerializerMethodField()
    is_abakus_member = serializers.BooleanField()

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
        username_exists = User.objects \
            .filter(username__iexact=username) \
            .exclude(id=self.instance.id) \
            .exists()

        if username_exists:
            raise exceptions.ValidationError('Username exists')

        return username

    class Meta:
        model = User
        fields = (
            'id', 'username', 'first_name', 'last_name', 'full_name', 'email', 'email_address',
            'email_lists_enabled', 'profile_picture', 'gender', 'allergies', 'is_active',
            'is_student', 'abakus_groups', 'is_abakus_member', 'is_abakom_member', 'penalties',
            'ical_token', 'unanswered_surveys'
        )
