from lego.apps.files.fields import ImageField
from lego.apps.flatpages.models import Page
from lego.utils.serializers import BasisModelSerializer


class PageListSerializer(BasisModelSerializer):

    cover = ImageField(required=False, options={'height': 300})

    class Meta:
        model = Page
        fields = ('pk', 'title', 'slug', 'parent', 'cover')


class PageDetailSerializer(BasisModelSerializer):

    cover = ImageField(required=False, options={'height': 500})

    class Meta:
        model = Page
        fields = ('pk', 'title', 'slug', 'content', 'parent', 'cover')
