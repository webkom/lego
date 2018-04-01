from django.db.models import Count
from rest_framework import viewsets

from lego.apps.gallery.filters import GalleryFilterSet
from lego.apps.gallery.pagination import GalleryPicturePagination
from lego.apps.permissions.api.views import AllowedPermissionsMixin
from lego.apps.permissions.constants import EDIT, OBJECT_PERMISSION_FIELDS

from .models import Gallery, GalleryPicture
from .serializers import GalleryListSerializer, GalleryPictureSerializer, GallerySerializer


class GalleryViewSet(AllowedPermissionsMixin, viewsets.ModelViewSet):

    queryset = Gallery.objects.all().select_related('event', 'cover')
    filter_class = GalleryFilterSet
    serializer_class = GallerySerializer
    ordering = '-created_at'

    def get_queryset(self):
        if self.action != 'list':
            return super().get_queryset().prefetch_related(
                'photographers', *OBJECT_PERMISSION_FIELDS
            )

        return super().get_queryset().annotate(picture_count=Count('pictures')
                                               ).select_related('cover')

    def get_serializer_class(self):
        if self.action == 'list':
            return GalleryListSerializer
        return super().get_serializer_class()


class GalleryPictureViewSet(viewsets.ModelViewSet):
    """
    Nested viewset used to manage pictures in a gallery.
    """
    queryset = GalleryPicture.objects.all().select_related('file')
    serializer_class = GalleryPictureSerializer
    pagination_class = GalleryPicturePagination

    def get_queryset(self):
        queryset = super().get_queryset()
        gallery_id = self.kwargs.get('gallery_pk', None)
        if gallery_id:
            queryset = queryset.filter(gallery_id=gallery_id)
            if self.request.user.has_perm(EDIT, queryset):
                return queryset
            return queryset.filter(active=True)
        return GalleryPicture.objects.none()
