from django.contrib.contenttypes.models import ContentType
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from lego.apps.reactions.models import Reaction, ReactionType
from lego.apps.users.serializers.users import PublicUserSerializer
from lego.utils.serializers import BasisModelSerializer, GenericRelationField


class ReactionTypeSerializer(BasisModelSerializer):
    class Meta:
        model = ReactionType
        fields = ("short_code", "unicode")


class GroupedReactionSerializer(serializers.Serializer):
    count = serializers.IntegerField()
    type = serializers.CharField()
    # users = PublicUserSerializer(many=True)
    has_reacted = serializers.SerializerMethodField()

    def get_has_reacted(self, obj):
        user = self.context["request"].user
        return obj.get_has_reacted(user)

    # class Meta:
    #    fields = ("count", "type", "has_reacted")

    class Meta:
        fields = ("count", "type", "users")


class ReactionSerializer(BasisModelSerializer):
    created_by = PublicUserSerializer(read_only=True)
    target = GenericRelationField(source="content_object")

    class Meta:
        model = Reaction
        fields = ("id", "type", "created_by", "target")

    def create(self, validated_data):
        answer, created = Reaction.objects.update_or_create(
            question=validated_data.get('question', None),
            defaults={'answer': validated_data.get('answer', None)})
        return answer
