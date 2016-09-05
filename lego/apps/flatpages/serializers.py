from basis.serializers import BasisSerializer

from lego.apps.flatpages.models import Page


class PageSerializer(BasisSerializer):
    class Meta:
        model = Page
        fields = ('pk', 'title', 'slug', 'content', 'toc')
