from rest_framework import serializers
from rest_framework.fields import CharField

from lego.apps.comments.serializers import CommentSerializer
from lego.apps.events.fields import PublicEventField
from lego.apps.events.models import Event
from lego.apps.files.fields import FileField, ImageField
from lego.apps.gallery.fields import GalleryCoverField
from lego.apps.users.fields import PublicUserField
from lego.apps.users.models import User
from lego.utils.serializers import BasisModelSerializer

from .models import Gallery, GalleryPicture


class GalleryCoverSerializer(serializers.ModelSerializer):

    file = ImageField(
        required=False,
        options={'height': 700, 'smart': True}
    )

    thumbnail = ImageField(
        source='file',
        read_only=True,
        options={'height': 300, 'width': 300, 'smart': True}
    )

    class Meta:
        model = GalleryPicture
        fields = ('file', 'thumbnail', 'id')


class GalleryListSerializer(BasisModelSerializer):

    picture_count = serializers.SerializerMethodField()
    cover = GalleryCoverSerializer()

    class Meta:
        model = Gallery
        fields = ('id', 'title', 'cover', 'location', 'taken_at', 'created_at', 'picture_count')

    def get_picture_count(self, gallery):
        return gallery.pictures.count()


class GalleryPictureSerializer(serializers.ModelSerializer):

    file = ImageField(
        required=True,
        options={'height': 700, 'smart': True}
    )
    thumbnail = ImageField(
        source='file',
        read_only=True,
        options={'height': 200, 'width': 300, 'smart': True}
    )
    raw_file = FileField(source='file', read_only=True)
    comments = CommentSerializer(read_only=True, many=True)
    comment_target = CharField(read_only=True)
    taggees = PublicUserField(many=True, queryset=User.objects.all(), required=False)

    class Meta:
        model = GalleryPicture
        fields = ('id', 'gallery', 'description', 'taggees', 'active', 'file', 'thumbnail',
                  'raw_file', 'comments', 'comment_target')
        read_only_fields = ('raw_file', 'thumbnail', 'gallery')

    def validate(self, attrs):
        gallery = Gallery.objects.get(pk=self.context['view'].kwargs['gallery_pk'])
        return {'gallery': gallery, **attrs}


class GallerySerializer(BasisModelSerializer):

    cover = GalleryCoverField(queryset=GalleryPicture.objects.all(), required=False)
    photographers = PublicUserField(many=True, queryset=User.objects.all())
    event = PublicEventField(queryset=Event.objects.all(), required=False)

    class Meta:
        model = Gallery
        fields = (
            'id', 'title', 'description', 'location', 'taken_at', 'created_at', 'event',
            'photographers', 'cover',
        )
        read_only_fields = ('created_at', 'pictures')


class GallerySearchSerializer(serializers.ModelSerializer):

    class Meta:
        model = Gallery
        fields = (
            'id',
            'title',
            'location',
            'description',
        )
