# -*- coding: utf8 -*-
from rest_framework import serializers

from lego.users.models import User
from lego.users.permissions import can_retrieve_user


class DetailedUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = (
            'id',
            'username',
            'first_name',
            'last_name',
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
            'last_name'
        )


class UserSerializer(DetailedUserSerializer):
    def to_representation(self, instance):
        view = self.context['view']
        request = self.context['request']

        if view.action == 'retrieve' and can_retrieve_user(instance, request.user):
            serializer = DetailedUserSerializer(instance, context=self.context)
        else:
            serializer = PublicUserSerializer(instance, context=self.context)
        return serializer.data
