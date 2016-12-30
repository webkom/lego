from lego.apps.flatpages.models import Page
from lego.utils.serializers import BasisModelSerializer


class PageListSerializer(BasisModelSerializer):
    class Meta:
        model = Page
        fields = ('pk', 'title', 'slug', 'parent')


class PageDetailSerializer(BasisModelSerializer):
    class Meta:
        model = Page
        fields = ('pk', 'title', 'slug', 'content', 'parent')
