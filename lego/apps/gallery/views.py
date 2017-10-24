from rest_framework import mixins, viewsets

from lego.apps.gallery.filters import GalleryFilterSet
from lego.apps.permissions.api.views import AllowedPermissionsMixin

from .models import Gallery, GalleryPicture
from .serializers import GalleryListSerializer, GalleryPictureSerializer, GallerySerializer


class GalleryViewSet(AllowedPermissionsMixin, viewsets.ModelViewSet):

    queryset = Gallery.objects.all().select_related('event', 'cover')
    filter_class = GalleryFilterSet
    serializer_class = GallerySerializer
    ordering = '-created_at'

    def get_queryset(self):
        if self.action != 'list':
            return super().get_queryset().prefetch_related('photographers')
        return super().get_queryset()

    def get_serializer_class(self):
        if self.action == 'list':
            return GalleryListSerializer
        return super().get_serializer_class()


class GalleryPictureViewSet(mixins.CreateModelMixin, mixins.RetrieveModelMixin,
                            mixins.UpdateModelMixin, mixins.DestroyModelMixin,
                            viewsets.GenericViewSet):
    """
    Nested viewset used to manage pictures in a gallery.
    """
    queryset = GalleryPicture.objects.all().select_related('file')
    serializer_class = GalleryPictureSerializer

    def get_queryset(self):
        queryset = super().get_queryset()
        gallery_id = self.kwargs.get('gallery_pk', None)
        if gallery_id:
            return queryset.filter(gallery_id=gallery_id)
        return GalleryPicture.objects.none()
