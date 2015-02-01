from rest_framework import serializers

from lego.app.articles.models import Article


class ArticleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Article
        fields = ('title', 'author', 'ingress', 'text')
