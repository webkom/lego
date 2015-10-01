from rest_framework import serializers

from lego.users.models import AbakusGroup, User
from lego.users.permissions import can_retrieve_abakusgroup, can_retrieve_user


class DetailedUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = (
            'id',
            'username',
            'first_name',
            'last_name',
            'full_name',
            'email',
            'is_staff',
            'is_active',
        )


class PublicUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = (
            'id',
            'username',
            'first_name',
            'last_name',
            'full_name'
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


class DetailedAbakusGroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = AbakusGroup
        fields = (
            'id',
            'name',
            'description',
            'parent',
            'permissions'
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

        if view.action == 'retrieve' and can_retrieve_abakusgroup(instance, request.user):
            serializer = DetailedAbakusGroupSerializer(instance, context=self.context)
        else:
            serializer = PublicAbakusGroupSerializer(instance, context=self.context)
        return serializer.data
