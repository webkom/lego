from rest_framework.fields import CharField

from lego.apps.articles.models import Article
from lego.apps.comments.serializers import CommentSerializer
from lego.apps.users.serializers import PublicUserSerializer
from lego.utils.serializers import BasisModelSerializer


class DetailedArticleSerializer(BasisModelSerializer):
    author = PublicUserSerializer(read_only=True)
    comments = CommentSerializer(read_only=True, many=True)
    comment_target = CharField(read_only=True)

    class Meta:
        model = Article
        fields = ('title', 'author', 'description', 'text', 'comments', 'comment_target')


class PublicArticleSerializer(BasisModelSerializer):
    class Meta:
        model = Article
        fields = ('id', 'title', 'description')
