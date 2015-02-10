from rest_framework import serializers

from lego.app.articles.models import Article


class ArticleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Article
        fields = ('title', 'author', 'ingress', 'text')

    def create(self, validated_data):
        request = self.context['request']
        article = Article.objects.create(created_by=request.user, **validated_data)
        return article

    def update(self, instance, validated_data):
        request = self.context['request']
        instance.updated_by = request.user
        return instance
