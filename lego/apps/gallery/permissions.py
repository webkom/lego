from lego.apps.permissions.constants import EDIT
from lego.apps.permissions.permissions import PermissionHandler


class GalleryPicturePermissionHandler(PermissionHandler):
    """
    Custom permission for nested view and filter GalleryPictures based on Gallery edit permission.
    """

    default_keyword_permission = '/sudo/admin/gallerys/{perm}/'

    def has_perm(
            self, user, perm, obj=None, queryset=None, check_keyword_permissions=True, **kwargs
    ):
        if obj:
            obj = obj.gallery

        return super().has_perm(user, perm, obj, queryset, check_keyword_permissions)

    def filter_queryset(self, user, queryset, **kwargs):
        from lego.apps.gallery.models import Gallery

        queryset = super().filter_queryset(user, queryset)
        view = kwargs.get('view')
        gallery_id = view.kwargs.get('gallery_pk', None)

        # Edit permission on the gallery is required to see deactivated images.
        if gallery_id and not user.has_perm(EDIT, Gallery.objects.get(id=gallery_id)):
            return queryset.filter(active=True)

        return queryset
