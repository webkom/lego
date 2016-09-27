from basis.serializers import BasisSerializer
from lego.apps.likes.models import Like


class LikeSerializer(BasisSerializer):

    class Meta:
            model = Like
            fields = (
                'id',
                'object_id',
                'content_type'
            )