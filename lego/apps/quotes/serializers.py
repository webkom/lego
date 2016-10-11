from lego.apps.quotes.models import Quote
from lego.utils.serializers import BasisModelSerializer


class QuoteSerializer(BasisModelSerializer):

    class Meta:
        model = Quote
        fields = ('id', 'created_at', 'title', 'text', 'source', 'approved', 'tags')
