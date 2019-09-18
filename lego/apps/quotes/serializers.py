from rest_framework import serializers
from rest_framework.fields import CharField

from lego.apps.content.fields import ContentSerializerField
from lego.apps.quotes.models import Quote
from lego.apps.tags.serializers import TagSerializerMixin
from lego.utils.serializers import BasisModelSerializer


class QuoteSerializer(TagSerializerMixin, BasisModelSerializer):
    text = ContentSerializerField()
    reactions_grouped = serializers.SerializerMethodField()
    content_target = CharField(read_only=True)

    def get_reactions_grouped(self, obj):
        user = self.context["request"].user
        return obj.get_reactions_grouped(user)

    class Meta:
        model = Quote
        fields = (
            "id",
            "created_at",
            "text",
            "source",
            "approved",
            "tags",
            "reactions_grouped",
            "content_target",
        )


class QuoteCreateAndUpdateSerializer(BasisModelSerializer):

    text = ContentSerializerField()

    class Meta:
        model = Quote
        fields = ("id", "text", "source", "approved", "tags")
