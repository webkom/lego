from rest_framework import exceptions, filters, mixins, viewsets

from lego.apps.gallery.filters import GalleryFilterSet
from lego.apps.gallery.permissions import GalleryPicturePermissions, user_filter_pictures
from lego.apps.permissions.filters import AbakusObjectPermissionFilter
from lego.apps.permissions.views import AllowedPermissionsMixin

from .models import Gallery, GalleryPicture
from .serializers import GalleryListSerializer, GalleryPictureSerializer, GallerySerializer


class GalleryViewSet(AllowedPermissionsMixin, viewsets.ModelViewSet):

    queryset = Gallery.objects.all()
    filter_backends = (AbakusObjectPermissionFilter, filters.DjangoFilterBackend,)
    filter_class = GalleryFilterSet
    serializer_class = GallerySerializer

    def get_queryset(self):
        if self.action != 'list':
            return Gallery.objects.all().prefetch_related('photographers')
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
    queryset = GalleryPicture.objects.all()
    permission_classes = (GalleryPicturePermissions, )
    serializer_class = GalleryPictureSerializer

    def get_queryset(self):
        user = self.request.user
        gallery_id = self.kwargs.get('gallery_pk', None)
        if not gallery_id:
            raise exceptions.NotFound

        try:
            gallery = Gallery.objects.get(id=gallery_id)
            return user_filter_pictures(user, gallery)
        except Gallery.DoesNotExist:
            raise exceptions.NotFound
