from basis.serializers import BasisSerializer

from lego.app.quotes.models import Quote, QuoteLike
from lego.users.models import User
from rest_framework import serializers


class QuoteSerializer(BasisSerializer):
    class Meta:
        model = Quote


class QuoteReadSerializer(BasisSerializer):
    has_liked = serializers.SerializerMethodField('user_has_liked')

    class Meta:
        model = Quote
        fields = ('id', 'title', 'author', 'quote', 'source', 'approved', 'likes', 'has_liked')

    def user_has_liked(self, obj):
        return obj.has_liked(user=self.context['request'].user)

    def create(self, validated_data):
        return Quote.objects.create(**validated_data)

class QuoteCreateAndUpdateSerializer(BasisSerializer):
    class Meta:
        model = Quote
        fields = ('id', 'title', 'author', 'quote', 'source', 'approved', 'likes')

    def create(self, validated_data):
        return Quote.objects.create(**validated_data)


class QuoteLikeSerializer(BasisSerializer):
    class Meta:
        model = QuoteLike
        fields = ('user', 'quote')
