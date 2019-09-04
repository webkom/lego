from rest_framework import mixins, viewsets

from lego.apps.emojis.models import Emoji
from lego.apps.emojis.permissions import EmojiPermissionHandler
from lego.apps.emojis.serializers import EmojiSerializer
from lego.apps.permissions.api.views import AllowedPermissionsMixin


class EmojiViewSet(AllowedPermissionsMixin, viewsets.ModelViewSet):
    pagination_class = None
    queryset = Emoji.objects.all()
    serializer_class = EmojiSerializer
