from django.db.models import Count
from rest_framework import viewsets

from lego.apps.gallery.filters import GalleryFilterSet
from lego.apps.gallery.pagination import GalleryPicturePagination
from lego.apps.permissions.api.views import AllowedPermissionsMixin
from lego.apps.permissions.constants import OBJECT_PERMISSIONS_FIELDS

from .models import Gallery, GalleryPicture
from .serializers import (
    GalleryAdminSerializer, GalleryListSerializer, GalleryPictureSerializer, GallerySerializer
)


class GalleryViewSet(AllowedPermissionsMixin, viewsets.ModelViewSet):

    queryset = Gallery.objects.all().select_related('event', 'cover')
    filter_class = GalleryFilterSet
    serializer_class = GallerySerializer
    ordering = '-created_at'

    def get_queryset(self):
        if self.action != 'list':
            return super().get_queryset().prefetch_related(
                'photographers', *OBJECT_PERMISSIONS_FIELDS
            )

        return super().get_queryset().annotate(picture_count=Count('pictures')
                                               ).select_related('cover')

    def get_serializer_class(self):
        if self.action == 'list':
            return GalleryListSerializer

        if self.action in ['create', 'partial_update', 'update', 'retrieve']:
            if self.request and self.request.user.is_authenticated:
                return GalleryAdminSerializer

        return super().get_serializer_class()


class GalleryPictureViewSet(viewsets.ModelViewSet):
    """
    Nested viewset used to manage pictures in a gallery.
    """
    queryset = GalleryPicture.objects.all().select_related('file').prefetch_related(
        'comments', 'taggees'
    )
    serializer_class = GalleryPictureSerializer
    pagination_class = GalleryPicturePagination

    def get_queryset(self):
        queryset = super().get_queryset()
        gallery_id = self.kwargs.get('gallery_pk', None)
        if gallery_id:
            return queryset.filter(gallery_id=gallery_id)

        return GalleryPicture.objects.none()
