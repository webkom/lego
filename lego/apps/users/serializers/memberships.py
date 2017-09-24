from rest_framework import serializers

from lego.apps.users.models import Membership, AbakusGroup


class MembershipSerializer(serializers.ModelSerializer):
    class Meta:
        model = Membership
        fields = (
            'user',
            'role',
            'is_active',
            'start_date',
            'end_date',
        )

    def validate(self, attrs):
        group = AbakusGroup.objects.get(pk=self.context['view'].kwargs['group_pk'])
        return {'abakus_group': group, **attrs}
