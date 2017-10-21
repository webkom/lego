from rest_framework import serializers

from .models import AbakusGroup


class AbakusGroupListField(serializers.RelatedField):

    def __init__(self, **kwargs):
        kwargs['many'] = True
        if not kwargs.get('read_only', False):
            kwargs['queryset'] = AbakusGroup.objects.all()
        super().__init__(**kwargs)

    def to_representation(self, iterable):
        return [{'id': group.id, 'name': group.name} for group in iterable.all()]


class AbakusGroupField(serializers.Field):

    def to_representation(self, value):
        return {'id': value.id, 'name': value.name}


class PublicUserField(serializers.PrimaryKeyRelatedField):

    def use_pk_only_optimization(self):
        return False

    def to_representation(self, value):
        from lego.apps.users.serializers.users import PublicUserSerializer
        serializer = PublicUserSerializer(instance=value)
        return serializer.data
