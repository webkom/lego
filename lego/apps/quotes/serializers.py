from lego.apps.quotes.models import Quote
from lego.apps.tags.serializers import TagSerializerMixin
from lego.utils.serializers import BasisModelSerializer


class QuoteSerializer(TagSerializerMixin, BasisModelSerializer):

    class Meta:
        model = Quote
        fields = ('id', 'created_at', 'title', 'text', 'source', 'approved', 'tags')
