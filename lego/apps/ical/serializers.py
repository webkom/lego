from lego.utils.serializers import BasisModelSerializer

from .models import ICalToken

class ICalTokenSerializer(BasisModelSerializer):
    class Meta:
        model = ICalToken
        fields = ('token', 'created')
