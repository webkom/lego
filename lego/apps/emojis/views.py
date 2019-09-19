from rest_framework import mixins, viewsets

from lego.apps.emojis.models import Category, Emoji
from lego.apps.emojis.permissions import EmojiPermissionHandler
from lego.apps.emojis.serializers import CategorySerializer, EmojiSerializer
from lego.apps.permissions.api.views import AllowedPermissionsMixin
from lego.apps.permissions.constants import OBJECT_PERMISSIONS_FIELDS


class EmojiViewSet(AllowedPermissionsMixin, viewsets.ModelViewSet):
    pagination_class = None
    queryset = Emoji.objects.all()
    serializer_class = EmojiSerializer

    def get_queryset(self):
        return self.queryset.select_related("category")


class EmojiCategoryViewSet(AllowedPermissionsMixin, viewsets.ModelViewSet):
    pagination_class = None
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
