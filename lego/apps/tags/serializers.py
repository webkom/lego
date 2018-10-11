from django.db import transaction
from rest_framework import serializers
from rest_framework.serializers import ModelSerializer

from lego.apps.tags.models import Tag
from lego.apps.tags.validators import validate_tag
from lego.utils.validators import ReservedNameValidator


class TagSerializer(ModelSerializer):
    class Meta:
        model = Tag
        fields = ('tag', )

    def to_representation(self, instance):
        return instance.tag

    def to_internal_value(self, data):
        return {'tag': data}

    def get_validators(self):
        validators = super().get_validators()
        validators.append(lambda t: validate_tag(t['tag']))
        validators.append(lambda t: ReservedNameValidator(reserved_names=['popular'])(t['tag']))
        return validators


class TagListSerializer(serializers.ModelSerializer):

    usages = serializers.IntegerField()

    class Meta:
        model = Tag
        fields = ('tag', 'usages')


class TagDetailSerializer(serializers.ModelSerializer):

    usages = serializers.IntegerField()

    class Meta:
        model = Tag
        fields = ('tag', 'usages', 'related_counts')


class TagSerializerMixin(serializers.Serializer):
    """
    Any serializer with write support and tags should implement this serializer to support automatic
    creation of new tags.
    """

    tags = TagSerializer(many=True, required=False, default=[])

    def create(self, validated_data):
        tags = [tag['tag'].lower() for tag in validated_data.pop('tags', [])]

        with transaction.atomic():
            instance = super().create(validated_data)

            for tag in tags:
                Tag.objects.get_or_create(pk=tag)
            if tags:
                instance.tags.set(tags)
                instance.save()

        return instance

    def update(self, instance, validated_data):
        tags = validated_data.pop('tags', None)

        with transaction.atomic():
            instance = super().update(instance, validated_data)

            if tags is not None:
                tags = [tag['tag'].lower() for tag in tags]
                for tag in tags:
                    Tag.objects.get_or_create(pk=tag)

                instance.tags.set(tags)
                instance.save()

        return instance


class TagSearchSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ('tag', )
