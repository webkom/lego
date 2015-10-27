from basis.serializers import BasisSerializer

from lego.app.articles.models import Article
from lego.users.serializers import PublicUserSerializer


class DetailedArticleSerializer(BasisSerializer):
    author = PublicUserSerializer(read_only=True)

    class Meta:
        model = Article
        fields = ('title', 'author', 'ingress', 'text')


class PublicArticleSerializer(BasisSerializer):
    class Meta:
        model = Article
        fields = ('title', 'ingress')
