from lego.app.articles.models import Article
from lego.utils.base_serializer import BasisSerializer


class ArticleSerializer(BasisSerializer):
    class Meta:
        model = Article
