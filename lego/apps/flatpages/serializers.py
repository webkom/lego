from lego.apps.files.fields import ImageField
from lego.apps.flatpages.models import Page
from lego.utils.serializers import BasisModelSerializer


class PageListSerializer(BasisModelSerializer):

    picture = ImageField(required=False, options={'height': 200, 'width': 200})

    class Meta:
        model = Page
        fields = ('pk', 'title', 'slug',  'picture')


class PageDetailSerializer(BasisModelSerializer):

    picture = ImageField(required=False, options={'height': 500})

    class Meta:
        model = Page
        fields = ('pk', 'title', 'slug', 'content', 'picture')
