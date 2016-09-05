from basis.serializers import BasisSerializer
from rest_framework.fields import CharField

from lego.apps.articles.models import Article
from lego.apps.comments.serializers import CommentSerializer
from lego.apps.users.serializers import PublicUserSerializer


class DetailedArticleSerializer(BasisSerializer):
    author = PublicUserSerializer(read_only=True)
    comments = CommentSerializer(read_only=True, many=True)
    comment_target = CharField(read_only=True)

    class Meta:
        model = Article
        fields = ('title', 'author', 'description', 'text', 'comments', 'comment_target')


class PublicArticleSerializer(BasisSerializer):
    class Meta:
        model = Article
        fields = ('id', 'title', 'description')
