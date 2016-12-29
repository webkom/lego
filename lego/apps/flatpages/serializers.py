from lego.apps.flatpages.models import Page
from lego.utils.serializers import BasisModelSerializer


class PageSerializer(BasisModelSerializer):
    class Meta:
        model = Page
        fields = ('pk', 'title', 'slug', 'content')
