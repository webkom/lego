from rest_framework import serializers


class GalleryCoverField(serializers.PrimaryKeyRelatedField):

    def use_pk_only_optimization(self):
        return False

    def to_representation(self, value):
        from lego.apps.gallery.serializers import GalleryCoverSerializer
        serializer = GalleryCoverSerializer(instance=value)
        return serializer.data
