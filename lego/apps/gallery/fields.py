from rest_framework import fields

from .permissions import user_filter_pictures


class PictureListField(fields.Field):
    """
    List pictures.
    Only users with can_edit perms on the gallery can see all pictures.
    """

    def __init__(self):
        return super().__init__(read_only=True, source='*')

    def to_representation(self, gallery):
        from .serializers import GalleryPictureSerializer
        user = self.context['request'].user

        images = user_filter_pictures(user, gallery)
        serializer = GalleryPictureSerializer(images, many=True)
        return serializer.data
