from rest_framework.fields import CharField

from lego.apps.comments.serializers import CommentSerializer
from lego.apps.content.fields import ContentSerializerField
from lego.apps.quotes.models import Quote
from lego.apps.tags.serializers import TagSerializerMixin
from lego.utils.serializers import BasisModelSerializer


class QuoteSerializer(TagSerializerMixin, BasisModelSerializer):

    comments = CommentSerializer(read_only=True, many=True)
    comment_target = CharField(read_only=True)
    text = ContentSerializerField()

    class Meta:
        model = Quote
        fields = ('id', 'created_at', 'text', 'source', 'approved', 'tags',
                  'comments', 'comment_target')


class QuoteCreateAndUpdateSerializer(BasisModelSerializer):

    text = ContentSerializerField()

    class Meta:
        model = Quote
        fields = ('id', 'text', 'source', 'approved', 'tags')
