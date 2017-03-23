from rest_framework.fields import CharField, IntegerField

from lego.apps.comments.serializers import CommentSerializer
from lego.apps.quotes.models import Quote
from lego.apps.tags.serializers import TagSerializerMixin
from lego.utils.serializers import BasisModelSerializer


class QuoteSerializer(TagSerializerMixin, BasisModelSerializer):

    comment_count = IntegerField(source='comments.count')

    class Meta:
        model = Quote
        fields = ('id', 'created_at', 'text', 'source', 'approved', 'tags',
                  'comment_count')


class QuoteDetailSerializer(TagSerializerMixin, BasisModelSerializer):

    comments = CommentSerializer(read_only=True, many=True)
    comment_target = CharField(read_only=True)

    class Meta:
        model = Quote
        fields = ('id', 'created_at', 'text', 'source', 'approved', 'tags',
                  'comments', 'comment_target')
