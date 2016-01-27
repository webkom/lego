from basis.serializers import BasisSerializer
from rest_framework import serializers

from lego.app.events.models import Event, Pool, Registration


class PoolSerializer(BasisSerializer):
    class Meta:
        model = Pool
        fields = ('id', 'name', 'capacity', 'activation_date', 'permission_groups')

    def create(self, validated_data):
        event = Event.objects.get(pk=self.context['view'].kwargs['event_pk'])
        permission_groups = validated_data.pop('permission_groups')
        pool = Pool.objects.create(event=event, **validated_data)

        if permission_groups:
            for group in permission_groups:
                pool.permission_groups.add(group)

        return pool


class EventCreateAndUpdateSerializer(BasisSerializer):
    class Meta:
        model = Event
        fields = ('id', 'title', 'author', 'ingress', 'text', 'event_type', 'location',
                  'start_time', 'end_time', 'merge_time')


class EventReadSerializer(BasisSerializer):
    pools = PoolSerializer(many=True)
    capacity = serializers.ReadOnlyField()

    class Meta:
        model = Event
        fields = ('id', 'title', 'author', 'ingress', 'text', 'event_type', 'location',
                  'start_time', 'end_time', 'pools', 'capacity',
                  'waiting_list')


class RegistrationCreateAndUpdateSerializer(BasisSerializer):
    class Meta:
        model = Registration
        fields = ('id',)

    def create(self, validated_data):
        user = validated_data['current_user']
        event = Event.objects.get(pk=self.context['view'].kwargs['event_pk'])
        return event.register(user)


class SpecificRegistrationCreateAndUpdateSerializer(BasisSerializer):
    class Meta:
        model = Registration
        fields = ('id', 'user')

    def create(self, validated_data):
        user = validated_data['user']
        event = Event.objects.get(pk=self.context['view'].kwargs['event_pk'])
        pool = Pool.objects.get(pk=self.context['view'].kwargs['pool_pk'])
        return event.admin_register(user, pool)
