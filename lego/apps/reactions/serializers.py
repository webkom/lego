from lego.apps.reactions.models import Reaction, ReactionType

from lego.apps.users.serializers import PublicUserSerializer
from lego.utils.serializers import BasisModelSerializer, GenericRelationField

class ReactionTypeSerializer(BasisModelSerializer):
    class Meta:
        model = ReactionType
        fields = ('name', )

class ReactionSerializer(BasisModelSerializer):
    created_by = PublicUserSerializer(read_only=True)
    target = GenericRelationField(source='content_object')

    class Meta:
        model = Reaction
        fields = ('id', 'type', 'created_by', 'target')