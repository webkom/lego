from basis.serializers import BasisSerializer
from rest_framework import serializers

from lego.app.events.models import Event, Pool


class PoolSerializer(BasisSerializer):

    class Meta:
        model = Pool
        fields = ('name', 'capacity', 'activation_date')


class EventCreateAndUpdateSerializer(BasisSerializer):
    pools = PoolSerializer(many=True)
    capacity = serializers.ReadOnlyField()

    class Meta:
        model = Event
        fields = ('title', 'author', 'ingress', 'text', 'event_type', 'location',
                  'start_time', 'end_time', 'merge_time', 'pools', 'capacity')

    def create(self, validated_data):
        pools_data = validated_data.pop('pools')
        event = Event.objects.create(**validated_data)
        for pool in pools_data:
            Pool.objects.create(event=event, **pool)
        return event


class EventReadSerializer(BasisSerializer):
    class Meta:
        model = Event
        fields = ('title', 'author', 'ingress', 'text', 'event_type', 'location',
                  'start_time', 'end_time', 'pools', 'capacity',
                  'waiting_list')
