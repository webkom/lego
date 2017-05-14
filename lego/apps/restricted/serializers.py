from lego.apps.restricted.models import RestrictedMail
from lego.utils.serializers import BasisModelSerializer


class RestrictedMailListSerializer(BasisModelSerializer):

    class Meta:
        model = RestrictedMail
        fields = ('id', 'from_address', 'hide_sender', 'used', 'created_at')
        read_only_fields = ('used', 'created_at')

    def save(self, **kwargs):
        kwargs['token'] = RestrictedMail.create_token()
        super().save(**kwargs)


class RestrictedMailDetailSerializer(RestrictedMailListSerializer):

    class Meta(RestrictedMailListSerializer.Meta):
        fields = RestrictedMailListSerializer.Meta.fields + (
            'users', 'groups', 'events', 'meetings', 'raw_addresses'
        )
