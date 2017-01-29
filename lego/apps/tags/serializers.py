from rest_framework import serializers
from rest_framework.serializers import ModelSerializer

from lego.apps.tags.models import Tag


class TagSerializer(ModelSerializer):
    class Meta:
        model = Tag
        fields = ('tag',)

    def to_representation(self, instance):
        return instance.tag

    def to_internal_value(self, data):
        return { 'tag': data }


class TagSerializerMixin(serializers.Serializer):
    tags = TagSerializer(many=True, required=False)
    class Meta:
        abstract = True

    def update(self, instance, validated_data):
        tags = [t['tag'] for t in validated_data.pop('tags')]
        instance = super().update(instance, validated_data)
        for tag in tags:
            Tag.objects.get_or_create(pk=tag)
        if tags:
            instance.tags = tags
            instance.save()
        return instance
