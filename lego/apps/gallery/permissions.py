from lego.apps.permissions.constants import CREATE, EDIT, LIST, VIEW
from lego.apps.permissions.permissions import PermissionHandler


class GalleryPicturePermissionHandler(PermissionHandler):
    """
    Custom permission for nested view and filter GalleryPictures based on Gallery edit permission.
    """

    default_keyword_permission = "/sudo/admin/gallerys/{perm}/"
    default_require_auth = True
    force_queryset_filtering = True
    force_object_permission_check = True
    authentication_map = {LIST: False, VIEW: False}

    def has_perm(
        self,
        user,
        perm,
        obj=None,
        queryset=None,
        check_keyword_permissions=True,
        **kwargs
    ):
        # This will force queryset-filtering on LIST
        if perm is LIST:
            return False

        if perm is VIEW:
            if obj is None:
                return False

            if not obj.active:
                return user.has_perm(EDIT, obj=obj.gallery)

        if perm is CREATE:
            from lego.apps.gallery.models import Gallery

            view = kwargs.get("view")
            gallery_id = view.kwargs.get("gallery_pk", None)

            try:
                gallery = Gallery.objects.get(id=gallery_id)
                return user.has_perm(EDIT, obj=gallery)
            except Gallery.DoesNotExist:
                return False
        if obj:
            return user.has_perm(perm, obj=obj.gallery)
        return super().has_perm(
            user, perm, obj, queryset, check_keyword_permissions, **kwargs
        )

    def filter_queryset(self, user, queryset, **kwargs):
        from lego.apps.gallery.models import Gallery, GalleryPicture

        queryset = super().filter_queryset(user, queryset)
        view = kwargs.get("view")
        gallery_id = view.kwargs.get("gallery_pk", None)

        try:
            gallery = Gallery.objects.get(id=gallery_id)

            if user.has_perm(EDIT, gallery):
                return queryset

            if user.has_perm(VIEW, gallery):
                return queryset.filter(active=True)

        except Gallery.DoesNotExist:
            pass

        return GalleryPicture.objects.none()
