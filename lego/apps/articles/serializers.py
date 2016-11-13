from rest_framework.fields import CharField

from lego.apps.articles.models import Article
from lego.apps.comments.serializers import CommentSerializer
from lego.apps.reactions.serializers import GroupedReactionSerializer, ReactionSerializer
from lego.utils.serializers import BasisModelSerializer


class DetailedArticleSerializer(BasisModelSerializer):
    comments = CommentSerializer(read_only=True, many=True)
    reactions = ReactionSerializer(read_only=True, many=True)
    reactions_grouped = GroupedReactionSerializer(read_only=True, many=True)
    comment_target = CharField(read_only=True)

    class Meta:
        model = Article
        fields = ('id', 'title', 'author', 'description', 'text', 'comments', 'comment_target',
                  'reactions', 'reactions_grouped')


class PublicArticleSerializer(BasisModelSerializer):
    class Meta:
        model = Article
        fields = ('id', 'title', 'description')
