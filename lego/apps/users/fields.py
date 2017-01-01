from rest_framework import serializers

from .models import AbakusGroup


class AbakusGroupListField(serializers.RelatedField):

    queryset = AbakusGroup.objects.all()

    def to_representation(self, iterable):
        return [{'id': group.id, 'name': group.name} for group in iterable.all()]
