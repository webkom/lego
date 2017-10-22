from lego.apps.events.fields import PublicEventListField
from lego.apps.meetings.fields import MeetingListField
from lego.apps.restricted.models import RestrictedMail
from lego.apps.users.fields import AbakusGroupListField, PublicUserListField
from lego.utils.serializers import BasisModelSerializer


class RestrictedMailListSerializer(BasisModelSerializer):

    class Meta:
        model = RestrictedMail
        fields = ('id', 'from_address', 'hide_sender', 'used', 'created_at')
        read_only_fields = ('used', 'created_at')

    def save(self, **kwargs):
        kwargs['token'] = RestrictedMail.create_token()
        return super().save(**kwargs)


class RestrictedMailSerializer(RestrictedMailListSerializer):

    class Meta(RestrictedMailListSerializer.Meta):
        fields = RestrictedMailListSerializer.Meta.fields + (
            'users', 'groups', 'events', 'meetings', 'raw_addresses'
        )


class RestrictedMailDetailSerializer(RestrictedMailSerializer):
    users = PublicUserListField({'read_only': True})
    groups = AbakusGroupListField({'read_only': True})
    events = PublicEventListField({'read_only': True})
    meetings = MeetingListField({'read_only': True})
