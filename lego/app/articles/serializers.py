from basis.serializers import BasisSerializer

from lego.app.articles.models import Article


class ArticleSerializer(BasisSerializer):
    class Meta:
        model = Article
        fields = ('title', 'author', 'ingress', 'text')
