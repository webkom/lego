from django.db import transaction
from rest_framework import serializers
from rest_framework.serializers import ModelSerializer

from lego.apps.tags.models import Tag
from lego.apps.tags.validators import validate_tag


class TagSerializer(ModelSerializer):

    class Meta:
        model = Tag
        fields = ('tag',)

    def to_representation(self, instance):
        return instance.tag

    def to_internal_value(self, data):
        return data

    def get_validators(self):
        validators = super().get_validators()
        validators.append(validate_tag)
        return validators


class TagSerializerMixin(serializers.Serializer):
    """
    Any serializer with write support and tags should implement this serializer to support automatic
    creation of new tags.
    """

    tags = TagSerializer(many=True, required=False, default=[])

    def create(self, validated_data):
        tags = [tag.lower() for tag in validated_data.pop('tags', [])]

        with transaction.atomic():
            instance = super().create(validated_data)

            for tag in tags:
                Tag.objects.get_or_create(pk=tag)
            if tags:
                instance.tags = tags
                instance.save()

        return instance

    def update(self, instance, validated_data):
        tags = validated_data.pop('tags', None)

        with transaction.atomic():
            instance = super().update(instance, validated_data)

            if tags is not None:
                tags = [tag.lower() for tag in tags]
                for tag in tags:
                    Tag.objects.get_or_create(pk=tag)

                instance.tags = tags
                instance.save()

        return instance


class TagSearchSerializer(serializers.ModelSerializer):

    class Meta:
        model = Tag
        fields = ('tag', )
