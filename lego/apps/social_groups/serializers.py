from rest_framework import serializers

from lego.apps.files.fields import ImageField
from lego.apps.social_groups.models import InterestGroup


class InterestGroupSerializer(serializers.ModelSerializer):

    logo = ImageField(required=False, options={'height': 500, 'width': 500})

    class Meta:
        model = InterestGroup
        fields = (
            'id',
            'name',
            'number_of_users',
            'description',
            'description_long',
            'logo',
            'permissions'
        )
