from lego.apps.permissions.permissions import AbakusPermission


def user_filter_pictures(user, gallery):
    """
    Only users with update permissions should be able to view deactivated pictures.
    """
    admin_permission = '/sudo/admin/gallerys/update/'

    if user.is_authenticated() and (gallery.can_edit(user) or user.has_perm(admin_permission)):
        images = gallery.pictures.all().select_related('file')
    else:
        images = gallery.pictures.filter(active=True).select_related('file')

    return images


class GalleryPicturePermissions(AbakusPermission):

    default_permission = '/sudo/admin/gallerys/{action}/'

    def has_object_permission(self, request, view, obj):
        gallery = obj.gallery

        return super().has_object_permission(request, view, gallery)
