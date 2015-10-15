from basis.serializers import BasisSerializer

from lego.app.quotes.models import Quote, QuoteLike


class QuoteSerializer(BasisSerializer):
    class Meta:
        model = Quote


class QuoteReadSerializer(BasisSerializer):
    class Meta:
        model = Quote
        fields = ('id', 'title', 'author', 'quote', 'source', 'approved', 'likes')


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
