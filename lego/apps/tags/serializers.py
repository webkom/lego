from rest_framework.serializers import ModelSerializer

from lego.apps.tags.models import Tag


class TagSerializer(ModelSerializer):
    class Meta:
        model = Tag
        fields = ('tag',)
