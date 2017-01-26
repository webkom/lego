from rest_framework import serializers

from lego.apps.files.fields import ImageField
from lego.apps.users.fields import AbakusGroupListField
from lego.apps.users.models import Penalty, User
from lego.apps.users.permissions import can_retrieve_user
from lego.apps.users.serializers.penalties import PenaltySerializer


class DetailedUserSerializer(serializers.ModelSerializer):
    penalties = serializers.SerializerMethodField('get_valid_penalties')
    picture = ImageField(required=False, options={'height': 400, 'width': 400})

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
            'picture',
            'is_staff',
            'is_active',
            'penalties'
        )


class PublicUserSerializer(serializers.ModelSerializer):

    picture = ImageField(required=False, options={'height': 400, 'width': 400})

    class Meta:
        model = User
        fields = (
            'id',
            'username',
            'first_name',
            'last_name',
            'full_name',
            'picture'
        )


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

    picture = ImageField(required=False, options={'height': 400, 'width': 400})
    abakus_groups = AbakusGroupListField()

    class Meta:
        model = User
        fields = (
            'id',
            'username',
            'first_name',
            'last_name',
            'full_name',
            'email',
            'picture',
            'is_staff',
            'is_active',
            'abakus_groups',
            'is_abakus_member',
            'is_abakom_member',
        )
