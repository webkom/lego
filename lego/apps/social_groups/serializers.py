from rest_framework import serializers

from lego.apps.social_groups.models import InterestGroup
from lego.apps.social_groups.permissions import can_retrieve_interestgroup
from lego.apps.users.models import AbakusGroup


class DetailedInterestGroupSerializer(serializers.ModelSerializer):

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


class PublicInterestGroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = InterestGroup
        fields = (
            'id',
            'name',
            'number_of_users',
            'description',
            'description_long'
        )


class InterestGroupSerializer(DetailedInterestGroupSerializer):
    def to_representation(self, instance):
        view = self.context['view']
        request = self.context['request']
        abakus_group = AbakusGroup.objects.get(pk=instance.pk)

        if (view.action == 'list' or
                view.action == 'retrieve'
                and not can_retrieve_interestgroup(abakus_group, request.user)):
            serializer = PublicInterestGroupSerializer(instance, context=self.context)
        else:
            serializer = DetailedInterestGroupSerializer(instance, context=self.context)
        return serializer.data
