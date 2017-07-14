from rest_framework import fields


class PictureListField(fields.Field):
    """
    List pictures.
    Only users with can_edit perms on the gallery can see all pictures.
    """

    def __init__(self):
        self.admin_permission = '/sudo/admin/gallerys/update/'
        return super().__init__(read_only=True, source='*')

    def to_representation(self, gallery):
        from .serializers import GalleryPictureSerializer
        user = self.context['request'].user

        if user.is_authenticated() and \
                (gallery.can_edit(user) or user.has_perm(self.admin_permission)):
            images = gallery.pictures.all().select_related('file')
        else:
            images = gallery.pictures.filter(active=True).select_related('file')

        serializer = GalleryPictureSerializer(images, many=True)
        return serializer.data
