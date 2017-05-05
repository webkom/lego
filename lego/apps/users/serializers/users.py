from rest_framework import serializers

from lego.apps.files.fields import ImageField
from lego.apps.ical.models import ICalToken
from lego.apps.users.fields import AbakusGroupField, AbakusGroupListField
from lego.apps.users.models import Penalty, User, AbakusGroup
from lego.apps.users.permissions import can_retrieve_user
from lego.apps.users.serializers.penalties import PenaltySerializer


class DetailedUserSerializer(serializers.ModelSerializer):

    penalties = serializers.SerializerMethodField('get_valid_penalties')
    profile_picture = ImageField(required=False, options={'height': 200, 'width': 200})

    def get_valid_penalties(self, user):
        qs = Penalty.objects.valid().filter(user=user)
        serializer = PenaltySerializer(instance=qs, many=True)
        return serializer.data

    class Meta:
        model = User
        fields = (
            'id',
            'username',
            'first_name',
            'last_name',
            'full_name',
            'gender',
            'email',
            'profile_picture',
            'allergies',
            'is_staff',
            'is_active',
            'penalties'
        )


class PublicUserSerializer(serializers.ModelSerializer):

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
            'profile_picture'
        )


class AdministrateUserSerializer(PublicUserSerializer):
    grade = AbakusGroupField()

    class Meta(PublicUserSerializer.Meta):
        fields = PublicUserSerializer.Meta.fields + ('grade', 'allergies')


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
    class Meta:
        model = AbakusGroup
        fields = ('id', 'name')


class UserSerializer(DetailedUserSerializer):
    def to_representation(self, instance):
        view = self.context['view']
        request = self.context['request']

        # List and public retrievals use PublicUserSerializer, the rest uses the detailed one:
        if (view.action == 'list' or
                view.action == 'retrieve' and not can_retrieve_user(instance, request.user)):
            serializer = PublicUserSerializer(instance, context=self.context)
        else:
            serializer = DetailedUserSerializer(instance, context=self.context)

        return serializer.data


class MeSerializer(serializers.ModelSerializer):

    abakus_groups = AbakusGroupListField()
    profile_picture = ImageField(required=False, options={'height': 200, 'width': 200})
    ical_token = serializers.SerializerMethodField('get_user_ical_token')
    penalties = serializers.SerializerMethodField('get_valid_penalties')

    def get_user_ical_token(self, user):
        ical_token = ICalToken.objects.get_or_create(user=user)[0]
        return ical_token.token

    def get_valid_penalties(self, user):
        qs = Penalty.objects.valid().filter(user=user)
        serializer = PenaltySerializer(instance=qs, many=True)
        return serializer.data

    class Meta:
        model = User
        fields = (
            'id',
            'username',
            'first_name',
            'last_name',
            'full_name',
            'email',
            'profile_picture',
            'gender',
            'allergies',
            'is_staff',
            'is_active',
            'abakus_groups',
            'is_abakus_member',
            'is_abakom_member',
            'penalties',
            'ical_token'
        )
