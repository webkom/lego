from rest_framework import serializers

from .models import AbakusGroup


class AbakusGroupListField(serializers.RelatedField):

    queryset = AbakusGroup.objects.all()

    def to_representation(self, iterable):
        return [{'id': group.id, 'name': group.name} for group in iterable.all()]


class PublicUserField(serializers.PrimaryKeyRelatedField):

    def use_pk_only_optimization(self):
        return False

    def to_representation(self, value):
        from lego.apps.users.serializers.users import PublicUserSerializer
        serializer = PublicUserSerializer(instance=value)
        return serializer.data
