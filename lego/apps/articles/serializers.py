from rest_framework.fields import CharField

from lego.apps.articles.models import Article
from lego.apps.comments.serializers import CommentSerializer
from lego.apps.content.fields import ContentSerializerField
from lego.apps.files.fields import ImageField
from lego.apps.reactions.serializers import GroupedReactionSerializer, ReactionSerializer
from lego.apps.tags.serializers import TagSerializerMixin
from lego.apps.users.serializers.users import PublicUserSerializer
from lego.utils.serializers import BasisModelSerializer


class DetailedArticleSerializer(TagSerializerMixin, BasisModelSerializer):
    author = PublicUserSerializer(read_only=True, source='created_by')
    comments = CommentSerializer(read_only=True, many=True)
    reactions = ReactionSerializer(read_only=True, many=True)
    cover = ImageField(required=False, options={'height': 500})
    reactions_grouped = GroupedReactionSerializer(read_only=True, many=True)
    comment_target = CharField(read_only=True)
    content = ContentSerializerField(source='text')

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
            'content',
            'created_at',
            'pinned'
        )


class SearchArticleSerializer(TagSerializerMixin, BasisModelSerializer):
    cover = ImageField(required=False, options={'height': 500})
    content = ContentSerializerField(source='text')

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
        fields = ('id', 'title', 'cover', 'description', 'tags', 'created_at', 'pinned')
