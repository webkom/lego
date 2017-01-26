from rest_framework import serializers

from lego.apps.users.models import AbakusGroup
from lego.apps.users.permissions import can_retrieve_abakusgroup

from .users import PublicUserSerializer


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

        if (view.action == 'list' or view.action == 'retrieve'
                and not can_retrieve_abakusgroup(instance, request.user)):

            serializer = PublicAbakusGroupSerializer(instance, context=self.context)
        else:
            serializer = DetailedAbakusGroupSerializer(instance, context=self.context)
        return serializer.data
