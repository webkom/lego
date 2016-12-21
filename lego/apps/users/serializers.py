from rest_framework import serializers

from lego.apps.files.fields import FileField
from lego.apps.users.fields import AbakusGroupListField
from lego.apps.users.models import AbakusGroup, Membership, Penalty, User
from lego.apps.users.permissions import can_retrieve_abakusgroup, can_retrieve_user


class PenaltySerializer(serializers.ModelSerializer):
    class Meta:
        model = Penalty
        fields = (
            'id', 'user', 'reason', 'weight', 'source_event'
        )


class DetailedUserSerializer(serializers.ModelSerializer):
    penalties = serializers.SerializerMethodField('get_valid_penalties')
    picture = FileField()

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

    picture = FileField()

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


class MembershipSerializer(serializers.ModelSerializer):
    user = PublicUserSerializer(many=False, read_only=True)

    class Meta:
        model = Membership
        fields = (
            'user',
            'abakus_group_id',
            'role',
            'is_active',
            'start_date',
            'end_date'
        )


class MeSerializer(serializers.ModelSerializer):
    committees = AbakusGroupListField()
    penalties = serializers.SerializerMethodField('get_valid_penalties')
    picture = FileField()

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
            'committees',
            'is_abakus_member',
            'is_abakom_member',
            'penalties'
        )


class DetailedAbakusGroupSerializer(serializers.ModelSerializer):
    users = PublicUserSerializer(many=True, read_only=True)

    class Meta:
        model = AbakusGroup
        fields = (
            'id',
            'name',
            'description',
            'parent',
            'permissions',
            'users'
        )


class PublicAbakusGroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = AbakusGroup
        fields = (
            'id',
            'name',
            'description',
            'parent'
        )


class AbakusGroupSerializer(DetailedAbakusGroupSerializer):
    def to_representation(self, instance):
        view = self.context['view']
        request = self.context['request']

        if (view.action == 'list' or
                view.action == 'retrieve' and not can_retrieve_abakusgroup(instance, request.user)):
            serializer = PublicAbakusGroupSerializer(instance, context=self.context)
        else:
            serializer = DetailedAbakusGroupSerializer(instance, context=self.context)
        return serializer.data
