from rest_framework import serializers

from lego.apps.users.fields import AbakusGroupField, PublicUserField
from lego.apps.users.models import MembershipHistory


class MembershipHistorySerializer(serializers.ModelSerializer):

    abakus_group = AbakusGroupField(read_only=True)
    user = PublicUserField(read_only=True)

    class Meta:
        model = MembershipHistory
        fields = ('id', 'user', 'abakus_group', 'role', 'start_date', 'end_date')
