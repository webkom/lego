from rest_framework.viewsets import ModelViewSet

from lego.apps.tags.models import Tag
from lego.apps.tags.serializers import TagSerializer


class TagViewSet(ModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
