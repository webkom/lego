from lego.apps.reactions.exceptions import (
    APIReactionExists,
    APITooManyReactions,
    ReactionExists,
    TooManyReactions,
)
from lego.apps.reactions.models import Reaction
from lego.utils.serializers import BasisModelSerializer, GenericRelationField


class ReactionSerializer(BasisModelSerializer):
    content_target = GenericRelationField(source="content_object")

    class Meta:
        model = Reaction
        fields = ("id", "emoji", "content_target")

    def create(self, validated_data):
        try:
            return super().create(validated_data)
        except ReactionExists as e:
            raise APIReactionExists() from e
        except TooManyReactions as e:
            raise APITooManyReactions() from e
