from rest_framework import serializers

from lego.apps.users.fields import PublicUserField
from lego.apps.users.models import Membership, User


class MembershipSerializer(serializers.ModelSerializer):
    user = PublicUserField(queryset=User.objects.all())

    class Meta:
        model = Membership
        fields = (
            'id',
            'user',
            'abakus_group',
            'role',
            'is_active',
            'start_date',
            'end_date',
        )
