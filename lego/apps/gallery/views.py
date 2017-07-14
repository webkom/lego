import copy

from rest_framework import decorators, exceptions, filters, status, viewsets
from rest_framework.response import Response

from lego.apps.gallery.filters import GalleryFilterSet
from lego.apps.permissions.filters import AbakusObjectPermissionFilter
from lego.apps.permissions.views import AllowedPermissionsMixin

from .models import Gallery, GalleryPicture
from .serializers import (GalleryDeletePictureSerializer, GalleryListSerializer,
                          GalleryPictureEditSerializer, GalleryPictureSerializer, GallerySerializer)


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

    @decorators.detail_route(methods=['POST'], serializer_class=GalleryPictureSerializer)
    def add_picture(self, request, *args, **kwargs):
        gallery = self.get_object()

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        GalleryPicture.objects.create(gallery=gallery, **serializer.validated_data)

        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @decorators.detail_route(methods=['POST'], serializer_class=GalleryDeletePictureSerializer)
    def delete_picture(self, request, *args, **kwargs):
        gallery = self.get_object()

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        picture = serializer.validated_data['id']

        if not picture.gallery == gallery:
            raise exceptions.ValidationError('Picture isn\'t connected to this gallery.')

        picture.delete()
        return Response(None, status=status.HTTP_204_NO_CONTENT)

    @decorators.detail_route(methods=['POST'], serializer_class=GalleryPictureEditSerializer)
    def update_picture(self, request, *args, **kwargs):
        gallery = self.get_object()

        serializer = self.get_serializer(data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        data = copy.deepcopy(serializer.validated_data)

        picture = data.pop('id')
        if not picture.gallery == gallery:
            raise exceptions.ValidationError('Picture isn\'t connected to this gallery.')

        serializer = GalleryPictureSerializer(instance=picture, data=data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(serializer.data, status=status.HTTP_200_OK)
