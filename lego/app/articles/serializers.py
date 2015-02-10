from lego.halla import BaseSerializer

from lego.app.articles.models import Article


class ArticleSerializer(BaseSerializer):
    class Meta:
        model = Article
        fields = ('title', 'author', 'ingress', 'text')
