from basis.serializers import BasisSerializer

from lego.app.articles.models import Article
from lego.app.comments.serializers import CommentSerializer
from lego.users.serializers import PublicUserSerializer


class DetailedArticleSerializer(BasisSerializer):
    author = PublicUserSerializer(read_only=True)
    comments = CommentSerializer(read_only=True, many=True)

    class Meta:
        model = Article
        fields = ('title', 'author', 'ingress', 'text', 'comments')


class PublicArticleSerializer(BasisSerializer):
    class Meta:
        model = Article
        fields = ('id', 'title', 'ingress')
