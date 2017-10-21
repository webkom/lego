from rest_framework import serializers

from lego.apps.users.fields import PublicUserField
from lego.apps.users.models import AbakusGroup, Membership, User


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
            'created_at',
        )
        read_only_fields = ('created_at', 'abakus_group', )

    def validate(self, attrs):
        group = AbakusGroup.objects.get(pk=self.context['view'].kwargs['group_pk'])
        return {'abakus_group': group, **attrs}
