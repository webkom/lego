from rest_framework import serializers

from lego.apps.files.fields import FileField, ImageField
from lego.apps.gallery.fields import PictureListField
from lego.apps.users.fields import PublicUserField
from lego.apps.users.models import User
from lego.utils.serializers import BasisModelSerializer

from .models import Gallery, GalleryPicture


class GalleryListSerializer(BasisModelSerializer):

    class Meta:
        model = Gallery
        fields = ('id', 'title', 'location', 'taken_at', 'created_at')


class GallerySerializer(BasisModelSerializer):

    pictures = PictureListField()
    photographers = PublicUserField(many=True, queryset=User.objects.all())

    class Meta:
        model = Gallery
        fields = (
            'id', 'title', 'description', 'location', 'taken_at', 'created_at', 'event',
            'pictures', 'photographers'
        )
        read_only_fields = ('created_at', 'pictures')


class GalleryPictureSerializer(serializers.ModelSerializer):

    file = ImageField(
        required=True,
        options={'height': 700, 'smart': True}
    )
    thumbnail = ImageField(
        source='file',
        required=False,
        options={'height': 200, 'width': 300, 'smart': True}
    )
    raw_file = FileField(source='file', required=False)

    class Meta:
        model = GalleryPicture
        fields = ('id', 'description', 'active', 'file', 'thumbnail', 'raw_file')
        read_only_fields = ('raw_file', )


class GalleryDeletePictureSerializer(serializers.Serializer):
    picture = serializers.PrimaryKeyRelatedField(queryset=GalleryPicture.objects.all())


class GallerySearchSerializer(serializers.ModelSerializer):

    class Meta:
        model = Gallery
        fields = (
            'id',
            'title',
            'location',
            'description',
        )
