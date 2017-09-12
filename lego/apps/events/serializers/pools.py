from rest_framework import serializers

from lego.apps.events.models import Event, Pool
from lego.apps.events.serializers.registrations import (RegistrationPaymentReadSerializer,
                                                        RegistrationReadDetailedSerializer,
                                                        RegistrationReadSerializer)
from lego.apps.users.serializers.abakus_groups import PublicAbakusGroupSerializer
from lego.utils.serializers import BasisModelSerializer


class PoolReadSerializer(BasisModelSerializer):
    registrations = serializers.SerializerMethodField()
    permission_groups = PublicAbakusGroupSerializer(many=True)

    class Meta:
        model = Pool
        fields = ('id', 'name', 'capacity', 'activation_date',
                  'permission_groups', 'registrations')
        read_only = True

    def create(self, validated_data):
        event = Event.objects.get(pk=self.context['view'].kwargs['event_pk'])
        permission_groups = validated_data.pop('permission_groups')
        pool = Pool.objects.create(event=event, **validated_data)
        pool.permission_groups.set(permission_groups)

        return pool

    def get_registrations(self, obj):
        queryset = obj.registrations.all()
        if obj.event.is_priced:
            return RegistrationPaymentReadSerializer(
                queryset, context=self.context, many=True
            ).data
        return RegistrationReadSerializer(queryset, context=self.context, many=True).data


class PoolAdministrateSerializer(PoolReadSerializer):
    registrations = RegistrationReadDetailedSerializer(many=True)


class PoolCreateAndUpdateSerializer(BasisModelSerializer):

    class Meta:
        model = Pool
        fields = ('id', 'name', 'capacity', 'activation_date', 'permission_groups')
        extra_kwargs = {'id': {'read_only': False, 'required': False}}

    def create(self, validated_data):
        event = Event.objects.get(pk=self.context['view'].kwargs['event_pk'])
        permission_groups = validated_data.pop('permission_groups')
        pool = Pool.objects.create(event=event, **validated_data)
        pool.permission_groups.set(permission_groups)

        return pool
