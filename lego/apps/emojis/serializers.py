from lego.apps.emojis.models import Emoji
from lego.utils.serializers import BasisModelSerializer


class EmojiSerializer(BasisModelSerializer):
    class Meta:
        model = Emoji
        fields = (
            "short_code",
            "keywords",
            "unicode_string",
            "fitzpatrick_scale",
            "category",
        )
