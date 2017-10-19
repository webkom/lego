from rest_framework.fields import CharField

from lego.apps.articles.models import Article
from lego.apps.comments.serializers import CommentSerializer
from lego.apps.files.fields import ImageField
from lego.apps.reactions.serializers import GroupedReactionSerializer, ReactionSerializer
from lego.apps.tags.serializers import TagSerializerMixin
from lego.utils.serializers import BasisModelSerializer


class DetailedArticleSerializer(TagSerializerMixin, BasisModelSerializer):
    comments = CommentSerializer(read_only=True, many=True)
    reactions = ReactionSerializer(read_only=True, many=True)
    cover = ImageField(required=False, options={'height': 500})
    reactions_grouped = GroupedReactionSerializer(read_only=True, many=True)
    comment_target = CharField(read_only=True)
    content = CharField()

    class Meta:
        model = Article
        fields = (
            'id',
            'title',
            'cover',
            'author',
            'description',
            'comments',
            'comment_target',
            'reactions',
            'reactions_grouped',
            'tags',
            'content'
        )


class SearchArticleSerializer(TagSerializerMixin, BasisModelSerializer):
    cover = ImageField(required=False, options={'height': 500})
    content = CharField()

    class Meta:
        model = Article
        fields = (
            'id',
            'title',
            'cover',
            'author',
            'description',
            'tags',
            'content',
            'pinned',
            'created_at'
        )


class PublicArticleSerializer(TagSerializerMixin, BasisModelSerializer):

    cover = ImageField(required=False, options={'height': 300})

    class Meta:
        model = Article
        fields = ('id', 'title', 'cover', 'description', 'tags')
