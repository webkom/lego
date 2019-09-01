from django.contrib.contenttypes.models import ContentType
from django.db import IntegrityError
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from lego.apps.reactions.exceptions import (
    APIReactionExists,
    APITooManyReactions,
    ReactionExists,
    TooManyReactions,
)
from lego.apps.reactions.models import Reaction
from lego.apps.users.serializers.users import PublicUserSerializer
from lego.utils.serializers import BasisModelSerializer, GenericRelationField


class GroupedReactionSerializer(serializers.Serializer):
    count = serializers.IntegerField()
    emoji = serializers.CharField()
    has_reacted = serializers.SerializerMethodField()

    def get_has_reacted(self, obj):
        user = self.context["request"].user
        return obj.get_has_reacted(user)

    class Meta:
        fields = ("count", "emoji", "users")


class ReactionSerializer(BasisModelSerializer):
    target = GenericRelationField(source="content_object")

    class Meta:
        model = Reaction
        fields = ("id", "emoji", "target")

    def create(self, validated_data):
        try:
            return super().create(validated_data)
        except ReactionExists:
            raise APIReactionExists()
        except TooManyReactions:
            raise APITooManyReactions()
