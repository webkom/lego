from lego.apps.permissions.constants import EDIT, LIST, VIEW
from lego.apps.permissions.permissions import PermissionHandler


class GalleryPicturePermissionHandler(PermissionHandler):
    """
    Custom permission for nested view and filter GalleryPictures based on Gallery edit permission.
    """

    default_keyword_permission = '/sudo/admin/gallerys/{perm}/'
    default_require_auth = False
    force_queryset_filtering = True

    def has_perm(
        self, user, perm, obj=None, queryset=None, check_keyword_permissions=True, **kwargs
    ):
        if perm is LIST:
            return False
        if obj:
            obj = obj.gallery
        return super().has_perm(user, perm, obj, queryset, check_keyword_permissions, **kwargs)

    def filter_queryset(self, user, queryset, **kwargs):
        from lego.apps.gallery.models import Gallery, GalleryPicture

        queryset = super().filter_queryset(user, queryset)
        view = kwargs.get('view')
        gallery_id = view.kwargs.get('gallery_pk', None)

        try:
            gallery = Gallery.objects.get(id=gallery_id)

            if user.has_perm(EDIT, gallery):
                return queryset

            if user.has_perm(VIEW, gallery):
                return queryset.filter(active=True)

        except Gallery.DoesNotExist:
            pass

        return GalleryPicture.objects.none()
