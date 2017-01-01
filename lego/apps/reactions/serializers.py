from rest_framework import serializers

from lego.apps.reactions.models import Reaction, ReactionType
from lego.apps.users.serializers.users import PublicUserSerializer
from lego.utils.serializers import BasisModelSerializer, GenericRelationField


class ReactionTypeSerializer(BasisModelSerializer):
    class Meta:
        model = ReactionType
        fields = ('short_code', 'unicode')


class GroupedReactionSerializer(serializers.Serializer):
    count = serializers.IntegerField()
    type = serializers.CharField()
    users = PublicUserSerializer(many=True)

    class Meta:
        fields = ('count', 'type', 'users')


class ReactionSerializer(BasisModelSerializer):
    created_by = PublicUserSerializer(read_only=True)
    target = GenericRelationField(source='content_object')
    # type = ReactionTypeSerializer(read_only=True)

    class Meta:
        model = Reaction
        fields = ('id', 'type', 'created_by', 'target')
