from rest_framework import serializers

from lego.apps.social_groups.models import InterestGroup


class InterestGroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = InterestGroup
        fields = (
            'id',
            'name',
            'number_of_users',
            'description',
            'description_long',
            'permissions'
        )
